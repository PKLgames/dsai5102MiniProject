# 结果 → 报告映射

> 报告里每一处数字/图都从本表取；**不要手抄**。所有路径相对仓库根。

## 1. 文件 → 报告位置

| 结果文件 | 内容 | 用到报告哪里 |
|---|---|---|
| `results/grid_knn.csv` | 逐折明细（2 数据集 × 10 折 × 4 方法 × 5 k = 400 行） | 表 2 的底层数据；附录可给列说明 |
| `results/grid_knn_summary.csv` | 聚合 mean ± std(ddof=1) | **表 2** |
| `results/paper_vs_ours.csv` | `dataset,method,k,paper_acc,paper_std,our_acc,our_std,delta,n_folds,verifiable` | **表 3** + **Fig.3** |
| `results/runtime.csv` | `dataset,method,median_s,min_s,max_s,timeout` | **表 4** |
| `results/embeddings/coil20_{umapours,tsne}.npz` | `E`(1440×2 float32)、`y`(1440 int64) | Fig.2 的输入（B 渲染） |
| `figures/results/fig2_qualitative_coil20.png` | COIL-20 定性两联图 | **Fig.2** |
| `figures/results/fig3_paper_vs_ours.png` | 原文 vs 我们 散点 | **Fig.3** |
| `results/README_numbers.md` | 唯一数字来源（含判定词） | §4 正文与结论表 |
| `docs/goal/PAPER_DATA.md` | 原文 Table 1/2/3 | 表 3 的 `paper_acc` 列、Fig.3 的 x 轴 |
| `docs/log/DEVIATIONS.md` | D1–D18 | 附录 A、§5 诊断 |
| `docs/goal/DATA_CARD.md` | 数据来源与预处理 | 表 1、§3 数据段 |

## 2. 判定怎么落到文字

| 判定 | 报告写法 | 证据 |
|---|---|---|
| 复现 | 「C2 在 X 数据集上复现：方向一致、排序一致、`|Δ|≤tol`」 | `paper_vs_ours.csv` 对应行 + tol 见 SPEC §5 |
| 部分复现 | 「方向与排序一致，但幅度超 tol（Δ=…）」 | 同上，标 `delta` |
| 未复现 | 「方向不符 / 未完成」，并给出归因 | `DEVIATIONS` D9 的归因段 |
| 不可比 | 「本机无对应口径（如 LargeVis）」，不计入分母 | DEVIATIONS D1 |

## 3. 三条硬规则

1. 报告里的数字必须能在 `README_numbers.md` 找到**同名行**（C 只复制，不计算）。
2. 图与 csv 必须一致：Fig.3 的点数 = `paper_vs_ours.csv` 中 `paper_acc` 非空的行数；改动图必须重跑 `scripts/make_figures.py`。
3. 报告、slides、`README_numbers.md` 三处数字逐项相同（A 抽查 10 处）。
