# 报告数字表（Number Lock）· 模板 v0

> 发布：**S1**（Day1 10:00，模板）/ **S3**（Day2 22:00，终值）· 维护人：A · 消费者：C（报告/slides 唯一取数来源）

> **状态：模板**。表里的 `{{...}}` 是占位符，等 P5 主表与 P6 终值填入（S3 发布）；**当前不是结果，禁止引用**。


## 规则（三条，别破）

1. 报告/slides 里出现的**每一个**数值都必须能在这里找到对应键，并能再指到 `results/grid_knn.csv` 的行（`dataset, method, k, fold`）。
2. 占位符键名固定，C 的正文直接写 `{{...}}`；P14 时用脚本整表替换，**不改句子**。
3. 同一个数字只有一个来源：均值/标准差来自 `grid_knn.csv` 的逐折聚合，判定词来自 `paper_vs_ours.csv`。不许手抄。

## 1 主结果：kNN 精度（10 折分层，均值 ± 折间 std）

| 数据集 | 方法 | k=10 | k=20 | k=40 | k=80 | k=160 |
|---|---|---|---|---|---|---|
| PenDigits | PCA | {{knn.pendigits.pca.k10.mean}} ± {{knn.pendigits.pca.k10.std}} | {{knn.pendigits.pca.k20.mean}} ± {{knn.pendigits.pca.k20.std}} | {{knn.pendigits.pca.k40.mean}} ± {{knn.pendigits.pca.k40.std}} | {{knn.pendigits.pca.k80.mean}} ± {{knn.pendigits.pca.k80.std}} | {{knn.pendigits.pca.k160.mean}} ± {{knn.pendigits.pca.k160.std}} |
| PenDigits | t-SNE | {{knn.pendigits.tsne.k10.mean}} ± {{knn.pendigits.tsne.k10.std}} | {{knn.pendigits.tsne.k20.mean}} ± {{knn.pendigits.tsne.k20.std}} | {{knn.pendigits.tsne.k40.mean}} ± {{knn.pendigits.tsne.k40.std}} | {{knn.pendigits.tsne.k80.mean}} ± {{knn.pendigits.tsne.k80.std}} | {{knn.pendigits.tsne.k160.mean}} ± {{knn.pendigits.tsne.k160.std}} |
| PenDigits | UMAP-ref | {{knn.pendigits.umap_ref.k10.mean}} ± {{knn.pendigits.umap_ref.k10.std}} | {{knn.pendigits.umap_ref.k20.mean}} ± {{knn.pendigits.umap_ref.k20.std}} | {{knn.pendigits.umap_ref.k40.mean}} ± {{knn.pendigits.umap_ref.k40.std}} | {{knn.pendigits.umap_ref.k80.mean}} ± {{knn.pendigits.umap_ref.k80.std}} | {{knn.pendigits.umap_ref.k160.mean}} ± {{knn.pendigits.umap_ref.k160.std}} |
| PenDigits | UMAP-ours | {{knn.pendigits.umap_ours.k10.mean}} ± {{knn.pendigits.umap_ours.k10.std}} | {{knn.pendigits.umap_ours.k20.mean}} ± {{knn.pendigits.umap_ours.k20.std}} | {{knn.pendigits.umap_ours.k40.mean}} ± {{knn.pendigits.umap_ours.k40.std}} | {{knn.pendigits.umap_ours.k80.mean}} ± {{knn.pendigits.umap_ours.k80.std}} | {{knn.pendigits.umap_ours.k160.mean}} ± {{knn.pendigits.umap_ours.k160.std}} |
| COIL-20 | PCA | {{knn.coil20.pca.k10.mean}} ± {{knn.coil20.pca.k10.std}} | {{knn.coil20.pca.k20.mean}} ± {{knn.coil20.pca.k20.std}} | {{knn.coil20.pca.k40.mean}} ± {{knn.coil20.pca.k40.std}} | {{knn.coil20.pca.k80.mean}} ± {{knn.coil20.pca.k80.std}} | {{knn.coil20.pca.k160.mean}} ± {{knn.coil20.pca.k160.std}} |
| COIL-20 | t-SNE | {{knn.coil20.tsne.k10.mean}} ± {{knn.coil20.tsne.k10.std}} | {{knn.coil20.tsne.k20.mean}} ± {{knn.coil20.tsne.k20.std}} | {{knn.coil20.tsne.k40.mean}} ± {{knn.coil20.tsne.k40.std}} | {{knn.coil20.tsne.k80.mean}} ± {{knn.coil20.tsne.k80.std}} | {{knn.coil20.tsne.k160.mean}} ± {{knn.coil20.tsne.k160.std}} |
| COIL-20 | UMAP-ref | {{knn.coil20.umap_ref.k10.mean}} ± {{knn.coil20.umap_ref.k10.std}} | {{knn.coil20.umap_ref.k20.mean}} ± {{knn.coil20.umap_ref.k20.std}} | {{knn.coil20.umap_ref.k40.mean}} ± {{knn.coil20.umap_ref.k40.std}} | {{knn.coil20.umap_ref.k80.mean}} ± {{knn.coil20.umap_ref.k80.std}} | {{knn.coil20.umap_ref.k160.mean}} ± {{knn.coil20.umap_ref.k160.std}} |
| COIL-20 | UMAP-ours | {{knn.coil20.umap_ours.k10.mean}} ± {{knn.coil20.umap_ours.k10.std}} | {{knn.coil20.umap_ours.k20.mean}} ± {{knn.coil20.umap_ours.k20.std}} | {{knn.coil20.umap_ours.k40.mean}} ± {{knn.coil20.umap_ours.k40.std}} | {{knn.coil20.umap_ours.k80.mean}} ± {{knn.coil20.umap_ours.k80.std}} | {{knn.coil20.umap_ours.k160.mean}} ± {{knn.coil20.umap_ours.k160.std}} |

