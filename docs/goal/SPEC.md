# 总目标与口径 · UMAP 复现

> 状态：**v3（2026-11-12 冻结）**。冻结后任何改动必须写进 `docs/log/DEVIATIONS.md` 并标「事后修改」。
> 本文件只说三件事：**复现什么、怎么算、接近到什么程度算复现**。节点与分工见 `PLAN.md`，原文数字见 `docs/goal/PAPER_DATA.md`。

## 1. 复现对象与主张

[1] McInnes, Healy & Melville (2018). *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction*. arXiv:1802.03426（63 页预印本，无正式会议/期刊版）。DOI `10.48550/arXiv.1802.03426`。
[2] Healy & McInnes (2024). *Uniform manifold approximation and projection*. Nat. Rev. Methods Primers **4**:82. DOI `10.1038/s43586-024-00363-x`（同作者教程综述，**无新实验**）。

原文的实证主张有 4 条，本轮**只复现 C2**：

| ID | 主张 | 原文证据 | 本轮 |
|---|---|---|---|
| C1 | 2 维嵌入的视觉质量与 t-SNE 可比 | §5.1、Fig.4 | 降级为 **1 张定性图**，不作正式评分 |
| **C2** | 嵌入上训 kNN：k=10–40 至少不差于 t-SNE；**大 k 更好**（COIL-20 k=80/160 显著） | §5.2、Table 1/2、Fig.5/6 | **本轮唯一主张**：PenDigits + COIL-20，原规模、10 折 |
| C3 | 子采样下 UMAP 更稳定（归一化 Procrustes） | §5.3、Fig.7/8 | 不做（写进 Future work） |
| C4 | 运行时间普遍更快 | §5.4、Table 3 | 只留 4 行 fit 秒数，不作加速比结论 |

**复现边界**：原文数字来自作者机器（MacBook Pro i7 3.1 GHz / 8 GB）与 MulticoreTSNE，我们只能复现**方向与排序**，绝对值按 §5 容差判定。

### 1.1 引用规范（报告 / slides / 答辩通用）

- 两篇**必须同时引用并说明关系**：`[1]` 是被复现对象与所有定量结果的唯一来源；`[2]` 只用于核对默认超参（其 Table 1：n_neighbours=15、min_dist=0.1、n_components=2、metric=Euclidean、init=spectral）与结果解读注意事项。
- 禁止说法：「[1] 是 [2] 的预印本」「[2] 是 [1] 的正式发表版」「两篇内容相同」。
- 讨论「原文未披露超参」这一 reproducibility gap 时，必须同时说明 [2] 已给出默认值。

## 2. 数据

| 数据集 | 原文 n × d | 本轮 | 来源（唯一指定） | 备注 |
|---|---|---|---|---|
| PenDigits | 1797 × 64 | ✅ | `sklearn.datasets.load_digits()` | 8×8 灰度、像素 0–16；**不是** OpenML did=32 的 10992 条版本 |
| COIL-20 | 1440 × 16384 | ✅ | `coil-20-proc.zip`（已在 `data/raw/coil20/`，1440 张 128×128 PNG，`objK__NN.png`） | 20 类 × 72 |
| Shuttle | 58000 × 9 | ✗ D18 | OpenML `data_id=40685` | 7 类、极不平衡 |
| MNIST | 70000 × 784 | ✗ D18 | OpenML `data_id=554` | 20k 子采样口径已废弃 |
| Fashion-MNIST | 70000 × 784 | ✗ D18 | OpenML `data_id=40996` | 同上 |

距离全部欧氏（原文仅 GoogleNews 用余弦，不跑）。

## 3. 规范口径（B 实现，A 逐条核验）

| 编号 | 决策 | 理由（写进数据卡） |
|---|---|---|
| R1 | `X: float32 (n,d)` C 序；`y: int64 (n,)`，类别按**首次出现**排序编码 0..K−1 | 与 sklearn `LabelEncoder` 一致，跨脚本可比 |
| R2 | **不做标准化/缩放**；PNG 仅 `/255` 落 [0,1] | UMAP 模糊图对均匀缩放不变（σ、ρ 同比缩放，a/b 只依赖 min_dist）；全组统一避免「预处理差异」被当成算法差异 |
| R3 | 图像行优先展平，不转置 | 与原文「treated as 16384 dimensional vector」一致 |
| R4 | 不去重；重复行数只记入 manifest | 去重会改变 n，破坏与原文计数对齐 |
| R5 | 出现 NaN/inf 立即 fail，不填补 | 这两个数据集不应有缺失；有就是 loader 有 bug |
| R6 | 落盘 `data/processed/{name}.npz`，键固定 `X`、`y`，`np.savez_compressed` | 单文件、无 pickle、可重放 |
| R7 | `array_sha256 = sha256(X.float32 C 序字节 + y.int64 字节)` | **不能用 npz 文件哈希**（zip 头含时间戳，字节不稳） |
| R8 | 时间戳统一 UTC ISO8601 | 跨机可读 |
| R9 | 划分：`StratifiedKFold(n_splits=10, shuffle=True, random_state=42)`，不重复 | 与原文 10 折一致；随机性由 seed 冻结承担 |

**硬校验**（loader 返回前 assert，失败抛错）：形状/dtype；`n` 精确等于 1797 / 1440；`np.isfinite(X).all()`；`set(y)=={0..K-1}`；`0 ≤ X.min()`、`X.max() ≤ 1+1e-6`；manifest 六项统计（n/d/K/类计数/NaN/重复行）与数组实测一致。

