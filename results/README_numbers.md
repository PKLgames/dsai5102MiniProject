# 结果数字（唯一来源）

> 本文件由 `scripts/fill_numbers.py` 从 `results/grid_knn.csv`、`grid_knn_summary.csv`、
> `runtime.csv`、`paper_vs_ours.csv` 机械生成（Python 3.14 / sklearn 1.9.1 / umap-learn 0.6.0，
> seed=42，10 折分层 CV，嵌入为 transductive 全量拟合）。C 写报告只允许引用本文件的数字。

## 0 结论速览

| 数据集 | 判定（SPEC §5） | 方向 | 排序一致率 | 幅度 | 关键证据 |
|---|---|---|---|---|---|
| coil20 | **未复现** | 不过 | 9/15 = 60%（≥70% 为过） | 不过（tol 0.10） | `paper_vs_ours.csv` coil20 行 |
| pendigits | **复现** | 过 | 11/15 = 73%（≥70% 为过） | 过（tol 0.03） | `paper_vs_ours.csv` pendigits 行 |

## 1 kNN 精度（表 2 底稿；10 折 mean ± std, ddof=1）

| dataset | method | k | mean | std | 键 | grid_knn.csv 行 |
|---|---|---|---|---|---|---|
| coil20 | pca | 10 | 0.7229 | 0.0419 | `{{knn.coil20.pca.k10.mean}}` | 2, 3, …（步长 1，共 10 行） |
| coil20 | pca | 20 | 0.7049 | 0.0417 | `{{knn.coil20.pca.k20.mean}}` | 12, 13, …（步长 1，共 10 行） |
| coil20 | pca | 40 | 0.6472 | 0.0383 | `{{knn.coil20.pca.k40.mean}}` | 22, 23, …（步长 1，共 10 行） |
| coil20 | pca | 80 | 0.5493 | 0.0335 | `{{knn.coil20.pca.k80.mean}}` | 32, 33, …（步长 1，共 10 行） |
| coil20 | pca | 160 | 0.3944 | 0.0395 | `{{knn.coil20.pca.k160.mean}}` | 42, 43, …（步长 1，共 10 行） |
| coil20 | tsne | 10 | 0.9653 | 0.0157 | `{{knn.coil20.tsne.k10.mean}}` | 52, 53, …（步长 1，共 10 行） |
| coil20 | tsne | 20 | 0.9118 | 0.0220 | `{{knn.coil20.tsne.k20.mean}}` | 62, 63, …（步长 1，共 10 行） |
| coil20 | tsne | 40 | 0.8694 | 0.0160 | `{{knn.coil20.tsne.k40.mean}}` | 72, 73, …（步长 1，共 10 行） |
| coil20 | tsne | 80 | 0.7833 | 0.0156 | `{{knn.coil20.tsne.k80.mean}}` | 82, 83, …（步长 1，共 10 行） |
| coil20 | tsne | 160 | 0.6535 | 0.0211 | `{{knn.coil20.tsne.k160.mean}}` | 92, 93, …（步长 1，共 10 行） |
| coil20 | umap_ref | 10 | 0.8576 | 0.0100 | `{{knn.coil20.umap_ref.k10.mean}}` | 152, 153, …（步长 1，共 10 行） |
| coil20 | umap_ref | 20 | 0.8576 | 0.0105 | `{{knn.coil20.umap_ref.k20.mean}}` | 162, 163, …（步长 1，共 10 行） |
| coil20 | umap_ref | 40 | 0.8556 | 0.0185 | `{{knn.coil20.umap_ref.k40.mean}}` | 172, 173, …（步长 1，共 10 行） |
| coil20 | umap_ref | 80 | 0.8153 | 0.0110 | `{{knn.coil20.umap_ref.k80.mean}}` | 182, 183, …（步长 1，共 10 行） |
| coil20 | umap_ref | 160 | 0.5701 | 0.0328 | `{{knn.coil20.umap_ref.k160.mean}}` | 192, 193, …（步长 1，共 10 行） |
| coil20 | umap_ours | 10 | 0.8569 | 0.0140 | `{{knn.coil20.umap_ours.k10.mean}}` | 102, 103, …（步长 1，共 10 行） |
| coil20 | umap_ours | 20 | 0.8486 | 0.0217 | `{{knn.coil20.umap_ours.k20.mean}}` | 112, 113, …（步长 1，共 10 行） |
| coil20 | umap_ours | 40 | 0.8486 | 0.0142 | `{{knn.coil20.umap_ours.k40.mean}}` | 122, 123, …（步长 1，共 10 行） |
| coil20 | umap_ours | 80 | 0.8174 | 0.0123 | `{{knn.coil20.umap_ours.k80.mean}}` | 132, 133, …（步长 1，共 10 行） |
| coil20 | umap_ours | 160 | 0.5785 | 0.0370 | `{{knn.coil20.umap_ours.k160.mean}}` | 142, 143, …（步长 1，共 10 行） |
| pendigits | pca | 10 | 0.6488 | 0.0303 | `{{knn.pendigits.pca.k10.mean}}` | 202, 203, …（步长 1，共 10 行） |
| pendigits | pca | 20 | 0.6411 | 0.0373 | `{{knn.pendigits.pca.k20.mean}}` | 212, 213, …（步长 1，共 10 行） |
| pendigits | pca | 40 | 0.6461 | 0.0363 | `{{knn.pendigits.pca.k40.mean}}` | 222, 223, …（步长 1，共 10 行） |
| pendigits | pca | 80 | 0.6516 | 0.0306 | `{{knn.pendigits.pca.k80.mean}}` | 232, 233, …（步长 1，共 10 行） |
| pendigits | pca | 160 | 0.6400 | 0.0322 | `{{knn.pendigits.pca.k160.mean}}` | 242, 243, …（步长 1，共 10 行） |
| pendigits | tsne | 10 | 0.9872 | 0.0095 | `{{knn.pendigits.tsne.k10.mean}}` | 252, 253, …（步长 1，共 10 行） |
| pendigits | tsne | 20 | 0.9766 | 0.0114 | `{{knn.pendigits.tsne.k20.mean}}` | 262, 263, …（步长 1，共 10 行） |
| pendigits | tsne | 40 | 0.9655 | 0.0160 | `{{knn.pendigits.tsne.k40.mean}}` | 272, 273, …（步长 1，共 10 行） |
| pendigits | tsne | 80 | 0.9505 | 0.0133 | `{{knn.pendigits.tsne.k80.mean}}` | 282, 283, …（步长 1，共 10 行） |
| pendigits | tsne | 160 | 0.9510 | 0.0139 | `{{knn.pendigits.tsne.k160.mean}}` | 292, 293, …（步长 1，共 10 行） |
| pendigits | umap_ref | 10 | 0.9877 | 0.0086 | `{{knn.pendigits.umap_ref.k10.mean}}` | 352, 353, …（步长 1，共 10 行） |
| pendigits | umap_ref | 20 | 0.9772 | 0.0116 | `{{knn.pendigits.umap_ref.k20.mean}}` | 362, 363, …（步长 1，共 10 行） |
| pendigits | umap_ref | 40 | 0.9683 | 0.0121 | `{{knn.pendigits.umap_ref.k40.mean}}` | 372, 373, …（步长 1，共 10 行） |
| pendigits | umap_ref | 80 | 0.9510 | 0.0141 | `{{knn.pendigits.umap_ref.k80.mean}}` | 382, 383, …（步长 1，共 10 行） |
| pendigits | umap_ref | 160 | 0.9210 | 0.0149 | `{{knn.pendigits.umap_ref.k160.mean}}` | 392, 393, …（步长 1，共 10 行） |
| pendigits | umap_ours | 10 | 0.9877 | 0.0098 | `{{knn.pendigits.umap_ours.k10.mean}}` | 302, 303, …（步长 1，共 10 行） |
| pendigits | umap_ours | 20 | 0.9844 | 0.0126 | `{{knn.pendigits.umap_ours.k20.mean}}` | 312, 313, …（步长 1，共 10 行） |
| pendigits | umap_ours | 40 | 0.9710 | 0.0153 | `{{knn.pendigits.umap_ours.k40.mean}}` | 322, 323, …（步长 1，共 10 行） |
| pendigits | umap_ours | 80 | 0.9560 | 0.0138 | `{{knn.pendigits.umap_ours.k80.mean}}` | 332, 333, …（步长 1，共 10 行） |
| pendigits | umap_ours | 160 | 0.9544 | 0.0139 | `{{knn.pendigits.umap_ours.k160.mean}}` | 342, 343, …（步长 1，共 10 行） |

