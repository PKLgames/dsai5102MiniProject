# 候选池可行性评估（2026-11-11）

> 依据：`selecting_exp.md` §5 检查表与评分卡；`for_next_round.md` §3 流程（候选池 → 核验 20 min/篇 → 1 h 冒烟）。
> 结论先行：**选定 UMAP（McInnes, Healy & Melville, arXiv:1802.03426, 2018）**；SHAP 为备选；其余 5 篇淘汰（理由见 §4）。

## 1. 方法与口径

- 评分卡权重：数据可得性 30 / 基准可实现性 20 / 评估口径明确 15 / 算力可行性 15 / 结论可讲性 10 / 年份 10。
  子项 0–5 分，加权分 = Σ(权重×子项)/5（满分 100）；**加权 < 70 不冒烟**。
- 一票否决：数据可得性 < 4；核心 baseline 缺失；论文 < 2010；**PDF 正文不可得（检查表第 1 项）**。
- 核验证据（PDF 已下载 + 抽文本，均在 `paper/`）：`umap_arxiv2018`、`shap_neurips2017`、`ncf_www2017`、
  `lightgbm_neurips2017`、`tabpfn_arxiv2207`、`gsmote_arxiv1709`。
- 数据落地点（实测，非推断）：PenDigits = `sklearn.datasets.load_digits()`（1797×64，与原文 8×8 灰度图一致）；
  COIL-20 = Columbia SLAM 压缩包（1440 张 128×128，解压后 1440 文件，已入 `data/raw/coil20/`）；
  Shuttle = OpenML did 40685（58,000×9）；MNIST = OpenML did 554（70,000×785）；Fashion-MNIST = OpenML did 40996（70,000×785）；
  OpenML-CC18 = study id 99（TabPFN 的 18 个数据集来源）；MovieLens 1M = `files.grouplens.org/datasets/movielens/ml-1m.zip`（HTTP 200，5.9 MB）。

## 2. 逐篇核验记录（检查表 9 项）

### 2.1 UMAP（arXiv:1802.03426, 2018，62 页，开放 PDF）

| 检查项 | 结果 |
|---|---|
| PDF 可取 | ✓ arXiv PDF（7.9 MB）+ 全文抽取 |
| 实验表含数据集与样本数 | ✓ Table 1/2/3 全列规模（1797×64 / 1440×16384 / 58000×9 / 70000×784 / …） |
| 数据集逐个可核 | ✓ 5 个有标签数据集 100% 可核（见 §1）；COIL-100 同源可下；Flow cytometry / GoogleNews / scRNA 仅用于 runtime，可作偏离 |
| baseline 可直接 import | △ t-SNE/PCA/Laplacian Eigenmaps 在 sklearn；**LargeVis 无 pip 包**（官方 C++/Java 实现），按偏离日志处理 |
| 核心主张 ≤4 条 | ✓（C1 定性可视化、C2 kNN 精度、C3 子采样稳定性、C4 运行时间） |
| 单配置 ≤30 min CPU | ✓ 实测 PenDigits 单次嵌入 ≤13 s、COIL-20 ≤18 s（见 §3） |
| 一张图讲直觉 | ✓ 嵌入散点对比即直觉 |
| ≥1 个自设扩展 | ✓ 可把原文 Fig.1–3 的“超参数定性图”改成定量 kNN 曲线（见 §5） |
| 年份双证 | ✓ 2018，arXiv 元数据 + 正文 |

风险：arXiv 预印本（无正式会议/期刊）；COIL-20 大 k 指标与原表有偏差（§3.2 已实测）；大规模数据集（70k×784）需子采样并写偏离。

### 2.2 SHAP（NeurIPS 2017, arXiv:1705.07874）

- ✓ PDF 可取；MNIST（OpenML 554）与合成树模型可用。
- ✗ 三条主张里 **5.2 是 Amazon Mechanical Turk 人因研究（30 人 / 52 人）**，不可复现；5.3 复用 DeepLIFT 预训练模型（TF1 时代代码，现代环境不可用）。
- ✗ Fig.3（KernelSHAP vs sampling vs LIME）的树模型训练数据与背景分布正文未给，只能自设。
- 结论：可复现的是“方法 + 效率实验”，核心“符合人类直觉”无法验证 → 完整性有硬缺口，列备选。

