"""把 results/*.csv 变成报告表格：C1 胜负表、配对差值、显著性。

只读原始逐折结果（run_grid.py 的输出），不重跑实验，保证报告里每个数字都能追溯到 CSV。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

UNDER_PREFIXES = ("rus",)
SMOTE_PREFIXES = ("smote", "borderline", "adasyn", "smoteenn", "smotetomek")


def load_grid(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"dataset", "sampler", "learner", "repeat", "fold", "auc"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"grid csv 缺少列: {sorted(missing)}")
    return df


def mean_auc(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["dataset", "sampler"], sort=False)["auc"]
    return g.agg(auc_mean="mean", auc_std="std", n="size").reset_index()


def c1_table(df: pd.DataFrame, learner: str = "dt") -> pd.DataFrame:
    """C1：每个数据集“最佳 SMOTE 列” vs “最佳降采样列”的胜负。"""
    d = df[df["learner"] == learner] if "learner" in df.columns else df
    m = mean_auc(d)
    rows = []
    for ds, sub in m.groupby("dataset", sort=False):
        under = sub[sub["sampler"].str.startswith(UNDER_PREFIXES)]
        smote = sub[sub["sampler"].str.startswith(SMOTE_PREFIXES)]
        if under.empty or smote.empty:
            continue
        b_u = under.loc[under["auc_mean"].idxmax()]
        b_s = smote.loc[smote["auc_mean"].idxmax()]
        rows.append(dict(
            dataset=ds,
            under_sampler=b_u["sampler"], under_auc=round(float(b_u["auc_mean"]), 4),
            smote_sampler=b_s["sampler"], smote_auc=round(float(b_s["auc_mean"]), 4),
            delta=round(float(b_s["auc_mean"] - b_u["auc_mean"]), 4),
            winner="SMOTE" if b_s["auc_mean"] > b_u["auc_mean"] else "Under",
        ))
    out = pd.DataFrame(rows)
    if len(out):
        out.loc[len(out)] = dict(
            dataset="**合计**", under_sampler="", under_auc=None, smote_sampler="",
            smote_auc=None, delta=None,
            winner=f"SMOTE {(out['winner'] == 'SMOTE').sum()}/{len(out)}",
        )
    return out


def paired(df: pd.DataFrame, sampler_a: str, sampler_b: str, learner: str = "dt") -> pd.DataFrame:
    """按 (dataset, repeat, fold) 对齐两条曲线，返回 a-b 的配对差值。"""
    d = df[df["learner"] == learner] if "learner" in df.columns else df
    keys = ["dataset", "repeat", "fold"]
    a = d[d["sampler"] == sampler_a].set_index(keys)["auc"]
    b = d[d["sampler"] == sampler_b].set_index(keys)["auc"]
    out = pd.concat([a.rename("a"), b.rename("b")], axis=1).dropna()
    out["delta"] = out["a"] - out["b"]
    return out.reset_index()


def wilcoxon_by_dataset(df: pd.DataFrame, sampler_a: str, sampler_b: str,
                        learner: str = "dt") -> pd.DataFrame:
    """每个数据集内部做配对 Wilcoxon（a vs b），汇总 p 值。"""
    from scipy.stats import wilcoxon

    rows = []
    p = paired(df, sampler_a, sampler_b, learner)
    for ds, sub in p.groupby("dataset", sort=False):
        x = sub["delta"].to_numpy()
        if len(x) < 5 or not x.any():
            rows.append(dict(dataset=ds, n=len(x), median_delta=float(pd.Series(x).median()),
                             p_value=None))
            continue
        stat = wilcoxon(x - 0.0, zero_method="wilcox", alternative="greater")
        rows.append(dict(dataset=ds, n=len(x), median_delta=float(pd.Series(x).median()),
                         p_value=float(stat.pvalue)))
    return pd.DataFrame(rows)
