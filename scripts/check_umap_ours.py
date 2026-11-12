"""P3/P4 对拍证据：自研实现 vs umap-learn 0.6.0。输出可直接贴进 docs/log/RUN_LOG.md。

用法：
    NUMBA_NUM_THREADS=1 .venv/bin/python scripts/check_umap_ours.py            # 两个数据集
    NUMBA_NUM_THREADS=1 .venv/bin/python scripts/check_umap_ours.py --datasets pendigits
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import warnings

import numpy as np

warnings.filterwarnings("ignore")

from sklearn.metrics import silhouette_score  # noqa: E402
from sklearn.model_selection import StratifiedKFold  # noqa: E402
from sklearn.neighbors import KNeighborsClassifier  # noqa: E402

import umap  # noqa: E402
import umap.umap_ as uu  # noqa: E402
from umap.spectral import spectral_layout  # noqa: E402

from src.data import load  # noqa: E402
from src.umap_impl import UMAPModel  # noqa: E402
from src.umap_impl.fuzzy import fuzzy_simplicial_set, knn_graph, smooth_knn_dist  # noqa: E402
from src.umap_impl.optimize import find_ab_params  # noqa: E402
from src.umap_impl.spectral import spectral_init  # noqa: E402

SEED = 42
K_LIST = (10, 160)


def rel(a, b):
    return float(np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-12)))


def knn_acc(E, y, k, folds=10):
    skf = StratifiedKFold(folds, shuffle=True, random_state=SEED)
    accs = [KNeighborsClassifier(n_neighbors=k, n_jobs=1).fit(E[tr], y[tr]).score(E[te], y[te])
            for tr, te in skf.split(E, y)]
    return float(np.mean(accs)), float(np.std(accs, ddof=1))


def check(name):
    X, y = load(name)
    print(f"\n== {name}  n={X.shape[0]} d={X.shape[1]} classes={len(np.unique(y))}")
    n_sub = min(400, X.shape[0])
    Xs = X[:n_sub]

    dist = knn_graph(Xs, 15)[1]
    rho_o, rho_r = smooth_knn_dist(dist, 15.0)[1], uu.smooth_knn_dist(dist, 15.0)[1]
    sig_o, sig_r = smooth_knn_dist(dist, 15.0)[0], uu.smooth_knn_dist(dist, 15.0)[0]
    print(f"  P3 sigma rel err {rel(sig_o, sig_r):.2e} | rho rel err {rel(rho_o, rho_r):.2e} (同一距离矩阵)")

    g, _, _ = fuzzy_simplicial_set(Xs, 15)
    ref, _, _ = uu.fuzzy_simplicial_set(Xs, 15, np.random.RandomState(SEED), "euclidean")
    print(f"  P3 graph nnz {g.nnz} vs {ref.nnz} | sum rel {abs(g.sum()-ref.sum())/ref.sum():.2e}"
          f" | max|dW| {np.abs((g-ref).toarray()).max():.3f}")

    e1 = spectral_init(g, 2, seed=SEED)
    e2 = spectral_layout(Xs, g, 2, np.random.RandomState(SEED))
    cos = [abs(np.dot(e1[:, c], e2[:, c])) / (np.linalg.norm(e1[:, c]) * np.linalg.norm(e2[:, c])) for c in range(2)]
    print(f"  P3 spectral cos {cos[0]:.6f} / {cos[1]:.6f}")

    a1, b1 = find_ab_params(1.0, 0.1)
    print(f"  P3 a,b {a1:.6f} {b1:.6f} (umap {uu.find_ab_params(1.0, 0.1)[0]:.6f} {uu.find_ab_params(1.0, 0.1)[1]:.6f})")

    t = time.time()
    Eo = UMAPModel(n_neighbors=15, min_dist=0.1, n_epochs=500, random_state=SEED).fit_transform(X)
    t_ours = time.time() - t
    t = time.time()
    Er = umap.UMAP(n_neighbors=15, min_dist=0.1, n_epochs=500, init="spectral", random_state=SEED).fit_transform(X)
    t_ref = time.time() - t
    print(f"  P4 fit  ours {t_ours:6.1f}s  ref {t_ref:6.1f}s  (x{t_ref/t_ours:.2f})")
    for k in K_LIST:
        mo, so = knn_acc(Eo, y, k)
        mr, sr = knn_acc(Er, y, k)
        print(f"  P4 kNN@{k:<3d} ours {mo:.4f}±{so:.4f}  ref {mr:.4f}±{sr:.4f}  |diff| {abs(mo-mr):.4f}")
    print(f"  P4 silhouette ours {silhouette_score(Eo, y):.3f}  ref {silhouette_score(Er, y):.3f}")
    print(f"  P4 ours range [{Eo.min():.2f}, {Eo.max():.2f}]  ref [{Er.min():.2f}, {Er.max():.2f}]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", nargs="+", default=["pendigits", "coil20"])
    args = ap.parse_args()
    for name in args.datasets:
        check(name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
