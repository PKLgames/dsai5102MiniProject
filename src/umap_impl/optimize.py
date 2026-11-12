"""负采样 SGD（原文 Algorithm 5）。

目标：Σ w_ij log Φ(‖y_i−y_j‖) + Σ (1-w) log(1-Φ)，Φ(x)=(1+a‖x‖^{2b})^{-1}。
实现按 umap 的调度展开：每条边的采样周期 = max_w / w_ij，每轮把「到期」的边
向量化更新；每条边每轮抽 n_neg 个负样本（按 deg^0.75 采样）。
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import curve_fit


def find_ab_params(spread: float = 1.0, min_dist: float = 0.1):
    """拟合 a、b，使曲线在 [0, spread] 内近似 1、之后再按 exp(-(x-spread)/min_dist) 衰减。"""

    def curve(x, a, b):
        return 1.0 / (1.0 + a * x ** (2 * b))

    # 与 umap.umap_.find_ab_params 完全同口径：
    # x < min_dist 时目标为 1，之后按 exp(-(x - min_dist)/spread) 衰减
    xv = np.linspace(0, spread * 3, 300)
    yv = np.zeros(xv.shape)
    yv[xv < min_dist] = 1.0
    yv[xv >= min_dist] = np.exp(-(xv[xv >= min_dist] - min_dist) / spread)
    (a, b), _ = curve_fit(curve, xv, yv)
    return float(a), float(b)


def make_epochs_per_sample(weights: np.ndarray, n_epochs: int) -> np.ndarray:
    max_w = weights.max()
    return np.where(weights > 0, max_w / np.maximum(weights, 1e-300), -1.0)


def _clip(x, lim=4.0):
    return np.clip(x, -lim, lim)


def sgd_layout(
    graph,
    init: np.ndarray,
    n_epochs: int = 500,
    a: float = 1.0,
    b: float = 1.0,
    gamma: float = 1.0,
    negative_sample_rate: int = 5,
    learning_rate: float = 1.0,
    seed: int = 42,
):
    """在模糊图上优化 2 维坐标；返回 (n, dim) float32。"""
    coo = graph.tocoo()
    mask = coo.row < coo.col  # 对称图只取上三角，避免重复计边
    head = coo.row[mask].astype(np.int64)
    tail = coo.col[mask].astype(np.int64)
    weights = coo.data[mask].astype(np.float64)

    y = np.array(init, dtype=np.float32, copy=True)
    n = y.shape[0]
    dim = y.shape[1]
    rng = np.random.default_rng(seed)

    period = make_epochs_per_sample(weights, n_epochs)
    next_sample = np.zeros(len(weights), dtype=np.float64)
    deg = np.asarray(graph.sum(axis=1)).ravel().astype(np.float64)
    neg_prob = (deg ** 0.75)
    neg_prob /= neg_prob.sum()

    for epoch in range(n_epochs):
        alpha = learning_rate * (1.0 - epoch / n_epochs)
        due = np.flatnonzero(next_sample <= epoch)
        if due.size == 0:
            continue
        next_sample[due] += period[due]

        h, t = head[due], tail[due]
        # float64 计算梯度：b≈11.4 时 d2**b 在 float32 会溢出成 inf，进而 inf/inf=nan
        d = y[h].astype(np.float64) - y[t].astype(np.float64)
        d2 = np.einsum("ij,ij->i", d, d)
        coef = np.zeros_like(d2)
        pos = d2 > 0
        coef[pos] = -2.0 * a * b * d2[pos] ** (b - 1.0) / (a * d2[pos] ** b + 1.0)
        g = _clip(coef[:, None] * d)
        np.add.at(y, h, (alpha * g).astype(np.float32))
        np.add.at(y, t, (-alpha * g).astype(np.float32))

        m = due.size * negative_sample_rate
        neg = rng.choice(n, size=m, p=neg_prob)
        hh = np.repeat(h, negative_sample_rate)
        dn = y[hh].astype(np.float64) - y[neg].astype(np.float64)
        dn2 = np.einsum("ij,ij->i", dn, dn)
        coefn = 2.0 * gamma * b / ((0.001 + dn2) * (a * dn2 ** b + 1.0))
        gn = _clip(coefn[:, None] * dn)
        np.add.at(y, hh, (alpha * gn).astype(np.float32))

    return y.astype(np.float32)
