"""数据契约测试：manifests / splits.json / B 的 data/processed 产物三方对拍。

- A 侧：manifests 必须与 datasets.load 一致（防止数据集配置被改坏）；
- 划分：splits.json 必须重放出同一个 StratifiedKFold（防止 B 手改索引）；
- B 侧：若 data/processed/{name}_X.csv 存在，必须与 datasets.load 逐行一致。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import StratifiedKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import datasets as D  # noqa: E402

MANIFESTS = ROOT / "data/manifests"
SPLITS = ROOT / "data/processed/splits.json"
PROCESSED = ROOT / "data/processed"

manifests = sorted(MANIFESTS.glob("*.json"))


@pytest.mark.parametrize("path", manifests, ids=[p.stem for p in manifests])
def test_manifest_matches_loader(path: Path) -> None:
    m = json.loads(path.read_text())
    X, y = D.load(m["dataset"])
    assert X.shape[0] == m["n"] == len(y)
    assert X.shape[1] == m["n_features"]
    assert int(y.sum()) == m["n_minority"]
    assert int((1 - y).sum()) == m["n_majority"]
    assert list(X.columns) == m["columns"]


@pytest.mark.skipif(not SPLITS.exists(), reason="splits.json 未生成，先跑 scripts/make_splits.py")
def test_splits_replay() -> None:
    payload = json.loads(SPLITS.read_text())
    folds, repeats, seed = payload["folds"], payload["repeats"], payload["seed"]
    for name, entry in payload["datasets"].items():
        X, y = D.load(name)
        assert entry["n"] == len(y)
        for rep in range(repeats):
            skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed + rep)
            for k, (tr, te) in enumerate(skf.split(X, y), start=1):
                got = entry["splits"][f"rep{rep}_fold{k}"]
                assert got["train"] == tr.tolist(), f"{name} rep{rep} fold{k} train 不一致"
                assert got["test"] == te.tolist(), f"{name} rep{rep} fold{k} test 不一致"
                assert not set(got["train"]) & set(got["test"])
                assert len(got["train"]) + len(got["test"]) == len(y)


@pytest.mark.parametrize("path", manifests, ids=[p.stem for p in manifests])
def test_processed_parity_if_present(path: Path) -> None:
    """B 的产物存在时逐行对拍；不存在则跳过（B 还未交付）。"""
    name = json.loads(path.read_text())["dataset"]
    csv, ycsv = PROCESSED / f"{name}_X.csv", PROCESSED / f"{name}_y.csv"
    if not (csv.exists() and ycsv.exists()):
        pytest.skip(f"{name}: B 的 processed CSV 尚未交付")

    Xb = pd.read_csv(csv)
    yb = pd.read_csv(ycsv)["y"].to_numpy()
    Xa, ya = D.load(name)

    assert Xb.shape == Xa.shape, f"{name}: 形状不一致 {Xb.shape} vs {Xa.shape}"
    assert np.array_equal(yb, ya), f"{name}: 标签不一致（正类必须同为少数类）"
    assert list(Xb.columns) == list(Xa.columns), f"{name}: 列名/顺序不一致"

    num = Xa.select_dtypes(include=[np.number]).columns
    assert np.allclose(Xb[num].to_numpy(dtype=float), Xa[num].to_numpy(dtype=float),
                       atol=1e-8), f"{name}: 数值特征不一致"
