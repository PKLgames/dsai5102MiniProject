"""指标：AUC（主）、PR-AUC、G-mean、F1、Brier。

G-mean 按 Kubat & Matwin 的定义 sqrt(TPR × TNR)，在固定阈值 0.5 上计算；
同时保留 PR-AUC 与 Brier，避免只看 AUC 得出片面结论（不平衡数据的常见陷阱）。
"""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (average_precision_score, brier_score_loss, f1_score,
                             recall_score, roc_auc_score)


def gmean(y_true, y_pred) -> float:
    tpr = recall_score(y_true, y_pred, pos_label=1, zero_division=0)
    tnr = recall_score(y_true, y_pred, pos_label=0, zero_division=0)
    return float(np.sqrt(tpr * tnr))


def all_metrics(y_true, proba, pred=None) -> dict:
    proba = np.asarray(proba, dtype=float)
    if pred is None:
        pred = (proba >= 0.5).astype(int)
    return {
        "auc": float(roc_auc_score(y_true, proba)),
        "pr_auc": float(average_precision_score(y_true, proba)),
        "gmean": gmean(y_true, pred),
        "f1_minority": float(f1_score(y_true, pred, pos_label=1, zero_division=0)),
        "brier": float(brier_score_loss(y_true, proba)),
    }