**splits.json**：存**行号**不存数据，`{"seed":42,"datasets":{name:{"n":int,"n_folds":10,"folds":[{"train":[...],"test":[...]}]}}}`，`json.dumps(sort_keys=True, indent=1)`，重跑字节相同。折大小差 ≤1，`train∩test=∅`。

## 4. 评估口径

### E1 定性（对应 C1，1 张图）

- 只 COIL-20 × {UMAP-ours, t-SNE} 两联图，固定 2 维、全量 1440 点。
- 超参固定：UMAP `n_neighbors=15, min_dist=0.1, n_epochs=500, init="spectral", random_state=42`；t-SNE `perplexity=30, init="pca", learning_rate="auto", max_iter=1000, random_state=42`。
- A 只导出坐标 `results/embeddings/coil20_{umapours,tsne}.npz`（键 `E` float32、`y` int64）；图由 B（P11）渲染成 `figures/results/fig2_qualitative_coil20.png`。

### E2 主表 kNN（对应 C2，本轮核心）

- 对每个 (数据集, 方法, 折)：在该折 **train 行**上 fit 降维 → 得到全部 n 点 2 维坐标（**transductive**：降维用了无标签的全体点，与原文一致）；用 train 坐标 + 标签训 `KNeighborsClassifier(n_neighbors=k, metric="euclidean", algorithm="brute")`，在 test 行预测。
- **必须写进报告**：kNN 衡量的是「嵌入保留了多少类结构」，不是泛化；避免被读成数据泄漏。
- k 网格 `{10,20,40,80,160}`；运行前 assert `k < 每折 train 规模`。
- 方法：PCA、t-SNE（sklearn）、UMAP-ref（umap-learn）、UMAP-ours（自研）。
- 产物：逐折 `results/grid_knn.csv`；聚合 `grid_knn_summary.csv`（mean ± std，ddof=1）；`paper_vs_ours.csv`（列见 `results/REPORT_MAP.md`）。

### E4 计时（对应 C4，只留 4 行）

- 只计 `fit`（含 NN 搜索、谱初始化、SGD），不含加载/评估/绘图；每 (数据集, 方法) 重复 3 次取中位数，记 min/max。
- 单配置上限 30 min，超时记 `timeout` 不进均值、单独列出。
- 判定只看**同机相对排序**，绝不与 Table 3 秒数直接比。

### 本轮不做（省下的时间换 C2 的扎实度）

C3 稳定性、E3/E5/E6、超参热力图、MNIST/FMNIST/Shuttle、LargeVis/LE、`transform` 泛化、拓扑推导复算。理由与影响方向见 `docs/log/DEVIATIONS.md`（D18 等）。

## 5. 等价判据

**三件套**：① 方向（UMAP−基线的符号与原文一致）② 排序（同一 k 下方法排序一致）③ 幅度（`|ours−paper| ≤ tol`）。

| 主张 | 方向 | 排序 | 幅度 | 「复现」条件 |
|---|---|---|---|---|
| C1 | UMAP 与 t-SNE 区分出同样结构 | UMAP 全局结构 ≥ t-SNE | 不做数值 | 三项 rubric 全过（簇数一致 ±1、无丝带碎裂、全局位置可辨），A/C 独立评分一致 |
| **C2** | 小 k：UMAP ≥ t-SNE − 0.03；大 k：UMAP > t-SNE | 5×4 排序矩阵中 ≥70% 位置与原文一致 | PenDigits **0.03**；COIL-20 **0.10** | 三件套全过 = 复现；方向+排序过、幅度不过 = 部分复现；方向不过 = 未复现 |

tol 来历：原文该数据集 std 的 1–2 倍量级（PenDigits σ≈0.03–0.07；COIL-20 σ 最大 0.115）。**看结果之前冻结，事后不得放宽。**

判定词：**复现 / 部分复现 / 未复现 / 不可比**（不可比 = 本机无对应口径，如 LargeVis）。每条判定在报告 §4 逐条列出证据文件。

**冻结条款**：判据、tol、k 网格、折数在看主表前冻结；事后调整一律进 DEVIATIONS 标「事后」；禁止换 seed 直到过（主表只用 42）；不允许删掉不利配置。

## 6. 与原文的差异（摘要）

| D | 偏离 | 对结论的影响方向 |
|---|---|---|
| D1 | 不跑 LargeVis | 主表少一列，不影响 C2 判定 |
| D2 | 全方法固定默认超参（原文称 tuned 未披露） | 可能低估各方法最佳表现，双向 |
| D3 | t-SNE 用 sklearn 单线程而非 MulticoreTSNE | **C4 的加速比偏乐观**（对 UMAP 有利），报告必须标注 |
| D9 | COIL-20 k=80/160 冒烟已未复现（.806/.606 vs 原文 .899/.803） | 预登记为讨论项，不掩饰 |
| D18 | 只复现 C2、两个数据集 | 不作稳定性/加速比外推；报告中写明 |

完整 18 条在 `docs/log/DEVIATIONS.md`。

## 7. 命令

```bash
cd /home/pklgames/coding/dsai5102MiniProject && source .venv/bin/activate
export NUMBA_NUM_THREADS=1          # joblib 会报 serial mode，意味着串行，预算按单核算

python src/data_prep.py --datasets pendigits coil20   # B：写 npz + manifest
python scripts/make_splits.py                          # B：写 splits.json
python -m pytest -q tests/                             # A：契约测试
python scripts/run_grid.py --datasets pendigits coil20 --methods pca tsne umap_ref umap_ours
```

产物命名：`results/{exp}_{dataset}_{method}.csv` 为逐折，`results/{exp}_summary.csv` 为聚合；图 `figures/results/figN_*.png`。
