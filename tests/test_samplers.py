"""采样器语义的单测：重点是“N% 过采样 = 额外合成 N%”的换算和 >1:1 的情况。"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import samplers as S  # noqa: E402


def y_imbalanced():
    """多数 500 / 少数 50，IR = 10。"""
    return np.array([0] * 500 + [1] * 50)


def test_none_returns_no_sampler():
    sampler, canon = S.build("none", y=y_imbalanced(), seed=0)
    assert sampler is None and canon == "none"


def test_smote_percent_is_extra_minority():
    y = y_imbalanced()
    for pct, expected in [(100, 100), (200, 150), (500, 300)]:
        sampler, _ = S.build(f"smote{pct}", y=y, seed=0)
        assert sampler.sampling_strategy == {1: expected}, pct


def test_smote_can_exceed_majority():
    """低不平衡比时论文会合成到超过多数类，不能 clamp 到 1:1。"""
    y = np.array([0] * 500 + [1] * 268)
    sampler, _ = S.build("smote500", y=y, seed=0)
    assert sampler.sampling_strategy == {1: 1608}


def test_smote_k_override():
    sampler, _ = S.build("smote100_k3", y=y_imbalanced(), seed=0)
    assert sampler.k_neighbors == 3


def test_rus_keeps_fraction_of_majority_but_not_below_minority():
    y = y_imbalanced()  # 多数 500，少数 50
    sampler, _ = S.build("rus25", y=y, seed=0)
    assert sampler.sampling_strategy == {0: 125}
    sampler, _ = S.build("rus5", y=y, seed=0)  # 25 < 50 → 由少数类数量兜底
    assert sampler.sampling_strategy == {0: 50}


@pytest.mark.parametrize("spec", ["borderline", "adasyn", "smoteenn", "smotetomek", "ros", "rus"])
def test_variants_build(spec):
    sampler, canon = S.build(spec, y=y_imbalanced(), seed=0)
    assert sampler is not None and canon == spec


def test_unknown_spec_raises():
    with pytest.raises(ValueError):
        S.build("smoote", y=y_imbalanced())
