"""从 results/*.csv 生成 C1 判据表（Markdown），直接粘进报告。

用法：
    .venv/bin/python scripts/check_claims.py results/grid.csv --learner dt --out report/c1_table.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import analysis as A  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("grid", nargs="+", help="一个或多个 run_grid 输出的 CSV")
    p.add_argument("--learner", default="dt")
    p.add_argument("--out", default=None, help="写入 .md 文件；缺省打印到 stdout")
    p.add_argument("--pairs", default="smote200:rus", help="要检验的采样器配对，如 a:b")
    a = p.parse_args(argv)

    import pandas as pd

    df = pd.concat([A.load_grid(g) for g in a.grid], ignore_index=True)
    df = df.drop_duplicates(subset=["dataset", "learner", "sampler", "repeat", "fold"])

    c1 = A.c1_table(df, a.learner)
    lines = ["### C1：每个数据集上“最佳 SMOTE” vs “最佳降采样”（AUC，5×2 CV）", "",
             c1.to_markdown(index=False), ""]

    for pair in a.pairs.split(","):
        sa, sb = pair.split(":")
        w = A.wilcoxon_by_dataset(df, sa, sb, a.learner)
        if w.empty:
            continue
        lines += [f"### 配对检验：{sa} vs {sb}（单侧 Wilcoxon，H1: {sa} > {sb}）", "",
                  w.round(4).to_markdown(index=False), ""]

    text = "\n".join(lines)
    if a.out:
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        print(f"wrote {out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
