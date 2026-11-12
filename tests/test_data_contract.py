"""数据契约测试（SPEC §3 R1–R8）。B 的 npz 与 A 的 loader 都必须满足同一套断言。"""

from __future__ import annotations

import numpy as np
import pytest

from src.data import EXPECTED, array_sha256, load, load_fresh

NAMES = ["pendigits", "coil20"]


@pytest.fixture(scope="module", params=NAMES)
def data(request):
    return request.param, load(request.param)


def test_shape_and_dtype(data):
    name, (X, y) = data
    n, d = EXPECTED[name]
    assert X.shape == (n, d)
    assert y.shape == (n,)
    assert X.dtype == np.float32, X.dtype
    assert y.dtype == np.int64, y.dtype
    assert X.flags["C_CONTIGUOUS"], "X 必须是 C 序（R1）"


def test_no_nan_or_inf(data):
    name, (X, y) = data
    assert np.isfinite(X).all(), f"{name}: X 含 NaN/inf（R5）"
    assert np.isfinite(y).all()


def test_value_range(data):
    name, (X, _) = data
    assert X.min() >= 0.0 and X.max() <= 1.0 + 1e-6, (name, X.min(), X.max())


def test_labels_contiguous_and_cover_classes(data):
    name, (_, y) = data
    k = 10 if name == "pendigits" else 20
    assert y.min() == 0 and y.max() == k - 1
    assert len(np.unique(y)) == k
    counts = np.bincount(y)
    assert counts.min() > 0
    # 首次出现编码：每个标签的第一次出现位置递增
    first_pos = [int(np.argmax(y == c)) for c in range(k)]
    assert first_pos == sorted(first_pos), "标签未按首次出现顺序编码（R1）"


def test_deterministic_across_calls(data):
    name, (X, y) = data
    X2, y2 = load_fresh(name)
    assert array_sha256(X, y) == array_sha256(X2, y2), f"{name}: 两次加载哈希不同"
    assert np.array_equal(y, y2)


def test_paper_counts(data):
    name, (X, _) = data
    n, _ = EXPECTED[name]
    assert X.shape[0] == n, f"{name}: 行数 {X.shape[0]} != 原文 {n}"


def test_coil20_class_counts():
    _, y = load("coil20")
    counts = np.bincount(y)
    assert counts.tolist() == [72] * 20, counts.tolist()


def test_unknown_dataset_raises():
    with pytest.raises(KeyError):
        load("mnist")
