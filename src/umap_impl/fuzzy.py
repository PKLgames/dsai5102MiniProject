"""局部模糊单纯复形（原文 Algorithm 1–3）。

与 umap-learn 0.6.0 的 smooth_knn_dist / compute_membership_strengths 等价：
- 距离矩阵含自身（第 0 列为 0），Σ_{j>=1} exp(-(d_ij - ρ_i)/σ_i) 的二分为 log2(k)
- 每一行用 ρ（最近非零距离）与 σ（二分得到的带宽）做指数衰减
- 有向权重再对称化为 (A + Aᵀ - A∘Aᵀ)（set_op_mix_ratio=1）
"""

from __future__ import annotations

import numpy as np
import scipy.sparse as sp
from sklearn.neighbors import NearestNeighbors

SMOOTH_K_TOLERANCE = 1e-5
MIN_K_DIST_SCALE = 1e-3
NPY_FLOATMAX = np.float32(np.finfo(np.float32).max)
N_ITER = 64


def smooth_knn_dist(distances, k, n_iter=N_ITER, local_connectivity=1.0, bandwidth=1.0):
    """求每点的 ρ 与 σ，使模糊集基数约为 k（原文 Algorithm 3）。"""
    distances = np.asarray(distances, dtype=np.float32)
    target = np.log2(k) * bandwidth
    n = distances.shape[0]
    rho = np.zeros(n, dtype=np.float32)
    sigma = np.zeros(n, dtype=np.float32)
    finite = distances[np.isfinite(distances)]
    mean_distances = float(finite.mean()) if finite.size else 0.0

    for i in range(n):
        lo, hi, mid = 0.0, float(NPY_FLOATMAX), 1.0
        row = distances[i]
        row = row[np.isfinite(row)]
        nz = row[row > 0.0]
        if nz.size >= local_connectivity:
            idx = int(np.floor(local_connectivity))
            frac = local_connectivity - idx
            if idx > 0:
                rho[i] = nz[idx - 1]
                if frac > SMOOTH_K_TOLERANCE:
                    rho[i] += frac * (nz[idx] - nz[idx - 1])
            else:
                rho[i] = frac * nz[0]
        elif nz.size > 0:
            rho[i] = nz.max()

        for _ in range(n_iter):
            d = (distances[i, 1:] - rho[i]).astype(np.float64)  # 与 umap 一致：先 float32 相减
            psum = float(np.where(d > 0.0, np.exp(-(d / mid)), 1.0).sum())
            if abs(psum - target) < SMOOTH_K_TOLERANCE:
                break
            if psum > target:
                hi = mid
                mid = (lo + hi) / 2.0
            else:
                lo = mid
                mid = mid * 2.0 if hi >= NPY_FLOATMAX else (lo + hi) / 2.0
        sigma[i] = mid

        if rho[i] > 0.0:
            floor = MIN_K_DIST_SCALE * float(row.mean())
        else:
            floor = MIN_K_DIST_SCALE * mean_distances
        if sigma[i] < floor:
            sigma[i] = floor

    return sigma, rho


def knn_graph(X, n_neighbors=15, metric="euclidean"):
    """精确 kNN（含自身在第 0 列），返回 (indices int32, distances float32)。"""
    nn = NearestNeighbors(n_neighbors=n_neighbors, metric=metric).fit(X)
    dist, ind = nn.kneighbors(X)
    return ind.astype(np.int32), dist.astype(np.float32)


def compute_membership_strengths(knn_indices, knn_dists, sigmas, rhos):
    """把距离转成模糊权重 w_ij = exp(-(d_ij - ρ_i)/σ_i)（自身与 d≤ρ 取 0/1）。"""
    n, k = knn_indices.shape
    rows = np.repeat(np.arange(n, dtype=np.int32), k)
    cols = knn_indices.reshape(-1)
    d = knn_dists.reshape(-1).astype(np.float32)
    r = np.repeat(rhos, k)
    s = np.repeat(sigmas, k)
    vals = np.where((d - r) <= 0.0, 1.0, np.where(s <= 0.0, 1.0, np.exp(-((d - r) / np.where(s <= 0.0, 1.0, s)))))
    vals = vals.astype(np.float32)
    vals[cols == rows] = 0.0  # 自己不连自己
    vals[cols < 0] = 0.0
    return rows, cols, vals


def fuzzy_simplicial_set(X, n_neighbors=15, metric="euclidean"):
    """返回 (graph_csr, sigma, rho)；graph 对称化后即原文的模糊单纯复形。"""
    n = X.shape[0]
    ind, dist = knn_graph(X, n_neighbors, metric)
    sigma, rho = smooth_knn_dist(dist, float(n_neighbors))
    rows, cols, vals = compute_membership_strengths(ind, dist, sigma, rho)

    directed = sp.coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsr()
    directed.eliminate_zeros()
    prod = directed.multiply(directed.transpose())
    graph = (directed + directed.transpose() - prod).tocsr()  # set_op_mix_ratio=1
    graph.eliminate_zeros()
    graph.sort_indices()
    return graph, sigma, rho
