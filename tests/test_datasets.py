"""加载器与剪枝树的单测。网络相关数据集只做“已在缓存里才比对”的软检查，避免 CI 依赖网络。"""

import sys
from pathlib import Path

import numpy as np
import pytest
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import datasets as D  # noqa: E402
from learners import PrunedDecisionTree  # noqa: E402


def test_same_label_handles_float_and_bytes_forms():
    assert D._same_label(4, "4.0")
    assert D._same_label(b"2", 2)
    assert not D._same_label(">50K", "<=50K")


def test_pima_counts_match_paper_if_cached():
    if not (D.RAW / "pima.csv").exists():
        pytest.skip("data/raw/pima.csv 未缓存")
    X, y = D.load("pima")
    assert (int(y.sum()), int((1 - y).sum())) == (268, 500)
    assert X.shape[0] == 768 and not X.isna().any().any()


def test_encode_produces_numeric_frame():
    import pandas as pd

    X = pd.DataFrame({"a": [1.0, np.nan, 3.0], "b": ["x", "y", "x"]})
    out = D._encode(X)
    assert out.shape[0] == 3 and out.shape[1] > 2
    assert all(np.issubdtype(t, np.floating) for t in out.dtypes)
    assert not out.isna().any().any()


def test_pruned_tree_prunes_and_still_predicts():
    X, y = load_breast_cancer(return_X_y=True)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
    raw = PrunedDecisionTree(random_state=0)
    raw.fit(Xtr, ytr)
    p_raw = raw.predict_proba(Xte)[:, 1]
    assert p_raw.shape == yte.shape and raw.ccp_alpha_ >= 0
    from sklearn.metrics import roc_auc_score

    assert roc_auc_score(yte, p_raw) > 0.85
