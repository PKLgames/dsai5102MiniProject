# 复现协议 · UMAP（arXiv:1802.03426）

> 状态：**v1 冻结于 2026-11-11**，冻结后任何改动必须写进 `docs/DEVIATIONS.md` 并注明"事后修改"。
> 作者：A 起草，B/C 已知会。
> 目的：把"复现论文"变成可判定的问题——先说清做什么、怎么算、多接近算复现，再写代码。**先协议后代码**是 `selecting_exp.md` 里最贵的一条教训。

---

## 1. 论文与复现目标

McInnes, L., Healy, J., & Melville, J. (2018). *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction*. arXiv:1802.03426 [stat.ML]. 63 页，预印本（无正式会议/期刊版）。

论文的实证部分只有 4 个可复现主张，逐条编号如下（C = Claim）。表里"原文证据"是可以逐字核对的锚点，`docs/PAPER_NUMBERS.md` 存了全部数字。

| ID | 主张（原文措辞的直译） | 原文证据 | 我们的复现实验 |
|---|---|---|---|
| **C1** | 降到 2–3 维时，UMAP 嵌入的**视觉质量**与 t-SNE 可比：区分出同样的结构，且保留了更多全局结构 | §5.1、Fig.4（COIL-20 / MNIST / Fashion-MNIST / GoogleNews） | E1 定性网格图（5 数据集 × 4 方法，2 维），三人盲评 + 2D silhouette 作辅助证据 |
| **C2** | 在嵌入空间上训 kNN 分类器：k=10–40 时 UMAP 至少不差于 t-SNE / LargeVis；**大 k 时更好**（COIL-20 k=80/160、Shuttle k=800/3200 显著；MNIST k=1600/3200 有证据；Fashion-MNIST 小 k 更差、k=1600/3200 相当） | §5.2、Table 1/2、Fig.5/6 | E2 主表：5 数据集 × {PCA, LE, t-SNE, UMAP-ours, UMAP-ref} × k 网格，逐折记录 |
| **C3** | 子采样下 UMAP 嵌入**比 t-SNE 稳定**：归一化 Procrustes 距离更小；5% 子采样时 UMAP 的每点误差已低于 t-SNE 的任何取值 | §5.3、Fig.7/8（Flow Cytometry 1M×17） | E3 稳定性：Shuttle（替代 Flow）+ COIL-20，子采样 {5%,10%,25%,50%} × {t-SNE, UMAP-ours, UMAP-ref} × 3 seed |
| **C4** | 运行时间**普遍快于**其他方法（除 PenDigits 上 LE/Isomap 略快） | §5.4、Table 3 | E4 计时：5 数据集 × {PCA, LE, t-SNE, UMAP-ours, UMAP-ref}，3 次取中位数 |

**复现边界（重要）**：C2/C3/C4 的原始数字都来自作者机器（MacBook Pro i7 3.1 GHz / 8 GB；MulticoreTSNE 的 C++ 实现）。我们只能复现**方向与排序**，绝对数值按 §5.2 的容差判定。

## 2. 不做什么（Explicit non-goals）

| 不做 | 原因 | 在报告中的处理 |
|---|---|---|
| 不跑 LargeVis | 无 Python 3.14 可用轮子，且原实现需自编译；Table 1/2 中它的位置与 t-SNE 高度重合 | 表格中保留原文 LargeVis 列（标注"引自原文"），我们的列留空 |
| 不自研 t-SNE / FIt-SNE / MulticoreTSNE | 复现 UMAP 不需要重写别人的优化器；时间应花在算法 1–5 上 | 用 sklearn 的 Barnes-Hut t-SNE，并在讨论中说明"单一实现"的局限 |
| 不复现 COIL-100 / scRNA / Flow Cytometry / GoogleNews | 数据量超出本机（1M×17、300 万×300），且这些数据集只出现在 Table 3 与 Fig.8 | C3 用 Shuttle 替代 Flow（同为"大 n、低 d"，见偏离 D4） |
| 不实现 `transform` / 增量嵌入 | 论文主张里没有它 | — |
| 不复算拓扑/范畴论推导（§2–3） | 报告第 2 节只做综述式说明 | §2 引用原文定理，不重证 |
| 不调参到"论文的最优" | 原文说"Where possible we attempted to tune parameters"，但**未披露各算法具体取值** | 全部方法使用固定默认超参；在偏离日志 D2 写明，并在讨论中分析其影响 |