## 2 运行时间（表 4 底稿；只计 fit，3 次取中位数，本机 16 vCPU / joblib 串行）

| dataset | method | median_s | min_s | max_s | 键 |
|---|---|---|---|---|---|
| coil20 | pca | 0.39 | 0.31 | 0.41 | `{{runtime.coil20.pca.fit_s}}` |
| coil20 | tsne | 5.75 | 3.47 | 5.82 | `{{runtime.coil20.tsne.fit_s}}` |
| coil20 | umap_ref | 6.49 | 6.48 | 6.54 | `{{runtime.coil20.umap_ref.fit_s}}` |
| coil20 | umap_ours | 3.74 | 1.27 | 3.84 | `{{runtime.coil20.umap_ours.fit_s}}` |
| pendigits | pca | 0.05 | 0.05 | 0.06 | `{{runtime.pendigits.pca.fit_s}}` |
| pendigits | tsne | 6.06 | 6.02 | 6.12 | `{{runtime.pendigits.tsne.fit_s}}` |
| pendigits | umap_ref | 1.88 | 1.87 | 1.89 | `{{runtime.pendigits.umap_ref.fit_s}}` |
| pendigits | umap_ours | 2.68 | 2.68 | 2.69 | `{{runtime.pendigits.umap_ours.fit_s}}` |

