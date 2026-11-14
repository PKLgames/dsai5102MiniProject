"""P5 主表：2 数据集 × 10 折 × 4 方法 × 5 个 k = 400 行。

口径（SPEC §4 E2，transductive）：每种方法在**全体点**的原始特征上降维一次（不用标签），
然后用 10 折分层 CV 训练/评估 kNN 分类器（只切嵌入坐标，不切降维过程）——与原文 Table 1 一致。

产物：
  results/grid_knn.csv          逐折明细（dataset,fold,method,k,acc）
  results/grid_knn_summary.csv  聚合 mean/std(ddof=1)
  results/paper_vs_ours.csv     原文 vs 我们（列见 results/REPORT_MAP.md）
  results/embeddings/*.npz      coil20 的 umap_ours / tsne 坐标（给 B 出图）

用法：
  NUMBA_NUM_THREADS=1 .venv/bin/python scripts/run_grid.py            # 全量；仅可跳过同协议下完整完成的方法
  ... --datasets pendigits --methods umap_ours                        # 只补一种（不与旧协议结果混用）
  ... --recompute                                                     # 忽略已有 csv 重算
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
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
    """Read B's validated nested schema; fail closed, never invent a fallback."""
    import json
    from src.data import array_sha256
    path = PROJECT / "data" / "manifests" / "splits.json"
    obj = json.loads(path.read_text())
    d = obj["datasets"][name]
    X, y = load(name)
    if d["n"] != n or d["n_folds"] != N_FOLDS:
        raise ValueError("Split dimensions disagree")
    if d["array_sha256"] != array_sha256(X, y):
        raise ValueError("Split row ordering/data hash mismatch")
    folds = [(np.asarray(f["train"], dtype=int), np.asarray(f["test"], dtype=int)) for f in d["folds"]]
    expected = list(StratifiedKFold(N_FOLDS, shuffle=True, random_state=SEED).split(X, y))
    seen = np.zeros(n, dtype=int)
    if len(folds) != N_FOLDS: raise ValueError("Wrong fold count")
    for i, (tr, te) in enumerate(folds):
        if (tr.ndim != 1 or te.ndim != 1 or
            len(np.unique(tr)) != len(tr) or len(np.unique(te)) != len(te) or
            np.any(tr < 0) or np.any(te < 0) or np.any(tr >= n) or np.any(te >= n) or
            np.intersect1d(tr, te).size or len(np.union1d(tr, te)) != n):
            raise ValueError("Invalid split")
        if not (np.array_equal(tr, expected[i][0]) and np.array_equal(te, expected[i][1])):
            raise ValueError("Split differs from agreed true-label stratified partitions")
        seen[te] += 1
    if not np.all(seen == 1): raise ValueError("Test coverage is not exactly once")
    return folds


def read_done(grid: Path) -> set[tuple[str, int, str, int]]:
    if not grid.exists():
        return set()
    with grid.open(newline="") as f:
        return {(r["dataset"], int(r["fold"]), r["method"], int(r["k"])) for r in csv.DictReader(f)}


def canonicalize(grid: Path) -> None:
    """Sort output deterministically; numeric reproducibility requires an independent rerun."""
    if not grid.exists():
        return
    with grid.open(newline="") as f:
        rows = list(csv.DictReader(f))
    best: dict[tuple, dict] = {}
    for r in rows:
        best[(r["dataset"], r["method"], int(r["k"]), int(r["fold"]))] = r
    ordered = [best[k] for k in sorted(best)]
    with grid.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=GRID_FIELDS)
        w.writeheader()
        w.writerows(ordered)


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
            verifiable = True  # Both published and computed values exist; NOT a success verdict.
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

    # Bind resumption to the repaired protocol so complete legacy CSVs cannot be skipped.
    RESULTS.mkdir(exist_ok=True)
    grid = RESULTS / "grid_knn.csv"
    provenance = RESULTS / "evaluation_protocol.json"
    source_paths = [PROJECT / "data/manifests/splits.json", Path(__file__)]
    source_paths += sorted((PROJECT / "src").rglob("*.py"))
    protocol = {"schema": "validated-stratified-v1", "seed": SEED,
                "sha256": {str(p.relative_to(PROJECT)): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in source_paths}}
    if not args.recompute and grid.exists():
        if not provenance.exists() or json.loads(provenance.read_text()) != protocol:
            raise RuntimeError("Legacy or changed-protocol results: use scripts/run_fixed_evaluation.py to back up and recompute.")
    # Validate all selected dataset partitions before removing any result file.
    for name in args.datasets:
        _, labels = load(name)
        load_splits(name, len(labels))
    done = set() if args.recompute else read_done(grid)
    if args.recompute and grid.exists():
        grid.unlink()
    provenance.write_text(json.dumps(protocol, indent=2) + "\n")

    for name in args.datasets:
        X, y = load(name)
        folds = load_splits(name, len(y))
        for method in args.methods:
            if all((name, f, method, k) in done for f in range(N_FOLDS) for k in K_LIST):
                print(f"[skip] {name}/{method} 已完成")
                continue
            present = {(f, k) for f in range(N_FOLDS) for k in K_LIST if (name, f, method, k) in done}
            if present:
                raise RuntimeError("Partial method results cannot safely resume: back up CSVs and use a full --recompute.")
            t = time.time()
            E = make_embedding(name, method, X)
            print(f"[embed] {name}/{method} {time.time()-t:.1f}s  range [{E.min():.2f}, {E.max():.2f}]")
            export_embeddings(name, method, E, y)
            rows = []
            for fold, (tr, te) in enumerate(folds):
                for k in K_LIST:
                    if (name, fold, method, k) in done:
                        continue
                    clf = KNeighborsClassifier(n_neighbors=k, metric="euclidean", weights="uniform", algorithm="brute", n_jobs=1).fit(E[tr], y[tr])
                    rows.append({"dataset": name, "fold": fold, "method": method,
                                 "k": k, "acc": f"{clf.score(E[te], y[te]):.6f}"})
            append_rows(grid, rows)
            print(f"[grid ] {name}/{method} 追加 {len(rows)} 行")

    canonicalize(grid)
    acc = summarise(grid)
    write_paper_vs_ours(acc)
    print(f"[done] rows={sum(len(v) for v in acc.values())} -> results/grid_knn.csv, "
          f"grid_knn_summary.csv, paper_vs_ours.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
