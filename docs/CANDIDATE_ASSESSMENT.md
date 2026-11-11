# 选题评估：候选池筛选 → 选定 UMAP（2026-11-11）

**结论**：复现对象定为 **UMAP**（McInnes, Healy & Melville, *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction*, arXiv:1802.03426, 2018）。
它在候选池里唯一同时通过 9 项核验、1 小时冒烟与算力闸门（加权 93）。本文只保留筛选理由与 UMAP 相关证据；
其他候选各留一句话否决理由（§2），逐篇详细核验表已按用户要求删除。

原文与抽取文本：`paper/umap_arxiv2018.pdf`、`paper/umap_arxiv2018.txt`（63 页，已通读 §1–§5 与 Algorithm 1/2/5）。

## 1. 筛选口径（沿用 `selecting_exp.md`）

| 维度 | 权重 | 判据 |
|---|---|---|
| 数据可得性 | 30 | 一票否决 <4：数据集必须能自行下载并核到样本数 |
| 基准可实现性 | 20 | 核心 baseline 缺失即淘汰 |
| 评估口径明确 | 15 | 必须能三行代码复算；整条 ROC/凸包/网格取最高分这类口径视为高风险 |
| 算力可行性 | 15 | 单配置 ≤30 min CPU，全矩阵 ≤10 天；**实测超 30 min 且无法压缩 → 闸门否决** |
| 结论可讲性 | 10 | 6 分钟能讲清直觉 |
| 年份 | 10 | 2010 至今（用户 2026-11-11 放宽） |

流程：列候选池 → 逐篇 9 项核验（PDF、实验表、数据集、baseline、主张、单配置耗时、直觉图、扩展、年份）→
**加权 ≥70 才允许冒烟** → 1 小时冒烟（单数据集 × 2 条件，看方向是否与原文一致）→ 写 `docs/PROTOCOL.md`。

## 2. 其他候选为什么被否（按淘汰顺序，各一句话）

| 候选 | 年份 | 加权 | 否决理由 |
|---|---|---|---|
| HDBSCAN | 2013/2015 | 73 | 正文 PDF 全渠道不可得（ACM TKDD / Springer / JCU 仓库 401，无 arXiv），协议无法核对 → 一票否决；顺带更正：扩展版不是 JMLR 2015，而是 **ACM TKDD 10(1), 2015, DOI 10.1145/2733381** |
| LightGBM | 2017 | 53 | 原文实验是 LETOR/Allstate/KDD10 19M×29M/KDD12 119M×54M 特征，多需 Kaggle 账号，7.5 GB 内存不可行 |
| NCF | 2017 | 68 | 核心 baseline **eALS 无标准库实现**；leave-one-out + 4 负样本协议有争议 |
| Geometric SMOTE | 2019 | 71 | 无官方代码；13 数据集 ×「网格内取最高 CV 分」口径膨胀；且与上一轮 SMOTE 同族 |
| SHAP | 2017 | 78 | 核心主张依赖 Mechanical Turk 人因研究（不可复现）；§5.3 需 TF1 时代 DeepLIFT 预训练模型；Fig.3 背景数据正文未给 |
| TabPFN | 2023/2025 | 80 | 本体需 8 GPU×20 h 预训练 → 只能「使用官方权重」而非复现；flagship「打败 AutoML」需每数据集 1 h AutoML 预算 |
| Class-Balanced Loss | 2019 | — | 算力闸门：ResNet-32 CPU 实测 366.7 ms/iter → 200 epochs ≈ **8.0 h/配置**，主表约 20 天，无 GPU |
| Kovács 过采样基准比较 | 2019 | 87 | 协议可读、`smote_variants` 可跑，但全量 104 数据集 × 85 方法外推 ≈**258 h ≈ 11 天单核**（多进程被沙箱拒绝）→ 算力闸门；列为备选 #2 |

共同教训：**先核 PDF 与单配置耗时，再读实验表**。HDBSCAN 与 Kovács 都在「正文拿不到」上耗了一轮；Cui 在「GPU 缺失」上被判死。

## 3. UMAP 核验（9 项）