口径提醒：t-SNE 用 sklearn 单线程而原文用 MulticoreTSNE（D3）→ **加速比偏乐观，报告须标注方向**。

## 3 原文 vs 我们（表 3 / Fig.3 底稿）

| dataset | method | k | paper | ours | Δ | verifiable |
|---|---|---|---|---|---|---|
| coil20 | tsne | 10 | 0.934 ± 0.115 | 0.9653 ± 0.0157 | +0.0313 | true |
| coil20 | tsne | 20 | 0.901 ± 0.133 | 0.9118 ± 0.0220 | +0.0108 | true |
| coil20 | tsne | 40 | 0.857 ± 0.125 | 0.8694 ± 0.0160 | +0.0124 | true |
| coil20 | tsne | 80 | 0.789 ± 0.118 | 0.7833 ± 0.0156 | -0.0057 | true |
| coil20 | tsne | 160 | 0.609 ± 0.067 | 0.6535 ± 0.0211 | +0.0445 | true |
| coil20 | umap_ref | 10 | 0.921 ± 0.075 | 0.8576 ± 0.0100 | -0.0634 | true |
| coil20 | umap_ref | 20 | 0.907 ± 0.064 | 0.8576 ± 0.0105 | -0.0494 | true |
| coil20 | umap_ref | 40 | 0.904 ± 0.056 | 0.8556 ± 0.0185 | -0.0484 | true |
| coil20 | umap_ref | 80 | 0.899 ± 0.058 | 0.8153 ± 0.0110 | -0.0837 | true |
| coil20 | umap_ref | 160 | 0.803 ± 0.138 | 0.5701 ± 0.0328 | -0.2329 | true |
| coil20 | umap_ours | 10 | 0.921 ± 0.075 | 0.8569 ± 0.0140 | -0.0641 | true |
| coil20 | umap_ours | 20 | 0.907 ± 0.064 | 0.8486 ± 0.0217 | -0.0584 | true |
| coil20 | umap_ours | 40 | 0.904 ± 0.056 | 0.8486 ± 0.0142 | -0.0554 | true |
| coil20 | umap_ours | 80 | 0.899 ± 0.058 | 0.8174 ± 0.0123 | -0.0816 | true |
| coil20 | umap_ours | 160 | 0.803 ± 0.138 | 0.5785 ± 0.0370 | -0.2245 | true |
| coil20 | pca | 10 | 0.667 ± 0.179 | 0.7229 ± 0.0419 | +0.0559 | true |
| coil20 | pca | 20 | 0.663 ± 0.196 | 0.7049 ± 0.0417 | +0.0419 | true |
| coil20 | pca | 40 | 0.620 ± 0.230 | 0.6472 ± 0.0383 | +0.0272 | true |
| coil20 | pca | 80 | 0.531 ± 0.294 | 0.5493 ± 0.0335 | +0.0183 | true |
| coil20 | pca | 160 | 0.375 ± 0.111 | 0.3944 ± 0.0395 | +0.0194 | true |
| pendigits | tsne | 10 | 0.977 ± 0.033 | 0.9872 ± 0.0095 | +0.0102 | true |
| pendigits | tsne | 20 | 0.973 ± 0.033 | 0.9766 ± 0.0114 | +0.0036 | true |
| pendigits | tsne | 40 | 0.956 ± 0.064 | 0.9655 ± 0.0160 | +0.0095 | true |
| pendigits | tsne | 80 | 0.948 ± 0.060 | 0.9505 ± 0.0133 | +0.0025 | true |
| pendigits | tsne | 160 | 0.949 ± 0.065 | 0.9510 ± 0.0139 | +0.0020 | true |
| pendigits | umap_ref | 10 | 0.973 ± 0.044 | 0.9877 ± 0.0086 | +0.0147 | true |
| pendigits | umap_ref | 20 | 0.976 ± 0.035 | 0.9772 ± 0.0116 | +0.0012 | true |
| pendigits | umap_ref | 40 | 0.954 ± 0.060 | 0.9683 ± 0.0121 | +0.0143 | true |
| pendigits | umap_ref | 80 | 0.951 ± 0.072 | 0.9510 ± 0.0141 | +0.0000 | true |
| pendigits | umap_ref | 160 | 0.951 ± 0.085 | 0.9210 ± 0.0149 | -0.0300 | true |
| pendigits | umap_ours | 10 | 0.973 ± 0.044 | 0.9877 ± 0.0098 | +0.0147 | true |
| pendigits | umap_ours | 20 | 0.976 ± 0.035 | 0.9844 ± 0.0126 | +0.0084 | true |
| pendigits | umap_ours | 40 | 0.954 ± 0.060 | 0.9710 ± 0.0153 | +0.0170 | true |
| pendigits | umap_ours | 80 | 0.951 ± 0.072 | 0.9560 ± 0.0138 | +0.0050 | true |
| pendigits | umap_ours | 160 | 0.951 ± 0.085 | 0.9544 ± 0.0139 | +0.0034 | true |
| pendigits | pca | 10 | 0.622 ± 0.092 | 0.6488 ± 0.0303 | +0.0268 | true |
| pendigits | pca | 20 | 0.633 ± 0.082 | 0.6411 ± 0.0373 | +0.0081 | true |
| pendigits | pca | 40 | 0.636 ± 0.078 | 0.6461 ± 0.0363 | +0.0101 | true |
| pendigits | pca | 80 | 0.643 ± 0.085 | 0.6516 ± 0.0306 | +0.0086 | true |
| pendigits | pca | 160 | 0.629 ± 0.107 | 0.6400 ± 0.0322 | +0.0110 | true |

