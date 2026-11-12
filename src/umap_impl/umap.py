"""自研 UMAP 的组装：fuzzy 图 → 谱初始化 → SGD。"""

from __future__ import annotations

import numpy as np

from src.umap_impl.fuzzy import fuzzy_simplicial_set, smooth_knn_dist  # noqa: F401
from src.umap_impl.optimize import find_ab_params, sgd_layout
from src.umap_impl.spectral import spectral_init


class UMAPModel:
    """参数与 umap-learn 的默认口径一致（SPEC §4 E1 / D2）。"""

    def __init__(
        self,
        n_neighbors: int = 15,
        n_components: int = 2,
        min_dist: float = 0.1,
        n_epochs: int = 500,
        metric: str = "euclidean",
        init: str = "spectral",
        random_state: int = 42,
    ):
        self.n_neighbors = n_neighbors
        self.n_components = n_components
        self.min_dist = min_dist
        self.n_epochs = n_epochs
        self.metric = metric
        self.init = init
        self.random_state = random_state
        self.embedding_: np.ndarray | None = None
        self.graph_ = None
        self.sigma_ = None
        self.rho_ = None
        self.a_, self.b_ = find_ab_params(1.0, min_dist)

    def fit(self, X):
        X = np.asarray(X, dtype=np.float32)
        graph, sigma, rho = fuzzy_simplicial_set(X, self.n_neighbors, self.metric)
        self.graph_, self.sigma_, self.rho_ = graph, sigma, rho

        rng = np.random.default_rng(self.random_state)
        if self.init == "spectral":
            emb = spectral_init(graph, self.n_components, seed=self.random_state)
        elif self.init == "pca":
            from sklearn.decomposition import PCA

            emb = PCA(n_components=self.n_components, random_state=self.random_state).fit_transform(X)
            emb = (emb * (10.0 / np.abs(emb).max())).astype(np.float32)
        else:
            emb = rng.uniform(-10.0, 10.0, size=(X.shape[0], self.n_components)).astype(np.float32)

        self.embedding_ = sgd_layout(
            graph,
            emb,
            n_epochs=self.n_epochs,
            a=self.a_,
            b=self.b_,
            seed=self.random_state,
        )
        return self

    def fit_transform(self, X):
        return self.fit(X).embedding_


def umap_ours(X, **kwargs):
    return UMAPModel(**kwargs).fit_transform(X)