### 2.3 NCF（WWW 2017）

- ✓ PDF、MovieLens 1M 可取；BPR / ItemKNN 在 `implicit` 有现成实现。
- ✗ **eALS 无标准库实现**（论文最强 baseline），必须自写；leave-one-out + 4 负样本协议争议大（`selecting_exp.md` §2 #5 明示）。
- 评分因“核心 baseline 缺失”被压到 68 < 70，淘汰。

### 2.4 LightGBM（NeurIPS 2017）

- ✗ 实验数据为 LETOR 30K query、Allstate 12M、Flight Delay 10M、KDD10 19M×29M 特征、KDD12 119M×54M 特征；多数需 Kaggle 账号，且远超 7.5 GB 内存。
- 数据可得性 1 分（一票否决）。淘汰。

### 2.5 Geometric SMOTE（Inf. Sci. 2019；预印本 arXiv:1709.07377）

- ✓ PDF 可取；13 个 UCI 数据集全部可下；SMOTE/BorderlineSMOTE/ADASYN 在 imbalanced-learn。
- ✗ 无官方代码（上轮已核：作者 GitHub 404、PyPI 404、imbalanced-learn 无此类）。
- ✗ 评估协议 = 13 数据集 × 2 分类器 × 3 指标 × 5 次重复 × 网格搜索，**每格取网格内最高 CV 分**再算 Friedman 排名——口径重且易膨胀，复现成本高于其“小数据”表象。
- △ 与上一轮放弃的 SMOTE 同族，选题差异化弱。加权 71，仅过线，不推荐。

### 2.6 TabPFN（Nature 2025；ICLR 2023 版 arXiv:2207.03778）

- ✓ 18 个 OpenML-CC18 数据集 API 可取，评估口径清楚（5 splits、ROC AUC OVO）。
- ✗ 核心方法需 **8 GPU × 20 h 预训练**，本机无 GPU → 只能“使用官方权重”，不构成复现。
- ✗ flagship 主张“与 AutoML 持平 + 230× 加速”需每数据集 1 h AutoML（AutoGluon/Auto-sklearn），18 数据集 × 多预算，10 天内不可行。
- 加权 80，但按“复现而非使用”原则判为不可复现，降为备选/扩展对照。

### 2.7 HDBSCAN（PAKDD 2013；扩展版 **ACM TKDD 10(1), 2015, DOI 10.1145/2733381**，非 JMLR）

- ✗ **正文 PDF 不可得**：Semantic Scholar `CLOSED`、OpenAlex `is_oa: false`、JCU 仓库 PDF 返回 401（页面写明 `Restricted to Repository staff only`）、ACM DL 与 Springer 均为拦截页、arXiv 无此文。手稿记的“JMLR 2015”是错的，需更正。
- 无法核对实验数据集与样本数 → 检查表第 1 项不通过，一票否决（若组内有 ACM DL 权限可重议，但 11-12 前拿不到就放弃）。

## 3. 冒烟测试（UMAP，1 h 预算内完成）

脚本：`scripts/smoke_umap.py`（结果 JSON 在 `results/smoke_umap/`）。协议照原文：先嵌入到 2 维，再在嵌入空间做
kNN 分类（k∈{10,20,40,80,160}），分层 10 折交叉验证取均值±标准差。嵌入用 **参考实现 umap-learn 0.6.0**（冒烟目的是验证数据+口径+耗时，不是自研实现）。
t-SNE 用 sklearn（原文用 MulticoreTSNE），单核，`random_state=42`，perplexity=30，1000 iter；UMAP `n_neighbors=15, min_dist=0.1`。

### 3.1 PenDigits（1797×64，10 类）—— 方向与绝对值均复现

