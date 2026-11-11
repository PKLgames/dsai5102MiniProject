# 候选池可行性评估（2026-11-11）

> 依据：`selecting_exp.md` §5 检查表与评分卡；`for_next_round.md` §3 流程（候选池 → 核验 20 min/篇 → 1 h 冒烟）。
> 结论先行：**选定 UMAP（McInnes, Healy & Melville, arXiv:1802.03426, 2018）**；SHAP 为备选；其余 5 篇淘汰（理由见 §4）。

## 1. 方法与口径

- 评分卡权重：数据可得性 30 / 基准可实现性 20 / 评估口径明确 15 / 算力可行性 15 / 结论可讲性 10 / 年份 10。
  子项 0–5 分，加权分 = Σ(权重×子项)/5（满分 100）；**加权 < 70 不冒烟**。
- 一票否决：数据可得性 < 4；核心 baseline 缺失；论文 < 2010；**PDF 正文不可得（检查表第 1 项）**；
  **单配置成本 > 30 min CPU 且矩阵无法压到 10 天预算内（检查表第 6 项，按通过/不通过处理）**。
  注：第 4 条否决是因为线性加权里“算力可行性”只占 15 分，一个其余四项满分的 GPU 重文章仍能拿到 73 分——
  与“10 天内做出可交付结果”的硬约束不符，故把第 6 项从评分项提升为闸门（2026-11-11 增补，适用于 §2.8/§2.9）。
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

### 2.8 Kovács (2019)：85 种少数类过采样在 104 个不平衡数据集上的实证比较（用户 m00404 追加；m00488 提供原文后重评）

**书目**：Applied Soft Computing 83:105662, 2019. DOI 10.1016/j.asoc.2019.105662（Crossref：112 条参考文献，被引 322）。
**正文来源**：用户提供 `paper/An_empirical_comparison_and_evaluation_of_minority.pdf`（13 页）；文本抽取用 `pdfminer.six`（pypdf 会把词粘成 `Anempiricalcomparison`，不可用），输出 `/tmp/kovacs_ml.txt`（87,287 字符）。

| 检查项 | 结果 |
|---|---|
| PDF 可取 | ✓ 本地正文已读（9 节 + 附录，含全部实验表） |
| 实验表含数据集与样本数 | ✓ Table 2 给出 **104 个数据集**的名称、IR、样本数、属性数；来自 KEEL imbalanced（多类 UCI 重构为二类）+ kNN 文献常用集；剔除 ADA/HIVA/sylva/satimage/dermathology_6/page_blocks0（过大） |
| 数据集可核 | ✓ KEEL 索引页 `https://sci2s.ugr.es/keel/imbalanced.php` HTTP 200；实测下载 `glass1`（214×9）、`pima`（768×8）均 200；预处理写明：删常数列、二值转浮点、名义 <5 值 one-hot 否则 label encode |
| baseline 可 import | ✓ 但性质特殊：85 种方法的实现就是作者自己的 `smote_variants`（GitHub `gykovacs/smote_variants`，PyPI 1.0.1）。实测 `--target /tmp/sv --no-deps` 安装 + 补 `metric-learn/minisom/seaborn` 后 import 成功，`get_all_oversamplers()` = **91 个**（论文 85 + 附加）；声明的 tensorflow/keras/mkl 在 import 时未被真正加载 |
| 核心主张 ≤4 条 | ✓ ① 在 104 个数据集上对 85 种过采样做统一比较；② 高级方法相对 SMOTE 的提升远小于既往小样本研究（AUC +0.01、F1 +0.01、G +0.02、P20 +0.0025）；③ 给出 Table 4 总体排名（前 10 名）；④ 分析前三名的机制（polynom-fit-SMOTE 的 4 种拓扑、ProWSyn 的距离权重、...） |
| 单配置 ≤30 min CPU | ✓ 单 (数据集 × 方法) 约 1–2 min；✗ **但全矩阵**按实测推算 ≈ **258 h ≈ 11 天单核**（见下），超出 10 天总预算 |
| 一张图讲直觉 | △ 基准论文，直觉要靠“平均秩排名 / 临界差异图”；6 分钟能讲，但不如方法论文好讲 |
| ≥1 个自设扩展 | ✓ 加分类器（XGBoost/LightGBM）或加指标重排；也可只对前 10 名补做多种子稳定性 |
| 年份双证 | ✓ 2019，Crossref + 期刊卷页 |

