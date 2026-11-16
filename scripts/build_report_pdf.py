"""md → PDF（pandoc 转 HTML + weasyprint 排版），版式由 report/report.css 决定。

    .venv/bin/python scripts/build_report_pdf.py report/DSAI5102_Group16_Report.md

在 pandoc 产出的 HTML 上做四类**纯排版**后处理（不改任何文字/数字）：
  1. 摘要包一层 <div class="abstract">；
  2. 参考文献包一层 <div class="refs">（悬挂缩进）；
  3. 图片段落加 class="figure"（居中、与图注同页）；
  4. 图注/表注里的编号加粗（如 <b>Table 3</b> …）。

依赖：pypandoc-binary（自带 pandoc）、weasyprint。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pypandoc
from weasyprint import CSS, HTML

PROJECT = Path(__file__).resolve().parents[1]


def wrap_section(html: str, heading_regex: str, cls: str) -> str:
    """把 heading 到下一个 <h2 之间的内容包进 <div class="cls">。"""
    m = re.search(heading_regex, html)
    if not m:
        return html
    start = m.start()
    nxt = re.search(r"<h2[\s>]", html[m.end():])
    end = m.end() + nxt.start() if nxt else len(html)
    inner = html[start:end]
    return html[:start] + f'<div class="{cls}">' + inner + "</div>" + html[end:]


def postprocess(body: str) -> str:
    # 1) 摘要
    body = wrap_section(body, r'<h2 id="abstract"[^>]*>', "abstract")
    # 2) 参考文献
    body = wrap_section(body, r'<h2 id="references"[^>]*>', "refs")
    # 3) 纯图片段落
    body = re.sub(r"<p>(\s*<img\b)", r'<p class="figure">\1', body)
    # 4) 图注/表注编号加粗
    body = re.sub(
        r'(<p class="caption">)(Table|Figure)\s+([0-9]+[a-z]?)',
        r"\1<b>\2 \3</b>",
        body,
    )
    return body


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("md", type=Path)
    ap.add_argument("--css", type=Path, default=PROJECT / "report/report.css")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    md = args.md
    out = args.out or md.with_suffix(".pdf")

    body = pypandoc.convert_file(
        str(md), "html5", format="markdown+raw_html+pipe_tables+tex_math_dollars",
        extra_args=["--wrap=none"],
    )
    body = postprocess(body)
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{md.stem}</title></head><body>{body}</body></html>"""
    doc = HTML(string=html, base_url=str(md.parent)).render(
        stylesheets=[CSS(filename=str(args.css))]
    )
    doc.write_pdf(str(out))
    print(f"[done] {out}  {len(doc.pages)} 页")
    return 0


if __name__ == "__main__":
    sys.exit(main())
