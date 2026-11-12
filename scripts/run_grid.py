"""P5 主表：2 数据集 × 10 折 × 4 方法 × 5 个 k = 400 行。

口径（SPEC §4 E2，transductive）：每种方法在**全体点**的原始特征上降维一次（不用标签），
然后用 10 折分层 CV 训练/评估 kNN 分类器（只切嵌入坐标，不切降维过程）——与原文 Table 1 一致。

产物：
  results/grid_knn.csv          逐折明细（dataset,fold,method,k,acc）
  results/grid_knn_summary.csv  聚合 mean/std(ddof=1)
  results/paper_vs_ours.csv     原文 vs 我们（列见 results/REPORT_MAP.md）
  results/embeddings/*.npz      coil20 的 umap_ours / tsne 坐标（给 B 出图）

用法：
  NUMBA_NUM_THREADS=1 .venv/bin/python scripts/run_grid.py            # 全量，可中断续跑
  ... --datasets pendigits --methods umap_ours                        # 只补一种
  ... --recompute                                                     # 忽略已有 csv 重算
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

from sklearn.decomposition import PCA  # noqa: E402
from sklearn.manifold import TSNE  # noqa: E402
from sklearn.model_selection import StratifiedKFold  # noqa: E402
from sklearn.neighbors import KNeighborsClassifier  # noqa: E402

import umap  # noqa: E402

from src.data import load  # noqa: E402
from src.paper_ref import PAPER  # noqa: E402
from src.umap_impl import UMAPModel  # noqa: E402

SEED = 42
PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"
EMB = RESULTS / "embeddings"
K_LIST = (10, 20, 40, 80, 160)
N_FOLDS = 10
METHODS = ("pca", "tsne", "umap_ref", "umap_ours")
PAPER_COL = {"pca": "pca", "tsne": "tsne", "umap_ref": "umap", "umap_ours": "umap"}
GRID_FIELDS = ["dataset", "fold", "method", "k", "acc"]


def make_embedding(name: str, method: str, X: np.ndarray) -> np.ndarray:
    if method == "pca":
        E = PCA(n_components=2, random_state=SEED).fit_transform(X)
    elif method == "tsne":
        E = TSNE(n_components=2, perplexity=30, init="pca", learning_rate="auto",
                 max_iter=1000, random_state=SEED).fit_transform(X)
    elif method == "umap_ref":
        E = umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=2, n_epochs=500,
                      init="spectral", random_state=SEED).fit_transform(X)
    elif method == "umap_ours":
        E = UMAPModel(n_neighbors=15, min_dist=0.1, n_components=2, n_epochs=500,
                      init="spectral", random_state=SEED).fit_transform(X)
    else:
        raise ValueError(method)
    return np.asarray(E, dtype=np.float32)


def load_splits(name: str, n: int) -> list[tuple[np.ndarray, np.ndarray]]:
    """优先读 B 的 data/manifests/splits.json；没有就现算（同 seed 同算法，事后核对）。"""
    path = PROJECT / "data" / "manifests" / "splits.json"
    if path.exists():
        import json

        obj = json.loads(path.read_text())
        if name in obj:
            return [(np.asarray(f["train"]), np.asarray(f["test"])) for f in obj[name]["folds"]]
    skf = StratifiedKFold(N_FOLDS, shuffle=True, random_state=SEED)
    return [(tr, te) for tr, te in skf.split(np.zeros(n), np.zeros(n))]


def read_done(grid: Path) -> set[tuple[str, int, str, int]]:
    if not grid.exists():
        return set()
    with grid.open(newline="") as f:
        return {(r["dataset"], int(r["fold"]), r["method"], int(r["k"])) for r in csv.DictReader(f)}


def append_rows(grid: Path, rows: list[dict]) -> None:
    new = not grid.exists()
    with grid.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=GRID_FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)
        f.flush()


def summarise(grid: Path) -> None:
    import collections

    acc: dict[tuple[str, str, int], list[float]] = collections.defaultdict(list)
    with grid.open(newline="") as f:
        for r in csv.DictReader(f):
            acc[(r["dataset"], r["method"], int(r["k"]))].append(float(r["acc"]))
    out = RESULTS / "grid_knn_summary.csv"
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset", "method", "k", "mean", "std", "n"])
        for (ds, m, k), vals in sorted(acc.items()):
            a = np.asarray(vals)
            w.writerow([ds, m, k, f"{a.mean():.6f}", f"{a.std(ddof=1):.6f}", len(a)])
    return acc


def write_paper_vs_ours(acc: dict) -> None:
    out = RESULTS / "paper_vs_ours.csv"
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset", "method", "k", "paper_acc", "paper_std", "our_acc", "our_std",
                    "delta", "n_folds", "verifiable"])
        for (ds, m, k), vals in sorted(acc.items()):
            if m not in PAPER_COL:
                continue
            entry = PAPER.get(ds, {}).get(PAPER_COL[m], {}).get(k)
            if entry is None:
                continue
            a = np.asarray(vals)
            verifiable = not (ds == "coil20" and k >= 80)  # D9：COIL-20 大 k 已预登记未复现
            w.writerow([ds, m, k, f"{entry[0]:.3f}", f"{entry[1]:.3f}",
                        f"{a.mean():.6f}", f"{a.std(ddof=1):.6f}",
                        f"{a.mean() - entry[0]:+.4f}", len(a), str(verifiable).lower()])


def export_embeddings(name: str, method: str, E: np.ndarray, y: np.ndarray) -> None:
    if name != "coil20" or method not in ("umap_ours", "tsne"):
        return
    EMB.mkdir(parents=True, exist_ok=True)
    tag = "umapours" if method == "umap_ours" else "tsne"
    np.savez_compressed(EMB / f"{name}_{tag}.npz", E=E.astype(np.float32), y=y.astype(np.int64))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", nargs="+", default=["pendigits", "coil20"])
    ap.add_argument("--methods", nargs="+", default=list(METHODS))
    ap.add_argument("--recompute", action="store_true")
    args = ap.parse_args()

    RESULTS.mkdir(exist_ok=True)
    grid = RESULTS / "grid_knn.csv"
    done = set() if args.recompute else read_done(grid)
    if args.recompute and grid.exists():
        grid.unlink()

    for name in args.datasets:
        X, y = load(name)
        folds = load_splits(name, len(y))
        for method in args.methods:
            todo_k = [k for k in K_LIST if (name, 0, method, k) not in done and (name, 1, method, k) not in done]
            if not todo_k or all((name, f, method, k) in done for f in range(N_FOLDS) for k in K_LIST):
                print(f"[skip] {name}/{method} 已完成")
                continue
            t = time.time()
            E = make_embedding(name, method, X)
            print(f"[embed] {name}/{method} {time.time()-t:.1f}s  range [{E.min():.2f}, {E.max():.2f}]")
            export_embeddings(name, method, E, y)
            rows = []
            for fold, (tr, te) in enumerate(folds):
                for k in K_LIST:
                    if (name, fold, method, k) in done:
                        continue
                    clf = KNeighborsClassifier(n_neighbors=k, n_jobs=1).fit(E[tr], y[tr])
                    rows.append({"dataset": name, "fold": fold, "method": method,
                                 "k": k, "acc": f"{clf.score(E[te], y[te]):.6f}"})
            append_rows(grid, rows)
            print(f"[grid ] {name}/{method} 追加 {len(rows)} 行")

    acc = summarise(grid)
    write_paper_vs_ours(acc)
    print(f"[done] rows={sum(len(v) for v in acc.values())} -> results/grid_knn.csv, "
          f"grid_knn_summary.csv, paper_vs_ours.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
