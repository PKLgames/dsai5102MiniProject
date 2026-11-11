# 偏离日志（Deviation Log）

> 论文：UMAP (arXiv:1802.03426)
> 规则（见 `docs/PROTOCOL.md` §5.4）：
> 1. **预登记**：写代码之前就能预见的偏离，先登记（D1–D15）；**事后**：跑完才发现的偏离，必须标注"事后"，并同时写出"调整前/调整后的判定"。
> 2. 每条必须写**影响方向**（对哪条主张、偏向谁）。写不出方向 = 说明还没想清楚，不许开工。
> 3. 禁止删条目。放弃的条目改成"未执行"而不是删除。
> 4. 状态取值：`预登记` / `事后` / `已执行` / `未触发` / `未执行`。

## 总表

| ID | 状态 | 类型 | 偏离内容 | 原因 | 影响方向 | 报告位置 |
|---|---|---|---|---|---|---|
| D1 | 预登记 | 范围 | 不跑 LargeVis | 无 Python 3.14 轮子、需自编译；Table 1/2 中其数值与 t-SNE 高度重合 | 主表少一列；不影响 C2 的方向判定 | §4 表注、§5 |
| D2 | 预登记 | 参数 | 所有方法使用**固定默认超参**（UMAP: n_neighbors=15, min_dist=0.1, n_epochs=500, init=spectral；t-SNE: perplexity=30, lr=auto, max_iter=1000, init=pca） | 原文 §5.1 只写"we attempted to tune parameters for each algorithm"，**未披露任何具体取值** | 双向：可能同时低估 t-SNE 与 UMAP 的最佳表现；对"UMAP vs t-SNE"的相对比较影响中性 | §4 表注、§5 "reproducibility gap" |
| D3 | 预登记 | 实现 | t-SNE 用 **sklearn**（单线程）而非原文的 **MulticoreTSNE**（C++ 多线程） | 本机 joblib 串行、无 GPU；MulticoreTSNE 无 3.14 轮子 | **C4 的 UMAP 加速比偏乐观**（对 UMAP 有利）；C2 的 t-SNE 精度与实现无关（同一算法） | §4.3 脚注、§5 讨论**必须点名** |
| D4 | 预登记 | 数据 | C3 稳定性改用 **Shuttle（58k×9）+ COIL-20**，替代原文的 Flow Cytometry（1M×17） | 1M 点超出本机内存（7.5 GB）与时间预算；t-SNE 在 1M 上不可行 | 数据规模小两个数量级；dP **绝对值不可比**，只判方向与曲线形状；原文"5% 时 UMAP 已优于 t-SNE 的任何取值"这一强结论无法逐字复现 | §4.2、§5 |
| D5 | 预登记 | 数据 | MNIST/FMNIST 用 **20k 分层子采样 + 5 折**（原文 70k / 20 折） | 内存与 t-SNE 时间；且 20 折下测试集仅 1000 点 < k=3200，kNN 无法训练 | C2 在这两个集上**只判方向与排序**，不判幅度；大 k 数值接近先验分类器 | §4.1 表注、§5 |
| D6 | 预登记 | 评估 | kNN 用 `sklearn.neighbors.KNeighborsClassifier`（brute, euclidean） | 原文未给实现细节；sklearn 是事实标准 | 可忽略（同一分类器族） | §4.1 |
| D7 | 预登记 | 评估 | Procrustes 归一化顺序：我们**先各自除以平均范数、再对齐** | 原文 "normalize ... by dividing by the average norm" 与 "determine optimal translation/scaling/rotation" 的先后有歧义 | 差一个常数因子，**方向判断不受影响**；绝对值不可与 Fig.8 比 | §4.2 脚注 |
| D8 | 预登记 | 评估 | 运行时间包含谱初始化与 NN 搜索，未按原文拆分（原文只给总时间） | 无法拆分对照 | 同口径内部比较，无影响 | §4.3 |
| D9 | **事后（已有冒烟证据）** | 结果 | **COIL-20 k=80/160 未复现**：原文 .899/.803，我们（umap-learn 参考实现，n_neighbors=15, min_dist=0.1）得 .806/.606 | 原文未披露 COIL-20 的 UMAP 超参；像素是否 /255 亦未明说；2 维嵌入下 k=160 的近邻结构对初始化敏感 | 直接削弱 C2 在 COIL-20 大 k 上的结论；**这是本项目最重要的诚实点之一** | §4.1、§5（用 E5 敏感性分析定位） |
| D10 | 预登记 | 图表 | 图内文字全英文 | 本机 matplotlib 无中文字体（会出方框） | 无 | 全文图注 |
| D11 | 预登记 | 评估 | 20k 子采样下 k=3200 的 kNN 实际接近"全局先验"分类器（3200/16000 = 20% 训练集） | 数学上无法避免 | MNIST/FMNIST 的 k=3200 数值解读需谨慎；另出一版 k≤800 的辅助表 | §4.1 脚注 |
| D12 | 预登记（条件性） | 范围 | 若 `SpectralEmbedding` 在 Shuttle（58k）上失败/超 20 min，则 LE 只在小数据集上报告 | sklearn 文档承认 LE 未针对大数据优化；原文也只在 COIL-20/PenDigits 有 LE 数字 | C2 的 Shuttle 行缺 LE 列（留空并注明） | §4.1 表注 |
| D13 | 预登记（条件性） | 数据 | 若 Shuttle 上 sklearn t-SNE 外推 > 30 min，则 Shuttle **全部方法**统一切到 20k 分层子采样 | 见 PLAN.md R3 | 口径统一后内部可比，但与原文 58k 不可比；C2/C4 的 Shuttle 行标注"缩小口径" | §4.1 表注 |
| D14 | 预登记 | 环境 | 单线程有效（joblib serial、`NUMBA_NUM_THREADS=1`、无 GPU）；硬件为 16 vCPU/7.5 GB 的共享机 | 沙箱限制（`~/.cache` 不可写、joblib 权限告警） | 只影响 C4 的绝对时间，不影响同机相对排序 | §4.3、附录 |
| D15 | 预登记 | 范围 | 不跑 Isomap（Table 3 有它）；若时间允许，仅在小数据集补一列 | 58k 上 sklearn Isomap 不可行；原文自己也说"failed to complete" | C4 表少一列 | §4.3 表注 |
| D16 | 预登记 | 数据 | Shuttle 的类别标签按 OpenML 原值映射（1..7 → 0..6，保持频次序） | P1 的编码规则 | 无（只影响标签名显示） | 数据卡 |

