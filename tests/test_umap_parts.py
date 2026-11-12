"""P3 对拍：自研 fuzzy / spectral / a,b 与 umap-learn 0.6.0 的私有实现逐函数比对。

口径（A_TASKS P3）：喂**同一份距离矩阵**时 ρ/σ 相对误差 <1e-6；同一张图上谱初始化
按列符号对齐后余弦 >0.99。注意不要拿整条 fuzzy_simplicial_set 的 σ 比对：umap 在
重复样本（digits 有完全相同的图）上的 kNN 并列打破与我们不同，个别行 σ 会差 ~2%，
这属于 kNN 选点的差异，不是公式差异，故只对「同一距离矩阵」设硬门。
"""

from __future__ import annotations

import numpy as np
import pytest

from src.umap_impl.fuzzy import fuzzy_simplicial_set, knn_graph, smooth_knn_dist
from src.umap_impl.optimize import find_ab_params
from src.umap_impl.spectral import spectral_init

u = pytest.importorskip("umap.umap_")
from umap.spectral import spectral_layout  # noqa: E402

from src.data import load  # noqa: E402

SUB = slice(0, 300)


@pytest.fixture(scope="module")
def digits():
    X, _ = load("pendigits")
    return X[SUB]


def _rel(a, b):
    return float(np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-12)))


def test_smooth_knn_dist_matches(digits):
    _, dist = knn_graph(digits, 15)
    s1, r1 = smooth_knn_dist(dist, 15.0)
    s2, r2 = u.smooth_knn_dist(dist, 15.0)
    assert _rel(r1, r2) < 1e-6, f"rho rel err {_rel(r1, r2):.2e}"
    assert _rel(s1, s2) < 1e-6, f"sigma rel err {_rel(s1, s2):.2e}"


def test_rho_equals_nearest_nonzero_distance(digits):
    _, dist = knn_graph(digits, 15)
    _, rho = smooth_knn_dist(dist, 15.0)
    for i in range(0, 300, 37):
        nz = dist[i][dist[i] > 0]
        assert abs(float(rho[i]) - float(nz[0])) < 1e-6


def test_graph_close_to_umap(digits):
    g, _, _ = fuzzy_simplicial_set(digits, 15)
    ref, _, _ = u.fuzzy_simplicial_set(digits, 15, np.random.RandomState(42), "euclidean")
    assert g.nnz == ref.nnz
    assert abs(g.sum() - ref.sum()) / ref.sum() < 1e-3


def test_graph_is_symmetric(digits):
    g, _, _ = fuzzy_simplicial_set(digits, 15)
    diff = abs(g - g.T)
    assert diff.nnz == 0 or diff.max() < 1e-9
    assert g.diagonal().max() == 0.0


def test_spectral_init_aligns_with_umap(digits):
    g, _, _ = fuzzy_simplicial_set(digits, 15)
    e1 = spectral_init(g, 2, seed=42)
    e2 = spectral_layout(digits, g, 2, np.random.RandomState(42))
    for c in range(2):
        cos = abs(np.dot(e1[:, c], e2[:, c])) / (np.linalg.norm(e1[:, c]) * np.linalg.norm(e2[:, c]))
        assert cos > 0.99, f"col{c} cos {cos:.6f}"


def test_ab_params_match():
    for min_dist in (0.0, 0.1, 0.5):
        a1, b1 = find_ab_params(1.0, min_dist)
        a2, b2 = u.find_ab_params(1.0, min_dist)
        assert abs(a1 - a2) / a2 < 1e-6 and abs(b1 - b2) / b2 < 1e-6
