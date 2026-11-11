# 偏离日志（Deviation Log）

> 论文：UMAP (arXiv:1802.03426, DOI 10.48550/arXiv.1802.03426)；配套综述（非复现对象）：Healy & McInnes, Nat. Rev. Methods Primers 4:82 (2024), DOI 10.1038/s43586-024-00363-x
> 规则（见 `docs/goal/SPEC.md` §5.4）：
> 1. **预登记**：写代码之前就能预见的偏离，先登记（D1–D15）；**事后**：跑完才发现的偏离，必须标注"事后"，并同时写出"调整前/调整后的判定"。
> 2. 每条必须写**影响方向**（对哪条主张、偏向谁）。写不出方向 = 说明还没想清楚，不许开工。
> 3. 禁止删条目。放弃的条目改成"未执行"而不是删除。
> 4. 状态取值：`预登记` / `事后` / `已执行` / `未触发` / `未执行`。

## 总表

| ID | 状态 | 类型 | 偏离内容 | 原因 | 影响方向 | 报告位置 |
|---|---|---|---|---|---|---|
| D1 | 预登记 | 范围 | 不跑 LargeVis | 无 Python 3.14 轮子、需自编译；Table 1/2 中其数值与 t-SNE 高度重合 | 主表少一列；不影响 C2 的方向判定 | §4 表注、§5 |
| D2 | 预登记 | 参数 | 所有方法使用**固定默认超参**（UMAP: n_neighbors=15, min_dist=0.1, n_epochs=500, init=spectral；t-SNE: perplexity=30, lr=auto, max_iter=1000, init=pca） | 原文 §5.1 只写"we attempted to tune parameters for each algorithm"，**未披露任何具体取值**（2024 Primer 的 Table 1 默认值与这里一致：n_neighbours=15、min_dist=0.1、n_components=2、metric=Euclidean、init=spectral，可作为作者侧默认值旁证） | 双向：可能同时低估 t-SNE 与 UMAP 的最佳表现；对"UMAP vs t-SNE"的相对比较影响中性 | §4 表注、§5 "reproducibility gap" |
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
| D16 | 预登记 | 数据 | Shuttle 的类别标签按 OpenML 原值映射（1..7 → 0..6，保持频次序） | R1 的编码规则 | 无（只影响标签名显示） | 数据卡 |
| D17 | **事后（协议 v1 冻结后新增）** | 文档 | `docs/goal/SPEC.md` 新增 §1.1「引用规范」：[1] 2018 预印本（被复现对象，数字唯一来源）与 [2] 2024 Nature Reviews Methods Primers 正式综述并列引用并说明关系 | 用户指令（2026-11-11）：2024 版为正式发表、2018 版为预印本但承载主要复现内容，报告须同时引用并说明 | 无（仅写作与引用规范，不改实验设计、数据与判据） | 报告 §1、参考文献、slides 首页 |
| D18 | **事后（协议 v1→v2 范围缩减）** | 范围 | 只复现 **C2**；数据集裁到 **PenDigits + COIL-20**；C3/C4/E6（稳定性、九数据集时间表、超参热力图）与 MNIST/FMNIST/Shuttle/COIL-100/scRNA/Flow/GoogleNews、LargeVis、LE 均**本轮不执行**；C1 降为 1 张定性图，C4 降为 4 行小表 | 用户 2026-11-11 决定「一到两天能搞定」：v1 全量 ≈5–6 h 算力 + ≈20 h 开发，超出两日窗口；砍数据集而非砍判据，保住 C2 的两条原规模证据 | **方向性影响**：(a) C3 无结果 → 报告不得对稳定性作任何断言；(b) C4 无加速比结论，只报两数据集 fit 秒数；(c) Novelty 从「热力图」改为「自研实现 + 与参考实现逐部件对拍 + D9 归因」（`configs/extension.yaml` 保留但标 `executed: false`） | 报告 §2（范围）、§5（Limitations）、slides 第 7 页 |

> 状态修订（2026-11-12，D18 之后）：D5 / D11 / D12 / D13 / D16 涉及的数据集（MNIST、Fashion-MNIST、Shuttle、LE）已随范围缩减移出 → 这 5 条统一视为 **未执行**，保留在表内供报告 Future work 引用。

## 每条的执行记录（跑完后填）

### D9 · COIL-20 大 k 未复现（重点）

- **现象**：参考实现（umap-learn 0.6.0, n_neighbors=15, min_dist=0.1, seed=42, 10 折）k=10/80/160 得 .860/.806/.606；原文 .934/.921/.789/.899/.803 → k=80 差 −0.093、k=160 差 −0.197。
- **候选原因**（E5 逐项测）：
  1. 像素是否 `/255`（R2 说不影响 UMAP，但影响 `KNeighborsClassifier` 的 k 选择敏感性——实测）；
  2. `n_neighbors` 取 15 是否偏小（试 30/50/100）；
  3. 嵌入维数 2 vs 3（原文 §4.3 讨论 d，实验用 2）；
  4. 初始化（spectral vs random）；
  5. 折划分不同（原文用 sklearn 10 折但未给 seed）。
- **记录**：`results/sensitivity_coil20.csv`，每条 = (variant, k, acc_mean, acc_std)。
- **结论写法**：在 §4.1 写"k≤40 复现（.860 vs .934? 见下）…"，并明确"我们把该点判为未复现，原因最可能是原文未披露的超参与像素预处理"。

> 注：k=10 我们 .860 vs 原文 .934 也偏低，说明差距在**全局**而非只在大 k；这一点必须在讨论里如实写，不能只报"k≤40 复现"。

### D18 · 范围缩减（2026-11-12 生效）

- 生效文件：`docs/goal/SPEC.md`（范围与判据）、`PLAN.md`（节点 P1–P15 / 交付物 S1–S6）、`configs/main.yaml`（只剩 2 数据集 4 方法）、`configs/extension.yaml`（`executed: false`）、`docs/tasks/B_TASKS.md`（只交 pendigits + coil20）。
- 报告必须写清三件事：① 复现对象缩到 C2，**不外推**到稳定性与跨数据集加速比；② C2 的两个数据集是**原规模、原折数**（1797×64、1440×16384，10 折），缩范围没有削弱这条主张的证据力；③ 未做的部分列 Future work，不写成「已复现」。
- 若 11-18 之后有余量再补 C3/热力图，**必须新开 D19** 并改掉本条「未执行」，不允许静默补跑。

## 如何新增一条

```bash
# 1. 先在表里加一行（状态=事后），写清影响方向；
# 2. 若是"事后调整判据"，同时写调整前后的判定各是什么；
# 3. 在报告 §5 Limitations 里加一句，句式和本文档一致（"Due to X, we did Y; this biases Z toward ..."）；
# 4. commit message: docs: register deviation D<n>
```

## 与报告 §5 的映射

报告 §5 Limitations 按 D3 → D4/D5/D13 → D9 → D2 → D1/D15 的顺序写（影响从大到小），每条一句话 + 指向本文件 ID。C 写这部分时**只允许**用本文件的措辞，不得自创偏离。