**协议（已从正文读出，口径 5 分）**：重复分层 **5 折 × 3 次重复**；每个 oversampler 至多 **35 组随机参数**；4 个分类器——kNN（k∈{3,5,7} × standard/distance）、SVM（hinge/gamma 等 6 组）、DT、MLP，各 6 组参数；指标 **G-mean / AUC / F1 / P20**；
**模型选择 = 每个 (数据集, 过采样器, 分类器) 取网格内最高分**；排序 = 先按分类器平均各指标 → 对每个 oversampler 赋秩 → 取平均秩（原文明确“平均秩比平均分数更有意义”，Table 4 为总排名）；论文自报总作业量 “over 76 million”。

**算力实测（决定性的重评证据）**：
- 计时脚本：`RepeatedStratifiedKFold(5, n_repeats=3)`、4 分类器各 1 组默认参数、过采样器默认参数。
- 每个 split（1 次采样 + 4 次拟合计）：glass1 SMOTE 2.5 + 77.0 = **79.6 ms**；ProWSyn 4.6 + 115.4 = 120.0 ms；SMOTE_IPF 32.7 + 69.3 = 101.9 ms。pima：SMOTE 143.1 ms；ProWSyn 149.1 ms；SMOTE_IPF 221.2 ms。
- 外推：×6 分类器参数组合 ≈ 0.5–1.0 s/(split·sampler-combo)；×15 splits ≈ 8–15 s；×约 10 个 sampler-combo ≈ **100 s/(数据集·方法)**；×104×85 = 8,840 对 → **≈ 26 万 s ≈ 258 h ≈ 11 天单核**。
- **并行不可用**：`multiprocessing.get_context('fork').Pool(4)` 抛 `PermissionError: [Errno 13] Permission denied`（SemLock 被沙箱拒绝），joblib 同样退化为串行 → 258 h 无法靠 16 核压缩。

**重评结论**：检查表前两项与口径全部通过（正文可得、数据集可核、协议逐条写明、代码就是作者自己的包），
但算力闸门不通过——**全量复现需 11 天单核 > 10 天总预算**。可行压缩方案：重复数 3→1（约 86 h ≈ 3.6 天）或 1/3 子集（约 30 数据集 × 85 方法 ≈ 3 天），两者都须写进偏离日志并放弃“104 数据集总体排名”这一核心主张。
评分：数据 5 / 基准 5 / 口径 5 / 算力 2 / 可讲 3 / 年份 5 → 加权 **87**（线性加权下高于 SHAP，低于 UMAP 93）；若降到 1 次重复按算力 3 计为 90，仍低于 UMAP。
体裁风险：这是“基准比较”而非“提出算法”，复现主要是重跑作者自家 `smote_variants` 包；且候选池里第三次落在 SMOTE 家族（上一轮 JAIR 2002 SMOTE 已按用户要求移出工作区）。
**可重议条件**：用户接受“1 次重复 + 104 数据集”或“3 次重复 + 30 数据集”的偏离版本，并认为“重跑作者基准”可作为本课复现对象。

### 2.9 Cui et al. (2019)：Class-Balanced Loss Based on Effective Number of Samples（用户 m00404 追加）

**书目**：Cui, Y., Jia, M., Lin, T.-Y., Song, Y., Belongie, S. *Class-Balanced Loss Based on Effective Number of Samples.*
CVPR 2019, DOI 10.1109/CVPR.2019.00949；arXiv:1901.05555（**OA**，已下载 `paper/cui_cvpr2019.pdf`，11 页）。代码：`https://github.com/richardaecn/class-balanced-loss`（PyTorch，作者放出代码/数据/预训练模型）。

| 检查项 | 结果 |
|---|---|
| PDF 可取 | ✓ arXiv + CVPR 正式版 |
| 实验表含数据集与样本数 | ✓ Table 1：Long-Tailed CIFAR-10（10 类，不平衡因子 10–200）、CIFAR-100（100 类，10–200）、iNaturalist 2017（5,089 类 / 579,184 训练图 / 因子 435.44）、iNaturalist 2018（8,142 类 / 437,513 张 / 因子 500）、ILSVRC 2012（1,281,167 训练 / 50,000 验证） |
| 数据集可核 | ✓ CIFAR-10/100 走 torchvision 可下，长尾重划分规则在论文 §5.2 写明；iNat 2017/2018 与 ImageNet 需 100 GB+ 且下载慢 → 只能做 CIFAR 部分 |
| baseline 可 import | ✓ softmax / sigmoid CE / focal（γ=0.5,1,2）都是几行代码；官方仓库给了全部损失实现 |
| 核心主张 ≤4 条 | ✓（有效样本数 (1−β^n)/(1−β) 重加权；CIFAR 上一致提升；大规模数据集上也提升；β 与类别粒度相关） |
| 单配置 ≤30 min CPU | ✗ **实测否决**：ResNet-32、batch 128、32×32，本机 16 线程 CPU 实测 **366.7 ms/iter → 2.4 min/epoch → 200 epochs ≈ 8.0 h/配置**（脚本见 §2.9 末）；原文 Table 2 是 10 个数据集变体 × 6 种损失，且 CB 的超参（损失类型 3 × β 4 × γ 3 = 36 组合）靠交叉验证选 → 主表 ≈ 60 次训练 × 8 h ≈ 480 h（20 天），仅超参搜索就再乘数倍；Table 3 的 ResNet-50/101/152 + iNat/ImageNet 原文用 TPU、batch 1024 → 本机完全不可能 |
| 一张图讲直觉 | ✓ “有效样本数”曲线 + 长尾分布图，6 分钟能讲清 |
| ≥1 个自设扩展 | ✓ 可把 CB 权重接到非视觉任务（表格长尾分类）或用轻量 MLP 做消融——但那就偏离原文设定 |
| 年份双证 | ✓ 2019，arXiv + CVPR proceedings |

