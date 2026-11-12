"""谱初始化（原文 Algorithm 4 / umap-learn spectral_layout）。

对归一化拉普拉斯 L = I - D^{-1/2} A D^{-1/2} 取最小的 dim+1 个特征向量，
丢掉平凡解（常数向量）后取前 dim 个，再缩放到最大坐标 10 并加 1e-4 噪声。

图不连通时退化为随机初始化（本项目的两个数据集均连通，仅作兜底）。
"""

from __future__ import annotations

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh


def spectral_init(graph: sp.csr_matrix, dim: int = 2, seed: int = 42):
    n = graph.shape[0]
    n_comp, _ = sp.csgraph.connected_components(graph)
    rng = np.random.default_rng(seed)
    if n_comp > 1 or n < dim + 1:
        return rng.uniform(low=-10.0, high=10.0, size=(n, dim)).astype(np.float32)

    sqrt_deg = np.sqrt(np.asarray(graph.sum(axis=0)).squeeze())
    sqrt_deg[sqrt_deg == 0] = 1.0
    D = sp.spdiags(1.0 / sqrt_deg, 0, n, n)
    A = D @ graph @ D
    L = sp.identity(n, dtype=np.float64) - A

    k = dim + 1
    ncv = max(2 * k + 1, int(np.sqrt(n)))
    vals, vecs = eigsh(
        L.tocsr().astype(np.float64),
        k,
        which="SM",
        ncv=ncv,
        tol=1e-4,
        v0=np.ones(n),
        maxiter=n * 5,
    )
    order = np.argsort(vals)[1:k]
    emb = np.asarray(vecs[:, order], dtype=np.float64)

    # 符号对齐（让每列的最大绝对值为正），避免对拍时符号翻转
    for j in range(emb.shape[1]):
        if emb[np.abs(emb[:, j]).argmax(), j] < 0:
            emb[:, j] *= -1.0

    emb = noisy_scale_coords(emb, rng, max_coord=10.0, noise=1e-4)
    return emb.astype(np.float32)


def noisy_scale_coords(coords, rng, max_coord=10.0, noise=1e-4):
    expansion = max_coord / np.abs(coords).max()
    coords = (coords * expansion).astype(np.float32)
    return coords + rng.normal(scale=noise, size=coords.shape).astype(np.float32)