| k | 原文 PCA | 本次 PCA | 原文 t-SNE | 本次 t-SNE | 原文 UMAP | 本次 UMAP |
|---|---|---|---|---|---|---|
| 10 | 0.622 | 0.649 | 0.977 | 0.987 | 0.973 | 0.988 |
| 20 | 0.633 | 0.641 | 0.973 | 0.977 | 0.976 | 0.977 |
| 40 | 0.636 | 0.646 | 0.956 | 0.965 | 0.954 | 0.968 |
| 80 | 0.643 | 0.652 | 0.948 | 0.950 | 0.951 | 0.951 |
| 160 | 0.629 | 0.640 | 0.949 | 0.951 | 0.951 | 0.921 |

结论：三条曲线形状一致（UMAP≈t-SNE≫PCA），|Δ|≤0.03（仅 k=160 的 UMAP 低 0.03）。**该数据集可作主表。**

### 3.2 COIL-20（1440×16384，20 类）—— 小 k 一致，大 k 未复现原文优势

| k | 原文 PCA | 本次 PCA | 原文 t-SNE | 本次 t-SNE | 原文 UMAP | 本次 UMAP |
|---|---|---|---|---|---|---|
| 10 | 0.667 | 0.720 | 0.934 | 0.958 | 0.921 | 0.860 |
| 20 | 0.663 | 0.697 | 0.901 | 0.908 | 0.907 | 0.853 |
| 40 | 0.620 | 0.648 | 0.857 | 0.866 | 0.904 | 0.844 |
| 80 | 0.531 | 0.552 | 0.789 | 0.765 | 0.899 | 0.806 |
| 160 | 0.375 | 0.388 | 0.609 | 0.640 | **0.803** | **0.606** |

- 方向部分一致：k=80 时 UMAP>t-SNE（0.806 vs 0.765），与原文一致；但 k=160 时本次 UMAP 掉到 0.606，原文是 0.803。
- 已排查但**未能解释**的变量：像素除以 255（无变化）、`n_neighbors=30`（更差）、嵌入维度 3/10（无改善，0.59/0.56）。推测是 umap-learn 0.5→0.6 的默认管线变化（`compatibility_layout` 警告）与原文 2018 版实现差异。
- 处置：主表保留 COIL-20 但**只声明 k≤80 的结论**，k=160 写入偏离日志与讨论节（“复现差异分析”本身是 Methodology 得分点）。

### 3.3 耗时（单核，`NUMBA_NUM_THREADS=1`）

| 数据集 | 规模 | PCA | t-SNE(sklearn) | UMAP(umap-learn) |
|---|---|---|---|---|
| PenDigits | 1797×64 | 0.0 s | 10.8 s | 12.2 s |
| COIL-20 | 1440×16384 | 1.5 s | 9.5 s | 17.4 s |

原文 Table 3（3.1 GHz i7 单核）：PenDigits UMAP 9 s / t-SNE 17 s；COIL-20 UMAP 12 s / t-SNE 22 s。本机同量级。
→ 单配置成本 = 秒级；5 数据集 × 5 方法 × 5 个 k 的全表可在 1–2 h 内跑完，70k 数据集乘 20 折需子采样（偏离）。

## 4. 评分卡与排序

| 候选 | 数据(30) | 基准(20) | 口径(15) | 算力(15) | 可讲(10) | 年份(10) | 加权分 | 判定 |
|---|---|---|---|---|---|---|---|---|
| **UMAP** | 5 | 4 | 5 | 4 | 5 | 5 | **93** | ✅ 选定 |
| TabPFN | 5 | 3 | 4 | 2 | 5 | 5 | 80 | ✗ 只能“用权重”，非复现 |
| SHAP | 5 | 3 | 2 | 4 | 4 | 5 | 78 | 备选（人因研究不可复现） |
| Geometric SMOTE | 4 | 4 | 2 | 3 | 3 | 5 | 71 | ✗ 同族 + 无代码 + 网格口径 |
| HDBSCAN | 1 | 5 | 4 | 5 | 5 | 5 | 73 | ✗ 一票否决（PDF 不可得） |
| NCF | 4 | 2 | 3 | 3 | 4 | 5 | 68 | ✗ 核心 baseline eALS 缺失 |
| LightGBM | 1 | 3 | 4 | 1 | 5 | 5 | 53 | ✗ 数据/内存不可行 |

