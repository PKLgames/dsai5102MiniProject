"""主网格：5×2 分层交叉验证 × {采样器} × {学习器}，输出逐折指标到 results/。

关键复现约定（与 docs/PROTOCOL.md 对应）：
- 重采样只发生在训练折内（imblearn Pipeline 保证），避免泄漏；
- 每次重采样用独立随机种子，折划分用固定种子，保证任何人重跑得到同一数字；
- 正类 = 少数类。
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from learners import PrunedDecisionTree
from sklearn.tree import DecisionTreeClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent))
import datasets as D  # noqa: E402
import metrics as M  # noqa: E402
import samplers as S  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

LEARNERS = {
    # C4.5 的代理：CART + 熵准则 + 训练折内 CCP 剪枝（见 src/learners.py、DEVIATIONS.md D1）
    "dt": lambda seed: PrunedDecisionTree(criterion="entropy", random_state=seed),
    # 剪枝代理的敏感性对照（报告 Discussion 用，不是主结果）
    "dt_raw": lambda seed: DecisionTreeClassifier(criterion="entropy", random_state=seed),
    "dt_msl5": lambda seed: DecisionTreeClassifier(criterion="entropy", min_samples_leaf=5,
                                                  random_state=seed),
    "rf": lambda seed: RandomForestClassifier(n_estimators=300, n_jobs=1, random_state=seed),
    "lr": lambda seed: LogisticRegression(max_iter=2000, random_state=seed),
}


def run(dataset: str, specs: list[str], learner: str = "dt",
        folds: int = 5, repeats: int = 2, seed: int = 0) -> pd.DataFrame:
    X, y = D.load(dataset)
    rows = []
    for spec in specs:
        for rep in range(repeats):
            skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed + rep)
            for k, (tr, te) in enumerate(skf.split(X, y), start=1):
                y_tr = y[tr]
                sampler, canon = S.build(spec, y=y_tr, seed=seed * 1000 + rep * 10 + k)
                steps = ([] if sampler is None else [("sampler", sampler)]) + \
                        [("clf", LEARNERS[learner](seed=seed + rep))]
                pipe = ImbPipeline(steps)
                t0 = time.time()
                pipe.fit(X.iloc[tr], y_tr)
                proba = pipe.predict_proba(X.iloc[te])[:, 1]
                m = M.all_metrics(y[te], proba)
                m.update(dataset=dataset, sampler=canon, learner=learner,
                         repeat=rep, fold=k, n_train=int(len(tr)), n_train_resampled=None,
                         seconds=round(time.time() - t0, 3))
                rows.append(m)
    df = pd.DataFrame(rows)
    return df


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["dataset", "learner", "sampler"], sort=False)
    out = g.agg(n=("auc", "size"), auc_mean=("auc", "mean"), auc_std=("auc", "std"),
                pr_auc_mean=("pr_auc", "mean"), gmean_mean=("gmean", "mean"),
                brier_mean=("brier", "mean"), seconds_mean=("seconds", "mean")).reset_index()
    return out.sort_values("auc_mean", ascending=False)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--datasets", default="pima", help="逗号分隔，如 pima,phoneme")
    p.add_argument("--samplers", default="none,rus,smote100", help="逗号分隔 sampler spec")
    p.add_argument("--learner", default="dt", choices=sorted(LEARNERS))
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--repeats", type=int, default=2)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="results/grid.csv")
    a = p.parse_args(argv)

    specs = [s for s in a.samplers.split(",") if s.strip()]
    frames = []
    for ds in [d for d in a.datasets.split(",") if d.strip()]:
        t0 = time.time()
        df = run(ds, specs, learner=a.learner, folds=a.folds, repeats=a.repeats, seed=a.seed)
        frames.append(df)
        print(f"[{ds}] {len(df)} folds in {time.time() - t0:.1f}s", flush=True)
    raw = pd.concat(frames, ignore_index=True)
    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    raw.to_csv(out, index=False)
    summ_path = out.with_name(out.stem + "_summary.csv")
    summ = summarize(raw)
    summ.to_csv(summ_path, index=False)
    print(summ.to_string(index=False))
    print(f"\nwrote {out} and {summ_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