## 3. 数据

### 3.1 数据集表

`n/d` 为原文口径。"实测"列在 B 的 H1 交接后由 A 核验填实（§5 交接标准）。

| 数据集 | 原文 n × d | 实测 n × d | 用途 | 来源（唯一指定） | 备注 |
|---|---|---|---|---|---|
| PenDigits | 1797 × 64 | 1797 × 64 ✅ | C2（小 k）、C4 | `sklearn.datasets.load_digits()` | 8×8 灰度，像素 0–16；**不是** OpenML did=32 的 10992 条版本 |
| COIL-20 | 1440 × 16384 | 1440 × 16384 ✅ | C1、C2、C3、C4 | `https://www.cs.columbia.edu/CAVE/databases/SLAM_coil-20_coil-100/coil-20/coil-20-proc.zip`（已在 `data/raw/coil20/`） | 128×128 PNG，20 类 × 72 张，命名 `objK__NN.png` |
| Shuttle | 58000 × 9 | 待 H1 | C2、C3（替代 Flow）、C4 | OpenML `data_id=40685` | 7 类，类别极不平衡（~80% 类 1） |
| MNIST | 70000 × 784 | 待 H1（应 70000） | C1、C2、C4 | OpenML `data_id=554` | 用 §3.4 的 20k 子采样跑 C2 |
| Fashion-MNIST | 70000 × 784 | 待 H1（应 70000） | C1、C2、C4 | OpenML `data_id=40996` | 同上 |

距离：全部欧氏距离（原文对 GoogleNews 才用余弦，我们不跑该数据集）。

### 3.2 规范预处理决策（B 必须照此实现，A 会逐条核验）

| 编号 | 决策 | 理由（必须写进数据卡） |
|---|---|---|
| P1 | `X: float32 (n, d)`，C 序连续；`y: int64 (n,)`，**类别按首次出现的排序**编码为 0..K−1 | 与 `sklearn` 的 `LabelEncoder` 一致，跨脚本可比 |
| P2 | **不做特征缩放 / 标准化**（COIL-20 仅 `/255` 落到 [0,1]，MNIST 已 0–255 亦仅 `/255`） | UMAP 的模糊图对**均匀缩放不变**：σ、ρ 同比缩放，exp(−(d−ρ)/σ) 不变；a、b 只依赖 `min_dist`。因此缩放对 UMAP 是无操作，对其他方法也只缩放坐标系。为避免"预处理差异"被误当成算法差异，**全组统一** |
| P3 | 图像展平顺序：`(28,28)`/`(128,128)` 行优先展平，不做转置 | 与原文"treated as 784/16384 dimensional vectors"一致 |
| P4 | 保留全部行，**不去重**；重复行数只统计并写入 manifest | 去重会改变 n，破坏与原文计数对齐 |
| P5 | 缺失/NaN：任何一列出现 NaN/inf 立即 fail，不允许填补 | 这 5 个数据集不应有缺失；出现即说明 loader 有 bug |
| P6 | 落盘 `data/processed/{name}.npz`，键名固定 `X`、`y`；`np.savez_compressed` | 单文件、无 pickle 风险、可 mmap |
| P7 | manifest 的 `array_sha256` = `sha256(X.float32 C 序字节 + y.int64 字节)` | **不能用 npz 文件哈希**：zip 头含时间戳，字节不稳定；数组内容哈希才可重放 |
| P8 | 时间戳统一 UTC ISO8601；不写本地时区 | 跨机交接可读 |

### 3.3 硬校验（loader 返回前必须 assert，失败即抛错）

1. `X.shape == (n, d)`、`y.shape == (n,)`、`X.dtype == float32`、`y.dtype == int64`；
2. `n` 与原文计数一致（见 §5 容差表；COIL-20/PenDigits 必须精确相等）；
3. `np.isfinite(X).all()`；
4. `set(y) == {0..K-1}` 且每类样本数 ≥ max(k 网格中的 k) 候选（折内 train 侧）；
5. `label_map` 覆盖全部类别；
6. `X.min() >= 0`、`X.max() <= 1.0 + 1e-6`（P2 之后）；
7. manifest 六项统计（n/d/类数/类计数/NaN 数/重复行数）与数组实测一致。

### 3.4 划分与子采样

