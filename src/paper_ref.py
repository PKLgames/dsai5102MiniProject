"""原文数字的唯一来源：解析 docs/goal/PAPER_DATA.md 的 Table 1（本轮只用 COIL-20 与 PenDigits）。

为什么解析而不是硬编码：数字只在 PAPER_DATA.md 里维护一份，避免两处不一致（B/C 都读同一文件）。
表格列序：k | t-SNE | UMAP | LargeVis | Eigenmaps | PCA。
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
PAPER_DATA = PROJECT / "docs" / "goal" / "PAPER_DATA.md"

_COLS = {"tsne": 0, "umap": 1, "largevis": 2, "eigenmaps": 3, "pca": 4}
_SECTION = {"COIL-20": "coil20", "PenDigits": "pendigits"}
_ROW = re.compile(r"^\|\s*(\d+)\s*\|(.+)\|\s*$")
_NUM = re.compile(r"(\d+\.\d+)\s*\(±(\d+\.\d+)\)")


def load_paper_table(path: Path = PAPER_DATA) -> dict[str, dict[str, dict[int, tuple[float, float]]]]:
    """返回 {dataset: {column: {k: (mean, std)}}}，只含 Table 1 的两个数据集。"""
    out: dict[str, dict[str, dict[int, tuple[float, float]]]] = {}
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## Table"):
            current = None
            for key, name in _SECTION.items():
                if key in line:
                    current = name
                    out[current] = {c: {} for c in _COLS}
            continue
        if current is None:
            continue
        m = _ROW.match(line)
        if not m:
            continue
        k = int(m.group(1))
        cells = [c.strip() for c in m.group(2).split("|")]
        if len(cells) < 5:
            continue  # 表头/分隔行
        for col, idx in _COLS.items():
            vals = _NUM.findall(cells[idx].replace("*", ""))
            if not vals:
                continue  # 没有 std 的格子（本轮两个数据集不存在）
            mean, std = vals[0]
            out[current][col][k] = (float(mean), float(std))
    return out


PAPER = load_paper_table()