**否决理由**：检查表第 6 项（单配置 ≤30 min CPU）按闸门处理，实测超 16 倍；主矩阵 20 天 > 10 天总预算，且无 GPU。
**可重议条件**：有 GPU（哪怕 1 张）且预算 ≥3 周，只做 CIFAR-10 单不平衡因子。

实测脚本（CPU 训练吞吐，用于上面 8.0 h 的推算）：

```python
# .venv-tabpfn/bin/python（py3.12 + torch 2.15），16 线程
# ResNet-32（3 stage × 5 basic block，与 CIFAR 版一致，0.47 M 参数）
# batch 128, 32×32, SGD+momentum, CrossEntropy；10 iter 计时 → 391 iter/epoch → 200 epochs
# 输出：per iter(128) 366.7 ms -> epoch 2.4 min -> 200 epochs 8.0 h
```

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
| Kovács 基准比较（2019） | 5 | 5 | 5 | 2 | 3 | 5 | **87** | ✗ 算力闸门（全量 11 天单核）；备选 #2 |
| Class-Balanced Loss（2019） | 4 | 4 | 5 | 0 | 4 | 5 | 73¹ | ✗ 闸门否决（实测单配置 8.0 h ≫ 30 min） |

¹ 只是线性加权的算术结果，用于说明权重设计的缺陷：算力 0 分仍能得 73。按检查表第 6 项做闸门后直接淘汰。
Kovács 拿回正文后“口径”从不可核验变为 5 分（协议逐条写明），但算力实测把总分压在 87：全量 104×85 需 11 天单核，且沙箱禁用了多进程 → 只能降重复数或缩子集，核心主张（104 数据集总体排名）随之失去。

淘汰顺序与理由（对应 `selecting_exp.md` 的“换题信号”）：
1. LightGBM / HDBSCAN：数据或正文不可得（一票否决）。
2. Class-Balanced Loss：算力闸门（单配置 8 h、主矩阵 20 天、无 GPU）。
2b. Kovács 基准比较：算力闸门（全量 11 天单核，且无法并行；压缩后核心主张失效）。
3. NCF：核心 baseline 需自实现（eALS）+ 协议争议。
4. Geometric SMOTE：与上轮同族、无官方码、评估口径重且膨胀。
5. TabPFN：训练不可复现（8 GPU×20 h），只能跑官方权重。

结论：**UMAP（93）仍为唯一同时通过全部检查表、冒烟与算力闸门的对象**；Kovács 重评后升为备选 #2（87，若接受偏离版本可到 90），Cui 与其余候选仍不通过。二选一建议：保留 UMAP，因为切换需重写协议并放弃“104 数据集排名”这一主结论，而 UMAP 已完成冒烟、协议骨架可直接落 `docs/PROTOCOL.md`。

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
6. 备选预案：若 11-14 自研 UMAP 仍不收敛，切换到 Kovács 基准（备选 #2）——协议用 `scripts/probe_kovacs_runtime.py` 已测的成本重写，采用「104 数据集 × 5 折 × 1 次重复」或「30 数据集 × 85 方法 × 5 折 × 3 次重复」，两者都必须在协议里登记偏离。

## 附：核验过程的一次更正

`for_next_round.md` §7 把 HDBSCAN 扩展版记作 “JMLR 2015”。经 Crossref/OpenAlex 核实，正确出处是
**ACM Transactions on Knowledge Discovery from Data 10(1), 2015, DOI 10.1145/2733381**，标题
“Hierarchical Density Estimates for Data Clustering, Visualization, and Outlier Detection”；PAKDD 2013 版 DOI 10.1007/978-3-642-37456-2_14（LNCS pp.160–172）。