- **折数**：PenDigits、COIL-20、Shuttle = **10 折**（同原文）；MNIST/FMNIST 在 20k 子采样上 = **5 折**。
  - 为什么不是原文的 20 折：20 折时测试集只有 1000 点，而 k 网格含 k=3200 → kNN 无法训练（k > 测试集规模，原文 70k/20 折 = 3500 测试点刚好够）。20k 下 k=3200 要求每折测试 ≥3200 → 折数 ≤6 → 取 5 折（测试 4000，每类 400）。**这是被 k 网格逼出来的数学约束，不是偷懒**（偏离 D5）。
- **分层**：`StratifiedKFold(n_splits, shuffle=True, random_state=42)`，逐数据集各取一次；不重复（repeats=1），随机性由 C3 的 seed 实验承担。
- **MNIST/FMNIST 子采样**（P9）：对每个类 c（按 P1 的标签序），`rng = np.random.default_rng(42 + c)`，从该类全部索引中取 2000 个（`replace=False`），合并后按原始行号排序。→ 恰好 20000 行，每类 2000。子采样**在折划分之前**完成，折基于子采样后的行号。
- **splits.json** 存**行号**而非数据：`{"seed": 42, "datasets": {name: {"n": int, "n_folds": int, "folds": [{"train": [...], "test": [...]}]}}, "config_sha256": "..."}`。JSON 用 `json.dumps(..., sort_keys=True, indent=1)` 落盘（字节稳定）。
- **测试可重放**：`tests/test_data_contract.py` 只读 `data/processed` 与 `splits.json`，不访问网络。

## 4. 评估协议

### E1 定性嵌入（对应 C1）

- 5 数据集 × 4 方法（PCA、t-SNE、UMAP-ours、UMAP-ref），固定 2 维；COIL-20/MNIST/FMNIST 用 §3.4 的 20k 子采样（MNIST/FMNIST）或全量（COIL-20）。
- 超参（全部固定，不逐数据集调）：UMAP `n_neighbors=15, min_dist=0.1, n_epochs=500, init="spectral", random_state=42`；t-SNE `perplexity=30, init="pca", learning_rate="auto", max_iter=1000, random_state=42`。
- 出图：`figures/results/fig2_qualitative.png`，每行一个数据集、每列一个方法，点按类别着色，**图内文字英文**（本机无中文字体），300 dpi，不画标题以外的装饰。
- 判定：见 §5.2 C1 的 rubric。

### E2 kNN 精度（对应 C2）

- 流程：对每个 (数据集, 方法, 折)：在该折的 **train 行**上拟合降维 → 得到全部 n 点的 2 维坐标（**transductive**：降维用了无标签的全体点，与原文"embeddings used for training the kNN classifier"以及 t-SNE 的常规用法一致）；用 train 行坐标 + train 标签训练 `KNeighborsClassifier(n_neighbors=k, metric="euclidean", algorithm="brute")`，在 test 行坐标上预测，记准确率。
- **transductive 说明**：降维本身用了 test 点的无标签坐标（原文与我们的实现都如此），因此 kNN 准确率衡量的是"嵌入保留了多少类结构"，不是"泛化"；报告必须写明这一点，避免被读成数据泄漏。
- k 网格：PenDigits/COIL-20 = {10,20,40,80,160}；Shuttle = {100,200,400,800,1600,3200}；MNIST/FMNIST = {100,200,400,800,1600,3200}。**k 必须 < 每折 train 规模**，运行前 assert。
- 逐折结果 → `results/grid_knn.csv`；均值±std（ddof=1）→ `results/grid_knn_summary.csv`。

### E3 稳定性（对应 C3）

- 数据集：Shuttle（58k，若 §8 R3 触发则 20k 统一切换）+ COIL-20（1440）。**替代 Flow Cytometry**（见偏离 D4）。
- 流程（严格按原文 §5.3）：
  1. 全量嵌入 `Y_full = embed(X)`；
  2. 对子采样率 s ∈ {5%,10%,25%,50%}、seed ∈ {0,1,2}：取 `idx`（分层子采样，保证每类至少 1 个点），`Y_sub = embed(X[idx])`；
  3. `Y_ref = Y_full[idx]`；
  4. 用 `scipy.spatial.procrustes(Y_sub, Y_ref)` 做最优平移+缩放+旋转对齐（`procrustes` 会先各自标准化，注意它返回的 `disparity` 是**标准化后**的平方和，需按下面的归一化口径重算）；
  5. 归一化：先把两组点各自除以"嵌入的平均范数" `mean(||y_i||_2)`（原文："dividing by the average norm of the embedded dataset"，我们取 `Y_ref` 的均值范数），再对齐、算 `dP = sqrt(Σ_i ||x_i − y_i'||²)`。**实现细节以 `src/procrustes.py` 的 docstring 为准，并在报告脚注写明公式**（原文对"是否先归一化再对齐"有歧义，两种顺序差一个常数因子，方向判断不受影响）。
  6. 对每个 (方法, s, seed) 记 `dP`；按 s 平均。