**书目**：被复现对象 = McInnes, L., Healy, J., & Melville, J. (2018). *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction*. arXiv:1802.03426 [stat.ML]，DOI `10.48550/arXiv.1802.03426`，63 页预印本（无正式会议/期刊版本，年份合规）。
配套文献（**不是**被复现对象）= Healy, J., & McInnes, L. (2024). *Uniform manifold approximation and projection*. Nature Reviews Methods Primers **4**:82，DOI `10.1038/s43586-024-00363-x`，15 页；属教程性 Primer，不含新实验，只用于交叉核对默认超参（其 Table 1：n_neighbours=15、min_dist=0.1、n_components=2、metric=Euclidean、output_metric=Euclidean、unique=False、init=spectral，与 §5 D2 采用的默认值一致）与结果解读注意事项。

| 检查项 | 结果 |
|---|---|
| PDF 可取 | ✓ arXiv 开放，全文与算法伪代码完整 |
| 实验表含数据集与样本数 | ✓ Table 1/2/3 给出 9 个数据集：PenDigits 1797×64、COIL-20 1440×16384、COIL-100 7200×49152、Mouse scRNA 20,921×26,774、Shuttle 58,000×9、MNIST 70,000×784、Fashion-MNIST 70,000×784、Flow cytometry 1,000,000×17、GoogleNews 3M×300 |
| 数据集可核 | ✓ PenDigits = `sklearn.datasets.load_digits()` 1797×64（注意不是 OpenML pendigits did=32 的 10,992 条）；COIL-20 可从 Columbia `https://www.cs.columbia.edu/CAVE/databases/SLAM_coil-20_coil-100/coil-20/coil-20-proc.zip` 下载（12.7 MB，1440 张 128×128 PNG，已解压到 `data/raw/coil20/coil-20-proc/`）；Shuttle = OpenML did 40685；MNIST = did 554；Fashion-MNIST = did 40996 |
| 核心 baseline 可 import | ✓ PCA / t-SNE / Laplacian Eigenmaps 在 sklearn；LargeVis 无 pip 实现 → 不跑（写偏离，主表不砍其他对照） |
| 核心主张 ≤4 条 | ✓ C1 视觉质量、C2 kNN 精度、C3 Procrustes 稳定性、C4 运行时间（见 §6） |
| 单配置 ≤30 min CPU | ✓ 单次嵌入秒级（冒烟实测：PenDigits t-SNE 10.8 s / UMAP 12.2 s；COIL-20 9.5 s / 17.4 s） |
| 一张图讲直觉 | ✓ 模糊单纯复形 → 低维布局，一页能讲完 |
| ≥1 个自设扩展 | ✓ 把原文 Fig.1–3 的超参定性图改成定量热力图（§6） |
| 年份双证 | ✓ 2018，arXiv 元数据 + 引文 |

**唯一未解风险**：原文用 MulticoreTSNE/FIt-SNE 版 t-SNE 与 LargeVis 官方实现，本机用 sklearn t-SNE；k=160 的 COIL-20 优势未复现（见 §4），已预登记为偏离。

## 4. 冒烟结果（1 小时预算内完成）

脚本 `scripts/smoke_umap.py`：PCA(2) / t-SNE(perplexity=30, init='pca', lr='auto', 1000 iter) / UMAP(n_neighbors=15, min_dist=0.1)，
评估 = 嵌入空间 kNN 分类精度，StratifiedKFold(10, seed 42)，k∈{10,20,40,80,160}；结果 `results/smoke_umap/{digits,coil20}.json`。
运行需 `NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1`。

**PenDigits（1797×64）——方向与绝对值均复现（|Δ|≤0.03）**

| k | PCA（本次/原文） | t-SNE（本次/原文） | UMAP（本次/原文） |
|---|---|---|---|
| 10 | .649 / .622 | .987 / .977 | .988 / .973 |
| 40 | .646 / .636 | .965 / .956 | .968 / .954 |
| 160 | .640 / .629 | .951 / .949 | .921 / .951 |

**COIL-20（1440×16384）——小 k 一致，k=160 未复现**

| k | PCA | t-SNE | UMAP |
|---|---|---|---|
| 10 | .720 / .667 | .958 / .934 | .860 / .921 |
| 80 | .552 / .531 | .765 / .789 | **.806 / .899** |
| 160 | .388 / .375 | .640 / .609 | **.606 / .803** |