淘汰顺序与理由（对应 `selecting_exp.md` 的“换题信号”）：
1. LightGBM / HDBSCAN：数据或正文不可得（一票否决）。
2. NCF：核心 baseline 需自实现（eALS）+ 协议争议。
3. Geometric SMOTE：与上轮同族、无官方码、评估口径重且膨胀。
4. TabPFN：训练不可复现（8 GPU×20 h），只能跑官方权重。

## 5. 选定后的复现框架（UMAP）

**主张（≤4 条）**
- C1（定性）：2 维嵌入视觉质量与 t-SNE 相当，且更好保留全局结构（原文 Fig.4，MNIST/F-MNIST/COIL-20）。
- C2（定量，主）：嵌入空间 kNN 精度 UMAP≈t-SNE/LargeVis（小 k），大 k 显著更好（Table 1/2）。
- C3（稳定性）：子采样下 normalized Procrustes distance 小于 t-SNE（原文 Fig.8）。
- C4（效率）：同等规模下运行时间低于 t-SNE/LargeVis（Table 3）。

**主表范围**：PenDigits、COIL-20（k≤80 结论）、Shuttle（58k×9）、MNIST / F-MNIST（子采样 + 减折，写偏离）。
**偏离日志（预登记）**：LargeVis 不跑（无 pip 实现，第三对照缺失，主表不砍）；t-SNE 用 sklearn 而非 MulticoreTSNE；
70k 数据集用 20k 子采样 × 5 折；COIL-20 k=160 不复现原文优势（已实测）；超参取参考实现默认值（原文未在正文列出）。

**自设扩展（Novelty 得分点）**：把原文 Fig.1–3 的“超参数定性图”改成定量曲线——在 PenDigits/COIL-20 上扫
`n_neighbors∈{5,10,15,30,50,100}` × `min_dist∈{0,0.1,0.5,0.8}`，用 kNN 精度（k=10/100/全部）画热力图，回答“局部/全局结构如何随超参变化”。
成本：约 40 次嵌入 × 秒级，1 h 内可完成，且是原文没有的定量结论。

**自研实现要求**：按 Algorithm 1/2/5 用 numpy 实现模糊单纯复形 + 谱初始化 + 负采样 SGD（a/b 由 min_dist 最小二乘拟合），
与 umap-learn 对照；等价判据初拟：PenDigits 上 kNN 精度与原文差 ≤0.03，且 UMAP≥t-SNE 在 k≤80 成立。

## 6. 下一步

1. `git checkout -b main-v2`（当前 main 只有交接文档与评估）。
2. `cp docs/TEMPLATE_PROTOCOL.md docs/PROTOCOL.md` 填写 §5 的主张/判据/矩阵/偏离。
3. 铺代码：`src/data.py`（load_digits / coil20 / openml shuttle,mnist,fmnist）、`src/umap_impl.py`、`scripts/run_table.py`。
4. 交 B：数据卡（5 数据集）+ EDA；交 C：报告骨架与 Fig.2/Fig.3 占位。
5. 时间锚点：11-12 选题定稿（本文件）；11-14 自研实现跑通 PenDigits；11-16 主表出数；11-18 扩展与敏感性；11-19 交 C。

## 附：核验过程的一次更正

`for_next_round.md` §7 把 HDBSCAN 扩展版记作 “JMLR 2015”。经 Crossref/OpenAlex 核实，正确出处是
**ACM Transactions on Knowledge Discovery from Data 10(1), 2015, DOI 10.1145/2733381**，标题
“Hierarchical Density Estimates for Data Clustering, Visualization, and Outlier Detection”；PAKDD 2013 版 DOI 10.1007/978-3-642-37456-2_14（LNCS pp.160–172）。