- t-SNE 的 `max_iter` 在稳定性实验中用 **1500**（原文为 Flow 明确提到从 1000 提到 1500，我们沿用以保证 t-SNE 收敛不成为混淆因素）。
- 判定：UMAP 的 `dP(s)` 曲线**整体低于** t-SNE（见 §5.2）。
- 出图：`figures/results/fig4_stability.png`（x=子采样率，y=平均 dP，每方法一条线 + 误差带）。

### E4 运行时间（对应 C4）

- 计时段：仅 `fit`（含 NN 搜索、谱初始化、SGD）；**不含**数据加载、评估、绘图。
- 每 (数据集, 方法) 重复 3 次，取**中位数**，同时记录 min/max；报告同机条件（`nproc`、`free`、`NUMBA_NUM_THREADS=1`、joblib 串行警告）。
- 单次上限 30 min/配置；超时记为 `timeout`，**不进均值**，单独列出（这本身是结论的一部分）。
- 判定只看**同机相对排序**，绝不与 Table 3 的秒数直接比（不同硬件）。

### E5 统计与不确定性

- 折内均值 `mean`、`std(ddof=1)`；C2 的"至少不差"用**均值 ± 原文 std** 的区间判断，不做显著性检验（原文也没做；样本量 10 折，SNedecor 检验收益低）。
- 报告里每个数字旁标 `n_folds`；`results/README_numbers.md` 是唯一数字来源。

### E6 扩展实验（Novelty，对应评分维度）

- 超参热力图：`n_neighbors ∈ {5,10,15,30,50,100}` × `min_dist ∈ {0,0.1,0.5,0.8}`，在 PenDigits 与 COIL-20 上各 24 组嵌入（共 48），度量 = 2D 嵌入的 kNN 精度（k=10 与 k=100）+ 2D silhouette。
- 原文只有 Fig.2/Fig.3 的定性插图（"Variation of UMAP hyperparameters n and min-dist"），**没有量化**。我们把它变成可读的 2×4 热力图 + 一句结论（"min_dist 主导簇内紧致度，n_neighbors 主导全局连通性；小 n 时 kNN 精度先升后降，拐点在 15–30"）。
- 产出：`results/extension_heatmap.csv`、`figures/results/fig5_extension_heatmap.png`。

## 5. 等价判据（Equivalence criteria）

### 5.1 三件套

对每一条主张，同时检查三件事，缺一不可：

1. **方向（direction）**：我们测出的符号差（UMAP − 基线）与原文一致；
2. **排序（ordering）**：同一方法族内部的排序（如 UMAP > t-SNE > LE > PCA 在大 k 上）与原文一致；
3. **幅度（magnitude）**：`|ours − paper| ≤ tol`，tol 按数据集给定（见 5.2）。

### 5.2 逐条判据

| 主张 | 方向判据 | 排序判据 | 幅度判据（tol） | 判定为"复现"的条件 |
|---|---|---|---|---|
| **C1** | UMAP 与 t-SNE 的二维图"区分出同样的结构" | UMAP 的全局结构 ≥ t-SNE（rubric 第 3 项） | 不做数值 | 3 项 rubric **全部**满足，且两人（A/C）独立评分结论一致 |
| **C2** | 小 k：UMAP ≥ t-SNE − 0.03；大 k：UMAP > t-SNE | 5×4 排序矩阵中 ≥70% 的 (数据集,k) 位置与原表一致 | PenDigits 0.03；COIL-20 0.10；Shuttle 0.01；MNIST/FMNIST **只判方向**（20k 子采样，口径不同） | 三件套全过 = 复现；方向+排序过、幅度不过 = 部分复现；方向不过 = 未复现 |
| **C3** | UMAP 的 dP(s) < t-SNE 的 dP(s)，对所有 s | dP 随 s 单调不增（UMAP 侧） | 原文无绝对值 | 4 个采样率中 ≥3 个满足方向且 UMAP 曲线整体在下 |
| **C4** | UMAP 比 t-SNE 快（至少在小/中数据集）；比 PCA 慢是允许的 | 5 方法排序与原文 ≥60% 位置一致 | 不与 Table 3 比绝对值；同机比值只做描述 | 方向过 + 无超时 = 复现；有 1 个数据集超时 = 部分复现 |

