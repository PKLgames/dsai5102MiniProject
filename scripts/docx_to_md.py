"""把 report/*.docx 转成保真 Markdown（表格、字号分段、彩色高亮、图片、链接）。

用法：
    .venv/bin/python scripts/docx_to_md.py report/DSAI5102_07_Report_draft.docx

产物：
    report/DSAI5102_07_Report_draft.md      正文（高亮用 <mark class="hl-a|hl-b|hl-c"> 保留）
    report/PLACEHOLDERS.md                  彩色占位符台账（谁填、在哪儿）
    report/media/*.png                      文档内嵌图片（按原文件名导出）
    report/report.css                       与 docx 对齐的排版样式（PDF 用）

高亮语义（Word 原生 highlight 值 → 语义）：
    cyan    → hl-a  A 负责的数据占位符（蓝）
    yellow  → hl-b  B 负责的交付物（黄）
    magenta → hl-c  报告成稿后再填（紫）
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"w": W, "r": R}

HL = {
    "cyan": ("hl-a", "#00FFFF", "A 数据占位符"),
    "yellow": ("hl-b", "#FFFF00", "B 交付物"),
    "magenta": ("hl-c", "#FF00FF", "报告成稿后填写"),
}
SUBTITLES = {
    "Environment and Hardware",
    "Reproduction Commands",
    "Measured Wall-Clock Duration",
    "Originality Check",
}
H1_RE = re.compile(r"^(\d+\.\s+|[A-Z]\.\s+)")
H1_PLAIN = {"Abstract", "References", "Appendix A — Deviation list (D1–D18)",
            "Appendix B — Reproduction guide"}


def q(tag: str) -> str:
    return f"{{{W}}}{tag}"


BR = "\x00br\x00"


def esc(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_")
    return text.replace(BR, "<br>")


def run_text(r: ET.Element) -> str:
    out = []
    for node in r:
        tag = node.tag.split("}")[1]
        if tag == "t":
            out.append(node.text or "")
        elif tag == "tab":
            out.append(" ")
        elif tag == "br":
            out.append(BR)
    return "".join(out)


def run_fmt(r: ET.Element) -> dict:
    rpr = r.find("w:rPr", NS)
    fmt = {"bold": False, "italic": False, "hl": None, "size": None, "font": None}
    if rpr is None:
        return fmt
    b = rpr.find("w:b", NS)
    fmt["bold"] = b is not None and (b.get(q("val")) or "1") not in ("0", "false")
    fmt["italic"] = rpr.find("w:i", NS) is not None
    hl = rpr.find("w:highlight", NS)
    if hl is not None:
        fmt["hl"] = hl.get(q("val"))
    sz = rpr.find("w:sz", NS)
    if sz is not None:
        fmt["size"] = int(sz.get(q("val")))
    fonts = rpr.find("w:rFonts", NS)
    if fonts is not None:
        fmt["font"] = fonts.get(q("ascii"))
    return fmt


def collect_segments(container: ET.Element, collector: list[dict], where: str,
                     suppress_bold: bool = False, suppress_italic: bool = False) -> list[tuple[str, dict]]:
    """把容器里的 run 拆成 (text, fmt) 片段，相邻同格式合并（避免 **a****b** 碎片）。"""
    segs: list[tuple[str, dict]] = []

    def add(text: str, fmt: dict) -> None:
        if not text:
            return
        if segs and segs[-1][1] == fmt:
            segs[-1] = (segs[-1][0] + text, fmt)
        else:
            segs.append((text, fmt))

    for child in container:
        tag = child.tag.split("}")[1]
        if tag == "r":
            text = run_text(child)
            fmt = run_fmt(child)
            if suppress_bold:
                fmt["bold"] = False
            if suppress_italic:
                fmt["italic"] = False
            if fmt["hl"]:
                cls, color, label = HL.get(fmt["hl"], ("hl-x", "#EEEEEE", fmt["hl"]))
                collector.append({"where": where, "kind": cls, "label": label,
                                  "color": color, "text": text.strip()})
                fmt = dict(fmt, hl=cls, color=color)
            add(text, fmt)
        elif tag == "fldSimple":  # SEQ 域：保留缓存结果（Figure/Table 编号）
            for seg in collect_segments(child, collector, where, suppress_bold, suppress_italic):
                add(*seg)
        elif tag == "hyperlink":
            inner = render_segments(collect_segments(child, collector, where, suppress_bold, suppress_italic))
            href = LINKS.get(child.get(f"{{{R}}}id"))
            add(f"[{inner}]({href})" if href else inner, {"bold": False, "italic": False, "hl": None})
        elif tag in ("smartTag", "ins"):
            for seg in collect_segments(child, collector, where, suppress_bold, suppress_italic):
                add(*seg)
    return segs


def render_segments(segs: list[tuple[str, dict]]) -> str:
    out = []
    for text, fmt in segs:
        if fmt.get("hl") and str(fmt["hl"]).startswith("hl-"):
            color = fmt.get("color", "#EEEEEE")
            seg = f'<mark class="{fmt["hl"]}" style="background-color:{color}">{esc(text)}</mark>'
        else:
            seg = esc(text)
        if fmt.get("font") in ("Menlo", "Consolas", "Courier New") and "\n" not in text:
            seg = "`" + text.replace("`", "\\`") + "`"
        if fmt.get("italic"):
            seg = f"*{seg}*"
        if fmt.get("bold"):
            seg = f"**{seg}**"
        out.append(seg)
    return "".join(out)


def render_runs(p: ET.Element, collector: list[dict], where: str,
                suppress_bold: bool = False, suppress_italic: bool = False) -> str:
    return render_segments(collect_segments(p, collector, where, suppress_bold, suppress_italic))


def drawing_target(p: ET.Element) -> str:
    for blip in p.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"):
        rid = blip.get(f"{{{R}}}embed")
        target = IMAGE_RELS.get(rid, "media/image1.png")
        return Path(target).name
    return "image1.png"


def para_props(p: ET.Element) -> dict:
    ppr = p.find("w:pPr", NS)
    props = {"style": None, "jc": None}
    if ppr is not None:
        st = ppr.find("w:pStyle", NS)
        if st is not None:
            props["style"] = st.get(q("val"))
        jc = ppr.find("w:jc", NS)
        if jc is not None:
            props["jc"] = jc.get(q("val"))
    return props


def para_all_bold(p: ET.Element) -> bool:
    seen = 0
    for r in p.iter(q("r")):
        if run_text(r).strip():
            seen += 1
            if not run_fmt(r)["bold"]:
                return False
    return seen > 0


def para_all_italic(p: ET.Element) -> bool:
    seen = 0
    for r in p.iter(q("r")):
        if run_text(r).strip():
            seen += 1
            if not run_fmt(r)["italic"]:
                return False
    return seen > 0


def para_codey(p: ET.Element) -> bool:
    sizes, fonts = set(), set()
    for r in p.iter(q("r")):
        if not run_text(r).strip():
            continue
        fmt = run_fmt(r)
        sizes.add(fmt["size"])
        fonts.add(fmt["font"])
    return sizes == {20} and fonts <= {"Menlo", "Consolas", "Courier New"}


def cell_md(tc: ET.Element, collector: list[dict], where: str) -> str:
    chunks = []
    for p in tc.findall("w:p", NS):
        txt = render_runs(p, collector, where).strip()
        if txt:
            chunks.append(txt)
    return "<br>".join(chunks) if chunks else " "


def table_md(tbl: ET.Element, collector: list[dict], where: str) -> str:
    rows = []
    for tr in tbl.findall("w:tr", NS):
        cells = [cell_md(tc, collector, where) for tc in tr.findall("w:tc", NS)]
        rows.append(cells)
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [" "] * (width - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |",
           "|" + "|".join([" --- "] * width) + "|"]
    for r in rows[1:]:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


def convert(src: Path, out: Path) -> int:
    global LINKS
    z = zipfile.ZipFile(src)
    doc = ET.fromstring(z.read("word/document.xml"))
    LINKS = {}
    try:
        rels = ET.fromstring(z.read("word/_rels/document.xml.rels"))
        for rel in rels:
            if rel.get("Type", "").endswith("/hyperlink"):
                LINKS[rel.get("Id")] = rel.get("Target")
    except KeyError:
        pass

    # 导出图片
    media_dir = out.parent / "media"
    for name in z.namelist():
        if name.startswith("word/media/"):
            media_dir.mkdir(parents=True, exist_ok=True)
            (media_dir / Path(name).name).write_bytes(z.read(name))

    IMAGE_RELS.clear()
    try:
        rels = ET.fromstring(z.read("word/_rels/document.xml.rels"))
        for rel in rels:
            if rel.get("Type", "").endswith("/image"):
                IMAGE_RELS[rel.get("Id")] = rel.get("Target")
    except KeyError:
        pass

    body = doc.find("w:body", NS)
    blocks: list[str] = []
    collector: list[dict] = []
    idx = 0
    code_buf: list[str] = []

    def flush_code() -> None:
        if not code_buf:
            return
        while code_buf and not code_buf[-1].strip():
            code_buf.pop()
        lang = "bash"
        # docx 里代码块首行常是一个单独的语言标签（"bash"），用作围栏语言后删除
        if len(code_buf) > 1 and code_buf[0].strip().lower() in ("bash", "sh", "shell", "console"):
            lang = "bash"
            code_buf.pop(0)
        while blocks and not blocks[-1].strip():
            blocks.pop()
        blocks.append(f"```{lang}\n" + "\n".join(code_buf) + "\n```")
        code_buf.clear()

    for el in body:
        tag = el.tag.split("}")[1]
        if tag != "p":
            if tag == "tbl":
                flush_code()
                idx += 1
                blocks.append(table_md(el, collector, f"表 {idx}"))
                blocks.append("")
            continue
        has_drawing = el.find(".//w:drawing", NS) is not None
        text = " ".join("".join(run_text(r) for r in el.iter(q("r"))).split())

        if has_drawing:
            img = drawing_target(el)
            flush_code()
            idx += 1
            blocks.append(f'<p class="center"><img src="media/{img}" alt="figure" '
                          'style="width:100%; max-width:16cm"/></p>')
            blocks.append("")
            continue
        if not text:
            if code_buf:
                code_buf.append("")
            continue
        if para_codey(el):
            code_buf.append("".join(run_text(r) for r in el.iter(q("r"))))
            continue
        flush_code()
        idx += 1
        props = para_props(el)
        where = f"段 {idx}"
        if props["style"] == "Caption":
            html = render_runs(el, collector, where)
            blocks.append(f'<p class="caption">{html}</p>')
            blocks.append("")
        elif props["jc"] == "center":
            cls = "subtitle" if para_all_bold(el) else "title"
            blocks.append(f'<p class="{cls}">{render_runs(el, collector, where, suppress_bold=True)}</p>')
            blocks.append("")
        elif para_all_bold(el) and (H1_RE.match(text) or text in H1_PLAIN):
            blocks.append(f'## {render_runs(el, collector, where, suppress_bold=True)}')
            blocks.append("")
        elif para_all_bold(el) and text in SUBTITLES:
            blocks.append(f"### {render_runs(el, collector, where, suppress_bold=True)}")
            blocks.append("")
        else:
            body_md = render_runs(el, collector, where, suppress_italic=para_all_italic(el))
            if para_all_italic(el):
                body_md = f"*{body_md}*"
            blocks.append(body_md)
            blocks.append("")
    flush_code()

    cleaned: list[str] = []
    for b in blocks:
        if b in ("", "\n"):
            cleaned.append(b)
            continue
        b = re.sub(r"(?:<br>\s*)+", "<br>", b).strip()
        b = re.sub(r"^<br>", "", b)
        b = re.sub(r"<br>$", "", b)
        b = b.replace("**<br>**", "<br>")
        if b:
            cleaned.append(b)
    blocks = []
    for i, b in enumerate(cleaned):
        nxt = cleaned[i + 1] if i + 1 < len(cleaned) else ""
        if b.strip().strip("`").lower() in ("bash", "sh", "shell", "console") \
                and nxt.lstrip().startswith("```"):
            continue  # 代码块前的语言标签，交给围栏处理
        blocks.append(b)
    out.write_text("\n".join(blocks).rstrip() + "\n", encoding="utf-8")

    # 占位符台账
    lines = ["# 报告占位符台账（自动生成，勿手改）", "",
             f"来源：`{src.name}`；生成命令：`.venv/bin/python scripts/docx_to_md.py {src}`", "",
             "| # | 颜色 | 语义 | 位置 | 占位文本 | 谁填 |",
             "|---|---|---|---|---|---|"]
    for i, item in enumerate(collector, 1):
        who = {"hl-a": "A", "hl-b": "B", "hl-c": "C（成稿后）"}.get(item["kind"], "?")
        lines.append(f"| {i} | `{item['kind']}` | {item['label']} | {item['where']} | "
                     f"`{item['text']}` | {who} |")
    lines += ["", f"合计 {len(collector)} 处。", ""]
    (out.parent / "PLACEHOLDERS.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[done] {out}  {len(blocks)} 块")
    print(f"[done] {out.parent / 'PLACEHOLDERS.md'}  {len(collector)} 处高亮")
    from collections import Counter
    print("      ", dict(Counter(c["label"] for c in collector)))
    return 0


LINKS: dict[str, str] = {}
IMAGE_RELS: dict[str, str] = {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("docx", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    out = args.out or args.docx.with_suffix(".md")
    return convert(args.docx, out)


if __name__ == "__main__":
    sys.exit(main())