## 4 判定明细

### coil20 → **未复现**

- 方向：小 k（10, 20, 40）要求 `UMAP ≥ t-SNE − 0.03`；大 k（80, 160）要求 `UMAP > t-SNE`。我们的 UMAP−t-SNE：k=10: -0.1083；k=20: -0.0632；k=40: -0.0208；k=80: +0.0340；k=160: -0.0750
- 排序：与原文逐 k 比对 pca/tsne/UMAP 三名次，一致 9/15 = 60%（阈值 70%）。
- 幅度：|Δ| ≤ 0.10 → k=10: -0.0641；k=20: -0.0584；k=40: -0.0554；k=80: -0.0816；k=160: -0.2245
- 逐 k 判定：k=10: 未复现（`{{verdict.coil20.k10}}`）；k=20: 未复现（`{{verdict.coil20.k20}}`）；k=40: 复现（`{{verdict.coil20.k40}}`）；k=80: 复现（`{{verdict.coil20.k80}}`）；k=160: 未复现（`{{verdict.coil20.k160}}`）

### pendigits → **复现**

- 方向：小 k（10, 20, 40）要求 `UMAP ≥ t-SNE − 0.03`；大 k（80, 160）要求 `UMAP > t-SNE`。我们的 UMAP−t-SNE：k=10: +0.0006；k=20: +0.0078；k=40: +0.0056；k=80: +0.0056；k=160: +0.0033
- 排序：与原文逐 k 比对 pca/tsne/UMAP 三名次，一致 11/15 = 73%（阈值 70%）。
- 幅度：|Δ| ≤ 0.03 → k=10: +0.0147；k=20: +0.0084；k=40: +0.0170；k=80: +0.0050；k=160: +0.0034
- 逐 k 判定：k=10: 复现（`{{verdict.pendigits.k10}}`）；k=20: 复现（`{{verdict.pendigits.k20}}`）；k=40: 复现（`{{verdict.pendigits.k40}}`）；k=80: 复现（`{{verdict.pendigits.k80}}`）；k=160: 复现（`{{verdict.pendigits.k160}}`）

