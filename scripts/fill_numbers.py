"""P6：把 results/*.csv 变成 results/README_numbers.md（报告数字的唯一来源）。

判定规则严格按 SPEC §5（三件套）：方向 / 排序 / 幅度；tol：PenDigits 0.03、COIL-20 0.10。
本脚本只做机械汇总，不做任何「调参直到通过」。

用法：NUMBA_NUM_THREADS=1 .venv/bin/python scripts/fill_numbers.py
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"
TOL = {"pendigits": 0.03, "coil20": 0.10}
SMALL_K = (10, 20, 40)
LARGE_K = (80, 160)
SMALL_K_SLACK = 0.03


def read_csv(name):
    path = RESULTS / name
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    grid = read_csv("grid_knn.csv")
    summary = read_csv("grid_knn_summary.csv")
    runtime = read_csv("runtime.csv")
    if not summary:
        print("缺 results/grid_knn_summary.csv：先跑 scripts/run_grid.py")
        return 1

    mean = {(r["dataset"], r["method"], int(r["k"])): (float(r["mean"]), float(r["std"]), int(r["n"]))
            for r in summary}
    line_of = defaultdict(list)
    for i, r in enumerate(grid, start=2):  # 表头占第 1 行
        line_of[(r["dataset"], r["method"], int(r["k"]))].append(i)
    rt = {(r["dataset"], r["method"]): r for r in runtime}
    paper = {(r["dataset"], r["method"], int(r["k"])): r for r in read_csv("paper_vs_ours.csv")}

    datasets = sorted({k[0] for k in mean})
    methods = ["pca", "tsne", "umap_ref", "umap_ours"]
    ks = sorted({k[2] for k in mean})

    def gap(ds, k):
        return mean[(ds, "umap_ours", k)][0] - mean[(ds, "tsne", k)][0]

    def ranks(ds, source):
        """同一 k 下 pca/tsne/umap 的排名（1 = 最低）；source='paper' 或 'ours'。"""
        out = {}
        for k in ks:
            if source == "paper":
                vals = {m: paper[(ds, m, k)]["paper_acc"] for m in ("pca", "tsne", "umap_ours")}
            else:
                vals = {m: mean[(ds, m, k)][0] for m in ("pca", "tsne", "umap_ours")}
            order = sorted(vals, key=lambda m: float(vals[m]))
            out[k] = {m: i + 1 for i, m in enumerate(order)}
        return out

    verdicts = {}
    for ds in datasets:
        tol = TOL[ds]
        direction = all(gap(ds, k) >= -SMALL_K_SLACK for k in SMALL_K if (ds, "umap_ours", k) in mean) and \
            all(gap(ds, k) > 0 for k in LARGE_K if (ds, "umap_ours", k) in mean)
        rp, ro = ranks(ds, "paper"), ranks(ds, "ours")
        pos = sum(rp[k][m] == ro[k][m] for k in ks for m in ("pca", "tsne", "umap_ours"))
        total = len(ks) * 3
        agree = pos / total
        ranking = agree >= 0.70
        deltas = [float(paper[(ds, m, k)]["delta"]) for m in ("umap_ours",) for k in ks if (ds, m, k) in paper]
        amplitude = all(abs(d) <= tol for d in deltas)
        if direction and ranking and amplitude:
            verdict = "复现"
        elif direction and ranking:
            verdict = "部分复现"
        elif direction:
            verdict = "部分复现（排序不一致）"
        else:
            verdict = "未复现"
        verdicts[ds] = dict(direction=direction, ranking=ranking, agree=agree, pos=pos, total=total,
                            amplitude=amplitude, tol=tol, verdict=verdict, deltas=deltas)

    L = []
    A = L.append
    A("# 结果数字（唯一来源）")
    A("")
    A("> 本文件由 `scripts/fill_numbers.py` 从 `results/grid_knn.csv`、`grid_knn_summary.csv`、")
    A("> `runtime.csv`、`paper_vs_ours.csv` 机械生成（Python 3.14 / sklearn 1.9.1 / umap-learn 0.6.0，")
    A("> seed=42，10 折分层 CV，嵌入为 transductive 全量拟合）。C 写报告只允许引用本文件的数字。")
    A("")
    A("## 0 结论速览")
    A("")
    A("| 数据集 | 判定（SPEC §5） | 方向 | 排序一致率 | 幅度 | 关键证据 |")
    A("|---|---|---|---|---|---|")
    for ds in datasets:
        v = verdicts[ds]
        A(f"| {ds} | **{v['verdict']}** | {'过' if v['direction'] else '不过'} | "
          f"{v['pos']}/{v['total']} = {v['agree']:.0%}（≥70% 为过） | "
          f"{'过' if v['amplitude'] else '不过'}（tol {v['tol']:.2f}） | "
          f"`paper_vs_ours.csv` {ds} 行 |")
    A("")
    A("## 1 kNN 精度（表 2 底稿；10 折 mean ± std, ddof=1）")
    A("")
    A("| dataset | method | k | mean | std | 键 | grid_knn.csv 行 |")
    A("|---|---|---|---|---|---|---|")
    for ds in datasets:
        for m in methods:
            for k in ks:
                if (ds, m, k) not in mean:
                    continue
                mo, sd, n = mean[(ds, m, k)]
                lines = sorted(line_of[(ds, m, k)])
                if len(lines) >= 2:
                    rng = f"{lines[0]}, {lines[1]}, …（步长 {lines[1]-lines[0]}，共 {len(lines)} 行）"
                elif lines:
                    rng = f"{lines[0]}"
                else:
                    rng = "—"
                A(f"| {ds} | {m} | {k} | {mo:.4f} | {sd:.4f} | `{{{{knn.{ds}.{m}.k{k}.mean}}}}` | {rng} |")
    A("")
    A("## 2 运行时间（表 4 底稿；只计 fit，3 次取中位数，本机 16 vCPU / joblib 串行）")
    A("")
    A("| dataset | method | median_s | min_s | max_s | 键 |")
    A("|---|---|---|---|---|---|")
    for ds in datasets:
        for m in methods:
            r = rt.get((ds, m))
            if not r:
                A(f"| {ds} | {m} | 待跑 | — | — | `{{{{runtime.{ds}.{m}.fit_s}}}}` |")
            else:
                A(f"| {ds} | {m} | {r['median_s']} | {r['min_s']} | {r['max_s']} | "
                  f"`{{{{runtime.{ds}.{m}.fit_s}}}}` |")
    A("")
    A("口径提醒：t-SNE 用 sklearn 单线程而原文用 MulticoreTSNE（D3）→ **加速比偏乐观，报告须标注方向**。")
    A("")
    A("## 3 原文 vs 我们（表 3 / Fig.3 底稿）")
    A("")
    A("| dataset | method | k | paper | ours | Δ | verifiable |")
    A("|---|---|---|---|---|---|---|")
    for ds in datasets:
        for m in ("tsne", "umap_ref", "umap_ours", "pca"):
            for k in ks:
                r = paper.get((ds, m, k))
                if not r:
                    continue
                A(f"| {ds} | {m} | {k} | {r['paper_acc']} ± {r['paper_std']} | "
                  f"{float(r['our_acc']):.4f} ± {float(r['our_std']):.4f} | {r['delta']} | {r['verifiable']} |")
    A("")
    A("## 4 判定明细")
    A("")
    for ds in datasets:
        v = verdicts[ds]
        A(f"### {ds} → **{v['verdict']}**")
        A("")
        A(f"- 方向：小 k（{', '.join(map(str, SMALL_K))}）要求 `UMAP ≥ t-SNE − {SMALL_K_SLACK}`；"
          f"大 k（{', '.join(map(str, LARGE_K))}）要求 `UMAP > t-SNE`。"
          f"我们的 UMAP−t-SNE："
          + "；".join(f"k={k}: {gap(ds, k):+.4f}" for k in ks))
        A(f"- 排序：与原文逐 k 比对 pca/tsne/UMAP 三名次，一致 {v['pos']}/{v['total']} = {v['agree']:.0%}（阈值 70%）。")
        A(f"- 幅度：|Δ| ≤ {v['tol']:.2f} → " + "；".join(f"k={k}: {float(paper[(ds, 'umap_ours', k)]['delta']):+.4f}"
                                                    for k in ks if (ds, "umap_ours", k) in paper))
        per_k = []
        for k in ks:
            g = gap(ds, k)
            ok_dir = g >= -SMALL_K_SLACK if k in SMALL_K else g > 0
            delta = float(paper[(ds, "umap_ours", k)]["delta"]) if (ds, "umap_ours", k) in paper else 0.0
            ok_amp = abs(delta) <= v["tol"]
            per_k.append(f"k={k}: {'复现' if ok_dir and ok_amp else ('部分复现' if ok_dir else '未复现')}"
                         f"（`{{{{verdict.{ds}.k{k}}}}}`）")
        A("- 逐 k 判定：" + "；".join(per_k))
        A("")
    A("## 5 写报告时要主动讲的两点")
    A("")
    A("1. **COIL-20 的差距是全局的**（D9）：不只大 k，小 k 也比原文低约 0.06–0.07；")
    A("   原文称对各算法调过参但未披露（D2），我们固定默认超参。敏感性探针：COIL-20 把 `n_neighbors`")
    A("   从 15 提到 100，我们的 kNN@10 从 0.8569 升到 0.8799（仍低于原文 0.921）。")
    A("2. **t-SNE 基线偏强**：我们 sklearn 单线程 t-SNE 在 COIL-20 上 0.961，高于原文 0.934；")
    A("   这会让「UMAP ≥ t-SNE」的方向更容易失败——报告 §5 要写清这一点，而不是只说 UMAP 差。")
    A("3. **COIL-20 k=80 是边界点**（D9）：Δ=-0.0907 落在 tol 0.10 内、方向也对，但该点在看主表前")
    A("   已按冒烟结果预登记为「未复现」；报告写「预登记未复现，实测落在 tol 边界内侧」，")
    A("   k=160（Δ=-0.2544）才是真正的未复现。数据集级判定以 §0 为准（方向在小 k 上就不过）。")
    A("")
    A("## 6 键名清单（C 只允许这四种形式）")
    A("")
    A("| 形式 | 例 | 语义 |")
    A("|---|---|---|")
    A("| `{{knn.<dataset>.<method>.k<k>.mean}}` | `{{knn.coil20.umap_ours.k80.mean}}` | 10 折均值 |")
    A("| `{{knn.<dataset>.<method>.k<k>.std}}` | `{{knn.coil20.umap_ours.k80.std}}` | 折间 std（ddof=1） |")
    A("| `{{runtime.<dataset>.<method>.fit_s}}` | `{{runtime.coil20.tsne.fit_s}}` | fit 秒数中位数 |")
    A("| `{{verdict.<dataset>.k<k>}}` | `{{verdict.coil20.k160}}` | 该数据集判定词（见 §0/§4） |")
    A("")
    A("<dataset> ∈ pendigits / coil20；<method> ∈ pca / tsne / umap_ref / umap_ours；<k> ∈ 10/20/40/80/160。")

    # 机读替换表：{{key}} -> 值（C 用 fill 脚本做机械替换，禁止手抄）
    subs: dict[str, object] = {}
    for r in summary:
        ds, method, k = r["dataset"], r["method"], int(r["k"])
        subs[f"knn.{ds}.{method}.k{k}.mean"] = f"{float(r['mean']):.4f}"
        subs[f"knn.{ds}.{method}.k{k}.std"] = f"{float(r['std']):.4f}"
    for (ds, method), r in sorted(rt.items()):
        subs[f"runtime.{ds}.{method}.fit_s"] = f"{float(r['median_s']):.2f}"
    for ds in datasets:
        for k in ks:
            g = gap(ds, k)
            ok_dir = g >= -SMALL_K_SLACK if k in SMALL_K else g > 0
            delta = float(paper[(ds, "umap_ours", k)]["delta"]) if (ds, "umap_ours", k) in paper else 0.0
            ok_amp = abs(delta) <= verdicts[ds]["tol"]
            subs[f"verdict.{ds}.k{k}"] = "复现" if ok_dir and ok_amp else ("部分复现" if ok_dir else "未复现")
    (RESULTS / "numbers.json").write_text(json.dumps(subs, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                                          encoding="utf-8")

    out = RESULTS / "README_numbers.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[done] {out.relative_to(PROJECT)}  {len(L)} 行")
    for ds in datasets:
        print(f"  {ds}: {verdicts[ds]['verdict']}  (方向 {verdicts[ds]['direction']}, 排序 {verdicts[ds]['agree']:.0%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
