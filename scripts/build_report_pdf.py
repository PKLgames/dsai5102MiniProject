"""md → PDF（pandoc 转 HTML + weasyprint 排版），用 report/report.css 还原 docx 观感。

    .venv/bin/python scripts/build_report_pdf.py report/DSAI5102_07_Report_draft.md

依赖：pypandoc-binary（自带 pandoc）、weasyprint。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pypandoc
from weasyprint import CSS, HTML

PROJECT = Path(__file__).resolve().parents[1]


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
