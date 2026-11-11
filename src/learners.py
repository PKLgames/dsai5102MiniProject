"""学习器封装。

`pruned_dt` 是论文 C4.5 的代理：CART 的熵准则 + **代价复杂度剪枝（CCP）**，剪枝强度在训练折内部用
3 折 CV 选（不接触测试折）。这比 sklearn 默认的未剪枝树更接近 C4.5 的 error-based pruning，
否则单棵未剪枝树在 Pima 上只有 ~0.67 AUC，而论文 C4.5 是 ~0.72–0.73（见 DEVIATIONS.md D1）。
"""

from __future__ import annotations

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.model_selection import StratifiedKFold
from sklearn.tree import DecisionTreeClassifier


class PrunedDecisionTree(BaseEstimator, ClassifierMixin):
    """熵准则 CART + CCP 剪枝，剪枝参数由内层 CV 在训练折内选择。"""

    def __init__(self, criterion: str = "entropy", inner_folds: int = 3,
                 n_alphas: int = 20, random_state: int = 0):
        self.criterion = criterion
        self.inner_folds = inner_folds
        self.n_alphas = n_alphas
        self.random_state = random_state

    def fit(self, X, y):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
        self.classes_ = np.unique(y)
        self.n_features_in_ = X.shape[1]
        base = DecisionTreeClassifier(criterion=self.criterion, random_state=self.random_state)
        path = base.cost_complexity_pruning_path(X, y)
        alphas = np.unique(path.ccp_alphas)
        if len(alphas) > self.n_alphas:  # 只在内层 CV 里试少数几个强度，控制耗时
            idx = np.linspace(0, len(alphas) - 1, self.n_alphas).round().astype(int)
            alphas = alphas[idx]
        alphas = np.append(alphas, 0.0)  # 0.0 = 不剪枝，作为兜底候选

        best_alpha, best_score = 0.0, -np.inf
        n_min = int(np.bincount(y).min()) if len(np.unique(y)) == 2 else 2
        if n_min >= self.inner_folds:
            skf = StratifiedKFold(self.inner_folds, shuffle=True, random_state=self.random_state)
            for alpha in alphas:
                scores = []
                for tr, va in skf.split(X, y):
                    t = DecisionTreeClassifier(criterion=self.criterion, ccp_alpha=alpha,
                                               random_state=self.random_state).fit(X[tr], y[tr])
                    p = t.predict_proba(X[va])[:, 1]
                    scores.append(_auc(y[va], p))
                s = float(np.mean(scores))
                if s > best_score:
                    best_alpha, best_score = float(alpha), s

        self.ccp_alpha_ = best_alpha
        self.inner_cv_auc_ = best_score
        self.tree_ = DecisionTreeClassifier(criterion=self.criterion, ccp_alpha=best_alpha,
                                            random_state=self.random_state).fit(X, y)
        return self

    def predict_proba(self, X):
        return self.tree_.predict_proba(np.asarray(X, dtype=float))

    def predict(self, X):
        return self.tree_.predict(np.asarray(X, dtype=float))

    @property
    def node_count(self) -> int:
        return int(self.tree_.tree_.node_count)


def _auc(y_true, proba) -> float:
    from sklearn.metrics import roc_auc_score

    try:
        return float(roc_auc_score(y_true, proba))
    except ValueError:  # 验证折只有单一类别
        return 0.5
