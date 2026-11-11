"""生成与 run_grid.py 逐索引对齐的折划分，以及一份数据契约清单（manifest）。

B 组员的数据准备管道必须与本脚本产出一致：
- data/processed/splits.json      折划分（train/test 索引）
- data/manifests/{name}.json      行数、特征名、标签分布（用于对拍）

用法：
    .venv/bin/python scripts/make_splits.py                     # 全部数据集
    .venv/bin/python scripts/make_splits.py --datasets pima,oil # 指定数据集
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.model_selection import StratifiedKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import datasets as D  # noqa: E402

SPLITS = ROOT / "data/processed/splits.json"
MANIFESTS = ROOT / "data/manifests"


def build(name: str, folds: int, repeats: int, seed: int) -> dict:
    X, y = D.load(name)
    out: dict[str, dict[str, list[int]]] = {}
    for rep in range(repeats):
        skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed + rep)
        for k, (tr, te) in enumerate(skf.split(X, y), start=1):
            out[f"rep{rep}_fold{k}"] = {"train": tr.tolist(), "test": te.tolist()}
    return {
        "dataset": name,
        "seed": seed,
        "folds": folds,
        "repeats": repeats,
        "n": int(len(y)),
        "n_minority": int(y.sum()),
        "n_majority": int((1 - y).sum()),
        "splits": out,
    }


def manifest(name: str, X, y) -> dict:
    return {
        "dataset": name,
        "n": int(len(y)),
        "n_features": int(X.shape[1]),
        "n_minority": int(y.sum()),
        "n_majority": int((1 - y).sum()),
        "ir": round(float((1 - y).sum() / max(y.sum(), 1)), 4),
        "columns": [str(c) for c in X.columns],
        "dtypes": {str(c): str(t) for c, t in X.dtypes.items()},
        "nan_total": int(X.isna().sum().sum()),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--datasets", default="all")
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--repeats", type=int, default=2)
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args(argv)

    names = list(D.DATASETS) if a.datasets == "all" else [s for s in a.datasets.split(",") if s]
    SPLITS.parent.mkdir(parents=True, exist_ok=True)
    MANIFESTS.mkdir(parents=True, exist_ok=True)

    payload = {"seed": a.seed, "folds": a.folds, "repeats": a.repeats, "datasets": {}}
    for name in names:
        t0 = time.time()
        try:
            X, y = D.load(name)
            payload["datasets"][name] = build(name, a.folds, a.repeats, a.seed)
            (MANIFESTS / f"{name}.json").write_text(
                json.dumps(manifest(name, X, y), ensure_ascii=False, indent=2))
            print(f"[{name}] n={len(y)} min={int(y.sum())} folds={len(payload['datasets'][name]['splits'])}"
                  f" in {time.time() - t0:.1f}s", flush=True)
        except Exception as e:  # 单个数据集失败不阻塞其余
            print(f"[{name}] SKIP {type(e).__name__}: {e}", flush=True)

    if not payload["datasets"]:
        print("no splits written")
        return 1
    SPLITS.write_text(json.dumps(payload, ensure_ascii=False))
    print(f"wrote {SPLITS} ({SPLITS.stat().st_size / 1e6:.2f} MB) and {len(payload['datasets'])} manifests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