## 2 运行时间（同机 fit 秒数，3 次取中位数；硬件见报告附录）

| 数据集 | PCA | t-SNE | UMAP-ref | UMAP-ours |
|---|---|---|---|---|
| PenDigits | {{runtime.pendigits.pca.fit_s}} | {{runtime.pendigits.tsne.fit_s}} | {{runtime.pendigits.umap_ref.fit_s}} | {{runtime.pendigits.umap_ours.fit_s}} |
| COIL-20 | {{runtime.coil20.pca.fit_s}} | {{runtime.coil20.tsne.fit_s}} | {{runtime.coil20.umap_ref.fit_s}} | {{runtime.coil20.umap_ours.fit_s}} |

## 3 判定词（复现 / 部分复现 / 未复现 / 不可比）

| 数据集 | k=10 | k=20 | k=40 | k=80 | k=160 |
|---|---|---|---|---|---|
| PenDigits | {{verdict.pendigits.k10}} | {{verdict.pendigits.k20}} | {{verdict.pendigits.k40}} | {{verdict.pendigits.k80}} | {{verdict.pendigits.k160}} |
| COIL-20 | {{verdict.coil20.k10}} | {{verdict.coil20.k20}} | {{verdict.coil20.k40}} | {{verdict.coil20.k80}} | {{verdict.coil20.k160}} |

## 4 原文数字从哪来

原文侧的数字**不在这里**，只在 `docs/goal/PAPER_DATA.md`（Table 1/2 全量转录 + 页码锚点）。这里只放**我们的**数字与判定，避免两边各存一份原文数字后对不上。

## 5 临时参考值（不是结果）

写句子需要量级时用 11-10 冒烟实测值（`results/smoke_umap/digits.json`、`coil20.json`；口径为主表同一套 t-SNE/UMAP 默认参数，10 折）：PenDigits t-SNE 0.987/0.951、UMAP-ref 0.988/0.921（k=10/160）；COIL-20 t-SNE 0.958/0.765/0.640、UMAP-ref 0.860/0.806/0.606（k=10/80/160）。**方向参考，不得当结论。**


## 6 键名清单（C 只允许用这四种形式）

| 形式 | 例 | 语义 |
|---|---|---|
| `{{knn.<dataset>.<method>.k<k>.mean}}` | `{{knn.coil20.umap_ours.k80.mean}}` | 10 折均值，来源 `grid_knn_summary.csv` |
| `{{knn.<dataset>.<method>.k<k>.std}}` | `{{knn.coil20.umap_ours.k80.std}}` | 折间 std（ddof=1） |
| `{{runtime.<dataset>.<method>.fit_s}}` | `{{runtime.coil20.tsne.fit_s}}` | 同机 fit 秒数中位数 |
| `{{verdict.<dataset>.k<k>}}` | `{{verdict.coil20.k160}}` | 复现 / 部分复现 / 未复现 / 不可比 |

- `<dataset>` ∈ `pendigits` `coil20`；`<method>` ∈ `pca` `tsne` `umap_ref` `umap_ours`；`<k>` ∈ `10` `20` `40` `80` `160`。
- 只允许这四种；需要别的口径（如 per-fold）走附录表并注明来源列，不进正文占位符。
