#!/usr/bin/env python
"""8-gram 重合率自查：报告草稿 vs 原文全文。

用法：
    .venv/bin/python scripts/similarity_check.py                # 默认扫 report/ 下 *.md/*.tex
    .venv/bin/python scripts/similarity_check.py report/main.md  # 指定文件

判定：整体 8-gram 重合率 < 5% 视为达标（`docs/TASKS_C.md` 的硬性要求）。
原理很笨但够用：原文按空白切词、小写、去标点，取连续 8 词为一个 n-gram；
我们的文本同样处理，统计每个 8-gram 是否在原文的集合里出现过。
输出里会列出最长的"连续命中"片段，方便直接改句子（改结构而不是换同义词）。
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

N = 8
ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "umap_arxiv2018.txt"
REPORT_DIR = ROOT / "report"

WORD_RE = re.compile(r"[a-z0-9]+")


def normalize(text: str) -> list[str]:
    return WORD_RE.findall(text.lower())


def ngrams(words: list[str], n: int = N) -> list[tuple[str, ...]]:
    if len(words) < n:
        return []
    return [tuple(words[i : i + n]) for i in range(len(words) - n + 1)]


def main(argv: list[str]) -> int:
    if not PAPER.exists():
        print(f"[ERR] 找不到原文：{PAPER}", file=sys.stderr)
        return 2

    paper_words = normalize(PAPER.read_text(encoding="utf-8", errors="ignore"))
    paper_set = set(ngrams(paper_words))
    print(f"原文：{PAPER.name}  词数={len(paper_words)}  8-gram 种类={len(paper_set)}")

    targets = [Path(a) for a in argv[1:]] or sorted(
        [*REPORT_DIR.glob("*.md"), *REPORT_DIR.glob("*.tex")]
    )
    if not targets:
        print(f"[WARN] {REPORT_DIR} 下没有 .md/.tex，先用 --help 里的方式指定文件")
        return 1

    failed = False
    for path in targets:
        if not path.exists():
            print(f"[SKIP] {path} 不存在")
            continue
        words = normalize(path.read_text(encoding="utf-8", errors="ignore"))
        grams = ngrams(words)
        if not grams:
            print(f"[SKIP] {path} 太短（< {N} 词）")
            continue
        hit = [g for g in grams if g in paper_set]
        ratio = len(hit) / len(grams)
        flag = "PASS" if ratio < 0.05 else "FAIL"
        failed |= ratio >= 0.05
        print(f"[{flag}] {path}  8-gram={len(grams)}  命中={len(hit)}  重合率={ratio:.2%}")

        # 最长连续命中片段（连续 3 个以上命中的 n-gram 视为一段）
        runs: list[list[tuple[str, ...]]] = []
        cur: list[tuple[str, ...]] = []
        for g in grams:
            if g in paper_set:
                cur.append(g)
            elif cur:
                runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)
        for run in sorted(runs, key=len, reverse=True)[:3]:
            if len(run) >= 3:
                span = " ".join(run[0]) + " … " + " ".join(run[-1][-3:])
                print(f"    连续命中 {len(run)} 个 8-gram：{span[:160]}")

        # 用词重合（辅助判断，不是判据）
        ours = Counter(words)
        paper_counter = Counter(paper_words)
        overlap = sum(1 for w in ours if w in paper_counter) / max(len(ours), 1)
        print(f"    词表覆盖（辅助）：我们的词有 {overlap:.0%} 在原文出现过")

    print("\n结论：" + ("达标（全部 <5%）" if not failed else "未达标，需要改写命中片段"))
    return 0 if not failed else 3


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