**tol 的来历**（必须写进报告脚注）：tol 取原文该数据集 std 的 1–2 倍量级；PenDigits `σ≈0.03–0.07` → 0.03，COIL-20 `σ` 最大 0.115（k=160）→ 0.10，Shuttle `σ≤0.006` → 0.01。tol **在看结果之前**由 CANDIDATE_ASSESSMENT 的冒烟偏差定下，事后不得放宽（§5.4）。

**C1 的 rubric**（三项，每项 0/1）：
1. 同类点形成**分离的簇**，与 t-SNE 的簇数一致（±1）；
2. **不出现"丝带化/碎裂"**（同一类被拆成 ≥3 个远离的碎片，而 t-SNE 没有）；
3. **全局结构**：类间的相对位置（如 MNIST 的 4/7/9 与 3/5/8 分块、F-MNIST 的鞋类/衣类分块）在 UMAP 中可辨认。
评分方式：A、C 各自独立看图打分（不看对方），记录在 `results/c1_rubric.csv`；分歧项由第三人（B）裁定或复核。

**C1 的辅助量化证据**（为避免"看图说话"）：`silhouette_score(X_2d, y)` 与 `trustworthiness(X, X_2d, n_neighbors=15)`，只作旁证，不参与判定（原文没有这两个数，无法设 tol）。

### 5.3 判定词

- **复现**：三件套全过；
- **部分复现**：方向与排序过，幅度超出 tol（或仅部分数据集/参数点过）；
- **未复现**：方向不符，或数据/实验无法完成；
- **不可比**：原报告数字本机无对应口径（如 LargeVis），不计入分母。

每条主张的最终判定写进报告 §4 结论表，逐条列出证据文件。

### 5.4 冻结条款（防 p-hacking）

1. 判据、tol、k 网格、折数在**看到主表结果之前**冻结（本文件 v1）；
2. 任何事后调整一律进 `docs/DEVIATIONS.md`，标注"事后"并说明调整前后的判定；
3. 禁止"换个 seed 直到过"；seed 只允许 42（主表）与 {0,1,2}（稳定性）；
4. 禁止删掉不利于结论的配置；缺失点要在表里留空并注明原因。

## 6. 实验矩阵

| 编号 | 实验 | 数据集 × 方法 × 参数 | 产物 | 预估 |
|---|---|---|---|---|
| E1 | 定性网格 | 5 × 4 | `fig2_qualitative.png` | 5 min |
| E2 | 主表 kNN | 5 × 5 × (5 或 6) 个 k × (10 或 5) 折 | `grid_knn.csv`、`grid_knn_summary.csv` | 60–90 min |
| E3 | 稳定性 | 2 × 3 × 4 采样率 × 3 seed | `stability_procrustes.csv`、`fig4` | 2–3 h |
| E4 | 计时 | 5 × 5 × 3 次 | `runtime.csv`、`fig`（bar） | 1–2 h |
| E5 | 敏感性（讨论用） | COIL-20 k=160 缺口定位 ~8 组；缩放不变性 3 组；MNIST 子采样 10k vs 20k 2 组 | `sensitivity_*.csv` | 40 min |
| E6 | 超参热力图 | 2 × 24 配置 | `extension_heatmap.csv`、`fig5` | 20 min |

**执行顺序**（每步产物落盘后再下一步）：PenDigits → COIL-20 → Shuttle → MNIST → F-MNIST。先小后大，前两个数据集的结果足以在 11-14 判断自研实现是否可信（G2）。

**命名**：`results/{exp}_{dataset}_{method}.csv` 为原始逐折，`results/{exp}_summary.csv` 为聚合；图 `figures/results/figN_*.png`（N 对应报告图号）。

## 7. 偏离日志

完整条目在 `docs/DEVIATIONS.md`（D1–D14 已预登记）。协议层摘要：