差异归因（已排查）：像素归一化、n_neighbors=30、嵌入维度 3/10 都不能解释；怀疑 umap-learn 0.5→0.6 的管线变化
（`compatibility_layout` 警告）+ 原文 2018 实现差异；原文 COIL-20 标准差高达 ±0.115（本次 ±0.014），说明原文分折细节未写明。

**处置**：主表保留 COIL-20，但只声明 k≤80 的结论；k=160 写进偏离日志，作为报告 Discussion 的「复现差异分析」得分点。

## 5. 评分卡

| 维度 | 数据 | 基准 | 口径 | 算力 | 可讲 | 年份 | 加权 |
|---|---|---|---|---|---|---|---|
| 得分 | 5 | 4 | 5 | 4 | 5 | 5 | **93** |

口径可三行复算（嵌入 → kNN → 10 折精度），这是 UMAP 相对基准类论文的最大优势。

## 6. 选定后的复现框架

**主张（≤4 条）**
- C1 定性：2 维嵌入视觉质量与 t-SNE 相当，更好保留全局结构（原文 Fig.4）。
- C2 定量（主）：嵌入空间 kNN 精度 UMAP ≈ t-SNE/LargeVis（小 k），大 k 显著更好（Table 1/2）。
- C3 稳定性：子采样下 normalized Procrustes distance 小于 t-SNE（原文 Fig.8）。
- C4 效率：同规模运行时间低于 t-SNE/LargeVis（Table 3）。

**主表范围**：PenDigits、COIL-20（k≤80 结论）、Shuttle（58k×9）、MNIST / Fashion-MNIST（子采样 + 减折）。
**偏离日志（预登记）**：LargeVis 不跑；t-SNE 用 sklearn 而非 MulticoreTSNE；70k 数据集用 20k 子采样 × 5 折；
COIL-20 k=160 不复现原文优势；超参取参考实现默认值（原文正文未列出 n_neighbors=15 / n_epochs=500 / min_dist=0.1）。

**自设扩展（Novelty）**：把原文 Fig.1–3 的「超参数定性图」改成定量曲线——PenDigits/COIL-20 上扫
`n_neighbors∈{5,10,15,30,50,100}` × `min_dist∈{0,0.1,0.5,0.8}`，用 kNN 精度（k=10/100/全部）画热力图，
回答「局部/全局结构如何随超参变化」。成本约 40 次嵌入 × 秒级。

**自研实现要求**：按 Algorithm 1/2/5 用 numpy 实现模糊单纯复形 + 谱初始化 + 负采样 SGD（Φ=(1+a‖x−y‖^{2b})^−1，a/b 由 min_dist 曲线最小二乘拟合），
与 umap-learn 对照；等价判据初拟：PenDigits 上 kNN 精度与原文差 ≤0.03，且 k≤80 时 UMAP ≥ t-SNE。

## 7. 下一步

1. ~~`git checkout -b main-v2`~~（已过时：2026-11-11 起只在 `main` / `main` + 短命分支上工作）。
2. `cp docs/TEMPLATE_PROTOCOL.md docs/PROTOCOL.md`，填 C1–C4、等价判据、矩阵、偏离日志。
3. 铺代码：`src/data.py`（load_digits / coil20 / openml shuttle,mnist,fmnist）、`src/umap_impl.py`、`scripts/run_table.py`。
4. 交 B：5 个数据集的数据卡 + EDA；交 C：报告骨架与 Fig.2/Fig.3 占位。
5. 时间锚点（**已被 `PLAN.md` v2 两日核心计划取代**，见其 §2 交付点 P1–P9；范围已缩到只复现 C2 = `DEVIATIONS` D18）：以下为 2026-11-11 的旧锚点，仅存档——11-12 选题定稿；11-14 自研实现跑通 PenDigits；11-16 主表出数；11-18 扩展与敏感性；11-19 交 C。

**备选预案**：若 11-14 自研实现仍不收敛，改做 Kovács 过采样基准（备选 #2），采用「104 数据集 × 5 折 × 1 次重复」或
「30 数据集 × 85 方法 × 5 折 × 3 次重复」，两者都须登记为偏离。