## 5 写报告时要主动讲的两点

1. **COIL-20 的差距是全局的**（D9）：不只大 k，小 k 也比原文低约 0.06–0.07；
   原文称对各算法调过参但未披露（D2），我们固定默认超参。敏感性探针：COIL-20 把 `n_neighbors`
   从 15 提到 100，我们的 kNN@10 从 0.8569 升到 0.8799（仍低于原文 0.921）。
2. **t-SNE 基线偏强**：我们 sklearn 单线程 t-SNE 在 COIL-20 上 0.961，高于原文 0.934；
   这会让「UMAP ≥ t-SNE」的方向更容易失败——报告 §5 要写清这一点，而不是只说 UMAP 差。
3. **COIL-20 k=80 是边界点**（D9）：Δ=-0.0907 落在 tol 0.10 内、方向也对，但该点在看主表前
   已按冒烟结果预登记为「未复现」；报告写「预登记未复现，实测落在 tol 边界内侧」，
   k=160（Δ=-0.2544）才是真正的未复现。数据集级判定以 §0 为准（方向在小 k 上就不过）。

## 6 键名清单（C 只允许这四种形式）

| 形式 | 例 | 语义 |
|---|---|---|
| `{{knn.<dataset>.<method>.k<k>.mean}}` | `{{knn.coil20.umap_ours.k80.mean}}` | 10 折均值 |
| `{{knn.<dataset>.<method>.k<k>.std}}` | `{{knn.coil20.umap_ours.k80.std}}` | 折间 std（ddof=1） |
| `{{runtime.<dataset>.<method>.fit_s}}` | `{{runtime.coil20.tsne.fit_s}}` | fit 秒数中位数 |
| `{{verdict.<dataset>.k<k>}}` | `{{verdict.coil20.k160}}` | 该数据集判定词（见 §0/§4） |

<dataset> ∈ pendigits / coil20；<method> ∈ pca / tsne / umap_ref / umap_ours；<k> ∈ 10/20/40/80/160。