| ID | 偏离 | 方向性影响 |
|---|---|---|
| D1 | 不跑 LargeVis | 主表少一列，不影响 C2 判定（原文该列与 t-SNE 重合） |
| D2 | 所有方法用固定默认超参（原文称"tuned"但未披露） | 可能低估 t-SNE/UMAP 的最佳表现，双向 |
| D3 | t-SNE 用 sklearn（单线程）而非 MulticoreTSNE | C4 的加速比**偏乐观**（对 UMAP 有利），必须在讨论中写明 |
| D4 | C3 用 Shuttle/COIL-20 替代 Flow Cytometry | 数据规模小 2 个数量级，dP 绝对值不可比，只看方向与曲线形状 |
| D5 | MNIST/FMNIST 20k 子采样 + 5 折（原文 70k/20 折） | C2 在这两个集上只判方向 |
| D6 | kNN 用 sklearn `KNeighborsClassifier` | 与原文"kNN classifier"一致，影响可忽略 |
| D7 | Procrustes 归一化顺序的歧义（先归一化 vs 先对齐） | 差常数因子，方向不变 |
| D8 | 运行时间含谱初始化（原文未拆分） | 同口径比较，无影响 |
| D9 | COIL-20 k=80/160 已预登记为"未复现" | 见 §5.2，转写为讨论 |
| D10 | 无中文字体，图内英文 | 无 |
| D11 | 20k 子采样下 k=3200 的分类器接近"先验分类器" | 大 k 数值解读需谨慎，报告注明 |

## 8. 交付物与验收

| 交付物 | 路径 | 验收人 | 验收方式 |
|---|---|---|---|
| 本协议 | `docs/PROTOCOL.md` | A 自检 | §5 每条主张都有判据与证据路径 |
| 偏离日志 | `docs/DEVIATIONS.md` | A | 每条含"原因 + 影响方向" |
| 原文数字 | `docs/PAPER_NUMBERS.md` | C | 与 PDF 逐格核对（抽查 10 格） |
| 数据包 | `data/processed/*.npz` + `data/manifests/*` | A | `docs/HANDOFF_B2A.md` 的 V1–V6 |
| 数据卡 | `docs/DATA_CARD.md` | A | V7 |
| 主表 | `results/grid_knn*.csv` | C | 行数 = 数据集 × 方法 × k × 折 |
| 数字汇总 | `results/README_numbers.md` | C | 报告里每个数字可回溯到该文件的行 |
| 图表 | `figures/results/fig1..5*.png` | C | 300 dpi、英文标注、图注含 n 与方法参数 |
| 可复现命令 | `scripts/repro.sh` | A | 空 `results/` 下跑通 PenDigits 全流程 |

## 附录 A · 关键命令（A 用，B 参考）

```bash
cd /home/pklgames/coding/dsai5102MiniProject
source .venv/bin/activate

# 数据（B 负责；A 用第二实现复核）
python scripts/fetch_data.py --datasets all
python src/data_prep.py --datasets all      # 写 data/processed/*.npz + manifests
python scripts/make_splits.py               # 写 data/manifests/splits.json

# 契约测试（A 的门）
python -m pytest -q tests/test_data_contract.py

# 主表（可断点续跑）
python scripts/run_grid.py --datasets pendigits coil20 --methods pca le tsne umap_ref umap_ours

# 稳定性 / 计时 / 扩展
python scripts/run_stability.py --datasets shuttle coil20 --sizes 0.05 0.1 0.25 0.5 --seeds 0 1 2
python scripts/run_runtime.py --datasets all --repeats 3
python scripts/run_extension.py --datasets pendigits coil20
```

环境注意：`NUMBA_NUM_THREADS=1`（否则 numba 在受限环境报错/抖动）；`joblib` 会打印 `[Errno 13] Permission denied ... serial mode`，可忽略但**意味着串行**，预算按单核算。

## 附录 B · 与原文数字对照的方式

`docs/PAPER_NUMBERS.md` 已有 Table 1/2/3 的全量转录。A8 生成 `results/paper_vs_ours.csv`：列 = `dataset, method, k, paper_acc, paper_std, our_acc, our_std, delta, n_folds, verifiable(bool)`；报告 Fig.3 即该表的散点（45 点，对角线上方=我们更好）。C 只读该 CSV 与 `README_numbers.md`，不手抄。

---

## 变更记录

| 版本 | 日期 | 变更 | 依据 |
|---|---|---|---|
| v1 | 2026-11-11 | 首次冻结 | 冒烟结果（`results/smoke_umap/`）+ 原文 §5 | 