## 每条的执行记录（跑完后填）

### D9 · COIL-20 大 k 未复现（重点）

- **现象**：参考实现（umap-learn 0.6.0, n_neighbors=15, min_dist=0.1, seed=42, 10 折）k=10/80/160 得 .860/.806/.606；原文 .934/.921/.789/.899/.803 → k=80 差 −0.093、k=160 差 −0.197。
- **候选原因**（E5 逐项测）：
  1. 像素是否 `/255`（P2 说不影响 UMAP，但影响 `KNeighborsClassifier` 的 k 选择敏感性——实测）；
  2. `n_neighbors` 取 15 是否偏小（试 30/50/100）；
  3. 嵌入维数 2 vs 3（原文 §4.3 讨论 d，实验用 2）；
  4. 初始化（spectral vs random）；
  5. 折划分不同（原文用 sklearn 10 折但未给 seed）。
- **记录**：`results/sensitivity_coil20.csv`，每条 = (variant, k, acc_mean, acc_std)。
- **结论写法**：在 §4.1 写"k≤40 复现（.860 vs .934? 见下）…"，并明确"我们把该点判为未复现，原因最可能是原文未披露的超参与像素预处理"。

> 注：k=10 我们 .860 vs 原文 .934 也偏低，说明差距在**全局**而非只在大 k；这一点必须在讨论里如实写，不能只报"k≤40 复现"。

## 如何新增一条

```bash
# 1. 先在表里加一行（状态=事后），写清影响方向；
# 2. 若是"事后调整判据"，同时写调整前后的判定各是什么；
# 3. 在报告 §5 Limitations 里加一句，句式和本文档一致（"Due to X, we did Y; this biases Z toward ..."）；
# 4. commit message: docs: register deviation D<n>
```

## 与报告 §5 的映射

报告 §5 Limitations 按 D3 → D4/D5/D13 → D9 → D2 → D1/D15 的顺序写（影响从大到小），每条一句话 + 指向本文件 ID。C 写这部分时**只允许**用本文件的措辞，不得自创偏离。
