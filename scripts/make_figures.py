"""出图：报告 Fig.2（各数据集 AUC vs 采样方式）与 Fig.3（折级 AUC 箱线图）。

用法：
    .venv/bin/python scripts/make_figures.py results/grid_small.csv results/grid_qsar.csv --outdir figures/results
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import analysis as A  # noqa: E402

ORDER = ["none", "rus25", "rus50", "rus100", "ros", "smote100", "smote200", "smote500"]


def _ordered(df: pd.DataFrame) -> pd.DataFrame:
    present = [s for s in ORDER if s in set(df["sampler"])]
    extra = sorted(set(df["sampler"]) - set(present))
    order = present + extra
    return df.assign(sampler=pd.Categorical(df["sampler"], categories=order, ordered=True))


def fig_auc_grid(df: pd.DataFrame, out: Path) -> None:
    d = _ordered(df[df["sampler"].isin(ORDER)])
    datasets = list(dict.fromkeys(d["dataset"]))
    ncol = min(3, len(datasets))
    nrow = (len(datasets) + ncol - 1) // ncol
    fig, axes = plt.subplots(nrow, ncol, figsize=(4.2 * ncol, 3.2 * nrow), squeeze=False)
    for ax, ds in zip(axes.ravel(), datasets):
        sub = d[d["dataset"] == ds]
        g = sub.groupby("sampler", observed=True)["auc"].agg(["mean", "std"]).reset_index()
        ax.errorbar(range(len(g)), g["mean"], yerr=g["std"], marker="o", capsize=3, lw=1.5)
        ax.set_xticks(range(len(g)))
        ax.set_xticklabels(g["sampler"], rotation=45, ha="right", fontsize=8)
        ax.set_title(ds)
        ax.set_ylabel("AUC (5x2 CV)")
        ax.grid(alpha=0.3)
    for ax in axes.ravel()[len(datasets):]:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)


def fig_box(df: pd.DataFrame, out: Path) -> None:
    d = _ordered(df[df["sampler"].isin(ORDER)])
    data = [d[d["sampler"] == s]["auc"].to_numpy() for s in ORDER if (d["sampler"] == s).any()]
    labels = [s for s in ORDER if (d["sampler"] == s).any()]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.boxplot(data, tick_labels=labels, showmeans=True)
    ax.set_ylabel("AUC per fold (all datasets pooled)")
    ax.set_xlabel("sampling method")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)


def fig_delta_vs_ir(df: pd.DataFrame, out: Path, ir: dict[str, float] | None = None) -> None:
    """C2：SMOTE 相对“无处理”的 AUC 增益 vs 不平衡比。"""
    m = A.mean_auc(df)
    rows = []
    for ds, sub in m.groupby("dataset"):
        base = sub[sub["sampler"] == "none"]
        best = sub[sub["sampler"].str.startswith("smote")]
        if base.empty or best.empty:
            continue
        rows.append(dict(dataset=ds, ir=(ir or {}).get(ds, float("nan")),
                         gain=float(best["auc_mean"].max() - base["auc_mean"].iloc[0])))
    d = pd.DataFrame(rows).dropna(subset=["ir"])
    if d.empty:
        return
    fig, ax = plt.subplots(figsize=(5, 3.6))
    ax.scatter(d["ir"], d["gain"])
    for _, r in d.iterrows():
        ax.annotate(r["dataset"], (r["ir"], r["gain"]), fontsize=7, xytext=(3, 3),
                    textcoords="offset points")
    ax.axhline(0, color="gray", lw=0.8, ls="--")
    ax.set_xlabel("imbalance ratio (majority/minority)")
    ax.set_ylabel("AUC gain of best SMOTE vs none")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("grids", nargs="+")
    p.add_argument("--outdir", default="figures/results")
    p.add_argument("--ir", default=None, help="可选：数据集 IR 的 json，用于 C2 散点图")
    a = p.parse_args(argv)

    df = pd.concat([A.load_grid(g) for g in a.grids], ignore_index=True)
    df = df.drop_duplicates(subset=["dataset", "learner", "sampler", "repeat", "fold"])
    df = df[df["learner"] == "dt"] if "learner" in df else df

    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    fig_auc_grid(df, outdir / "auc_by_sampler.png")
    fig_box(df, outdir / "box_auc.png")
    if a.ir:
        import json

        fig_delta_vs_ir(df, outdir / "gain_vs_ir.png", json.loads(Path(a.ir).read_text()))
    print(f"wrote figures to {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
