"""P5 运行时间表：每个（数据集, 方法）只计 fit 秒数，重复 3 次取中位数（SPEC §4 E4）。

产物 results/runtime.csv：dataset,method,median_s,min_s,max_s,timeout
口径提醒：本机 16 vCPU 但 joblib 串行（[Errno 13]），t-SNE 是 sklearn 单线程实现，
原文 t-SNE 用的 MulticoreTSNE → 我们的 t-SNE 偏慢、UMAP 相对占优（D3，报告必须标注方向）。
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

from scripts.run_grid import METHODS, make_embedding  # noqa: E402
from src.data import load  # noqa: E402

PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"
REPEATS = 3
TIMEOUT_S = 1800


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", nargs="+", default=["pendigits", "coil20"])
    ap.add_argument("--methods", nargs="+", default=list(METHODS))
    ap.add_argument("--repeats", type=int, default=REPEATS)
    args = ap.parse_args()
    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / "runtime.csv"
    rows = []
    for name in args.datasets:
        X, _ = load(name)
        for method in args.methods:
            make_embedding(name, method, X[:200])  # 预热：numba JIT / BLAS 线程池，不计时（E4 只计 fit）
            ts = []
            timeout = False
            for _ in range(args.repeats):
                t0 = time.time()
                make_embedding(name, method, X)
                dt = time.time() - t0
                ts.append(dt)
                if dt > TIMEOUT_S:
                    timeout = True
                    break
            ts.sort()
            med = float(np.median(ts))
            rows.append([name, method, f"{med:.2f}", f"{min(ts):.2f}", f"{max(ts):.2f}",
                         str(timeout).lower()])
            print(f"[runtime] {name:9s} {method:9s} median {med:6.2f}s  min {min(ts):6.2f}  max {max(ts):6.2f}")
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset", "method", "median_s", "min_s", "max_s", "timeout"])
        w.writerows(rows)
    print(f"[done] {out.relative_to(PROJECT)} ({len(rows)} 行)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
