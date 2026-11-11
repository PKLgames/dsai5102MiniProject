# DSAI5102 小组项目计划（形式 2.2 论文复现）

> 组员 3 人 ｜ 报告 2026-11-21 23:59 ｜ PPT 2026-11-24 12:00 ｜ 答辩 6 分钟（11-25/26）
> 评分维度：Time、Team、Slides、Completeness、Methodology、Novelty
> 计算条件：16 vCPU / 7.5 GB 内存 / **无 GPU**；venv 在 `dsai5102MiniProject/.venv`（imbalanced-learn 0.14.2、scikit-learn 1.9.1、Python 3.14）

## 1. 选题

**SMOTE: Synthetic Minority Over-sampling Technique**，Chawla, Bowyer, Hall, Kegelmeyer，JAIR 16 (2002) 321–357（arXiv:1106.1813）。PDF 与抽取文本在 `paper/`。

选择理由：

1. **易复现**：数据全是 KB–MB 级表格数据；`imbalanced-learn` 提供成熟实现，我们出错只会是协议问题、不会是代码问题；单次实验秒级，全矩阵 CPU 小时级；无 GPU 需求。
2. **易写报告**：论文 Table 3 直接给出 8 个数据集 × 5 种采样率的 AUC 数字，可逐行对照；结论是混合的（多数数据集 SMOTE 更好，Oil 与 E-state 更差），讨论部分天然有内容；消融维度多（k、采样率、变体）。
3. **风险最低**：备选论文都有更硬的缺口（iForest 依赖 ODDS，探测返回 403；NCF 依赖负采样协议；XGBoost 的 Higgs 在 7.5 GB 内存跑不动）。

## 2. 复现目标

**三条主张（对应论文自己的说法，不夸大）**

| 编号 | 主张 | 论文证据 |
|---|---|---|
| C1 | SMOTE + 多数类降采样，在**多数**数据集上 AUC 优于纯随机降采样 | Table 3：8 条记录中赢 6 条（Pima/Phoneme/Satimage/Forest Cover/Mammography/Can），输 Oil、E-state |
| C2 | 增益与不平衡比、类重叠程度相关（Mammography 42:1、Satimage 9:1 收益最大） | Table 2 + §5.2 |
| C3 | 合成过采样优于简单复制（树更小、少数类召回更高） | Fig. 4、5、19 |

**不做**：C4.5 release 8 本身（用 `DecisionTree(entropy)` 代理，并声明差异）、1990 年代的 UCI 版本、AUC 小数完全对齐。

**替换协议（必须写进报告）**：10-fold CV → 5×2 分层 CV、固定种子；指标 AUC（主）+ PR-AUC + G-mean + Brier；等价判据 = 效应方向一致 + 方法排序一致 + 效应量在容差内；所有偏离记入 `DEVIATIONS.md`。

## 3. 数据

论文用了 9 个二分类不平衡数据集。**7 个可原样获取**（已核验 OpenML 存在）：

| 论文数据集 | 来源 | 少数/多数 |
|---|---|---|
| Pima | OpenML did 37 | 268 / 500 |
| Phoneme | OpenML did 1489 | 1586 / 3818 |
| Adult | OpenML did 179 | 11687 / 37155 |
| Satimage | OpenML did 182 | 626 / 5809 |
| Forest Cover | OpenML did 150 / 1596 | 2747 / 35754（需取 2 类子集，可下采样） |
| Mammography | OpenML did 310 | 260 / 10923 |
| Oil | OpenML did 311 | 41 / 896 |

**2 个无公开镜像**，按“同角色”替换（角色 = 样本量、不平衡比、维度）：

| 缺失 | 角色 | 替代 | 说明 |
|---|---|---|---|
| E-state（53,220×~200，8.4:1） | 中大样本、高维、中度不平衡 | `qsar-biodeg`(did 1494) 或 `yeast`(did 181)，加 KDDCup99 子集补“中大样本”格 | 化学信息学数据 2002 年后仍是私有 |
| Can（443,872×~30，52:1） | 超大样本、极端不平衡 | KDDCup99 10%（did 1113，494,021×41，~20:1） | Can 是 AVATAR/Mustafa 内部产物 |

替代的代价：Can 那一行的绝对 AUC（9535/9560）不可比，只比方向与相对提升；`DEVIATIONS.md` 记录一条，报告 Discussion 写一段。

**外部有效性数据**：UCI credit-card fraud（OpenML did 1597，284,807×30）——现代真实不平衡场景，用于扩展。

**数据风险**：KDDCup99 的 target 需固定二分类化规则（`normal.` vs 攻击类）并写进 `PROTOCOL.md`，否则数字不可复现。

## 4. 实验矩阵

- 采样器：none / RandomOver / RandomUnder / SMOTE(k∈{1,3,5,10}) / 采样率∈{100%,200%,500%} / Borderline-SMOTE / ADASYN / SMOTE+ENN / SMOTE+Tomek / class_weight='balanced'
- 学习器：DecisionTree（主，对齐 C4.5）+ RandomForest + LogisticRegression（稳健性）
- 指标：AUC、PR-AUC、G-mean、F1、Brier；重复实验给 mean ± std
- 统计检验：跨数据集 Wilcoxon signed-rank；与论文 Table 3 的逐行对照表
- 交付图表：Table 1（AUC vs 论文）、Table 2（消融）、AUC-不平衡比 折线、PR 曲线、k/采样率 热图、运行时表

## 5. 扩展难度评估与决定（已核实可实现性）

今天实测 imblearn 0.14.2 中 `SMOTE(sampling_strategy, k_neighbors)`、`BorderlineSMOTE`、`ADASYN`、`SMOTEENN`、`SMOTETomek`、`RandomUnderSampler` 全部可直接调用，**变体对比几乎是“改一行构造函数”的成本**。

| 扩展项 | 实现成本 | 计算成本 | 结论 |
|---|---|---|---|
| k 敏感性 k∈{1,3,5,10} | 极低（参数网格） | 分钟级 | **做** |
| 4 个 SMOTE 变体对比 | 极低（imblearn 现成类） | 分钟级 | **做** |
| 采样率 100/200/500% | 极低（`sampling_strategy` 浮点） | 分钟级 | **做**（本就属 C1 复现） |
| 外部数据（credit-card fraud） | 低（下载 + 预处理） | 10 分钟级 | **做**（Novelty：现代场景） |
| 阈值/代价敏感决策层（用 `predict_proba` 扫阈值、最小化期望代价、画代价曲线） | 中（约 50–80 行 + 一张图） | 分钟级 | **做（轻量版）** |
| 提出并验证一个“新采样算法” | 高（设计 + 调参 + 说服力） | 数小时 + 大量写作 | **不做**（收益低、风险高） |

**决定：做“轻扩展三件套”** —— ①变体与 k 的横向对比（复现自然产物）②credit-card 外部验证 ③阈值/代价敏感分析。不做新算法发明。理由：前者在 imblearn 上成本≈0 而直接贡献 Methodology + Novelty；后者容易变成“自娱自乐的调参”，且挤占写作时间。

## 6. 6 分钟答辩结构（7 页，目标 5:30）

1. 标题 + 一句话结论（15s）
2. 问题与动机：不平衡为什么让 accuracy 失效（40s）
3. SMOTE 一页纸：公式 + 合成点示意（60s，Methodology 得分点）
4. 复现设置：7+2 数据集、协议、偏离说明各一行（40s）
5. **核心结果：AUC 对照表**，同时报“赢的”和“输的”（90s）
6. 消融 + 扩展：k/采样率热图、变体对比、代价曲线（60s）
7. 挑战与改进：3 条要点（45s）

规则：每页 ≤3 个要点；结果页必须把论文数字与本组数字并排；彩排以 5:30 为准。

## 7. 分工

| 成员 | 角色 | 负责内容 | GitHub 目录 | 报告章节 |
|---|---|---|---|---|
| **A（我）** | 主计划 + 主要代码 | 论文分析、协议与主张、**全部核心实验代码**、偏离记录、结果汇总 | `src/`、`scripts/`、`results/`、`docs/PROTOCOL.md`、`docs/DEVIATIONS.md` | 引言、方法、实验结果、结论 |
| **B** | 经典数据分析 + 预处理 | 数据获取、清洗、不平衡比统计、CV 切分、**EDA 图表**、基线复现、显著性检验 | `data/`、`src/data_prep.py`、`notebooks/eda/`、`figures/eda/` | 数据描述（数据来源 + 预处理，任务书强制要求）、部分结果 |
| **C** | 报告 + slides | 报告撰写与排版、6 分钟 PPT、彩排计时、参考文献 | `report/`、`slides/` | 讨论（挑战与改进）、PPT 叙事 |

协作规则：一个产物只有一个 owner；任何进入报告的数字由 A 复核、B 负责溯源（哪个脚本、哪个种子）；C 负责进度节拍；报告末尾“个人贡献声明”按本表填写。

## 8. GitHub 工作区结构

```
dsai5102MiniProject/
├── README.md                 # 项目说明、复现命令、环境
├── requirements.txt          # 固定版本
├── .gitignore                # data/raw/**, results/raw/**, *.pdf 大文件缓存等
├── paper/                    # 论文 PDF、抽取文本、笔记（A）
├── docs/
│   ├── PROTOCOL.md           # 协议：CV、种子、指标、等价判据（A）
│   ├── DEVIATIONS.md         # 与论文所有偏离及理由（A）
│   └── DATA_CARD.md          # 每个数据集的来源/许可/预处理（B）
├── data/
│   ├── raw/                  # 原始下载（不入库，脚本可重现）
│   ├── processed/            # 清洗后 parquet + splits.json（B 产出，A 消费）
│   └── manifests/            # 校验和、下载日志
├── src/
│   ├── data_prep.py          # 加载/清洗/切分（B）
│   ├── samplers.py           # 采样器封装（A）
│   ├── metrics.py            # AUC/PR-AUC/G-mean/Brier（A）
│   ├── run_grid.py           # 主网格（A）
│   ├── run_extensions.py     # 变体/k/代价分析（A）
│   └── eda.py                # 描述统计与图（B）
├── scripts/                  # 一键复现脚本（A）
├── configs/                  # 网格配置 yaml（A）
├── results/                  # 指标 json/csv（A），raw/ 不入库
├── figures/                  # 出图：eda/（B）、results/（A）
├── notebooks/                # 探索性分析（B）
├── report/                   # 报告源文件（C）
└── slides/                   # 6 分钟 PPT（C）
```

分支约定：`main` 保持可运行；各自用 `feat/<名字>-<内容>` 分支 + PR；`results/` 与 `figures/` 只提交汇总产物，原始大文件不入库。

## 9. 交接节点与依赖（无日期，按顺序）

| 节点 | 产出 | Owner | 阻塞谁 |
|---|---|---|---|
| **N0 仓库就绪** | 目录骨架、`requirements.txt`、`.gitignore`、README 模板 | A | 全体 |
| **N1 数据就绪** | 7 个原数据 + 2 个替代集落盘；`data/processed/*.parquet` + `splits.json`；`DATA_CARD.md` | **B** | A 的主网格（A 可先用 Pima 单集冒烟，不等 B） |
| **N2 冒烟通过** | Pima 一行 AUC（论文 7242 / 7307）方向可复现 | A | C 可开始写方法/引言（不依赖数字） |
| **N3 主网格冻结** | Table 1 对照表 + 消融表 + 显著性检验 | A | C 写结果章节、做 PPT 结果页 |
| **N4 扩展完成** | 变体/k/代价分析图表 | A | C 的讨论与 PPT 第 6 页 |
| **N5 报告 v1** | 全文初稿 | C | A 复核数字 |
| **N6 提交** | 报告 → PPT | C（收集）/A（最终代码检查） | — |

**我（A）开工前需要的东西**

- **不需要 B 的结果**就能开工：N0 仓库、`src/samplers.py`/`metrics.py`、Pima 单集冒烟（我自带最小加载器）。
- **需要 B 的 N1 产出**才能跑主网格：`data/processed/*.parquet` + `splits.json`（切分必须由 B 固定并入库，否则 A/B 的数字对不上）。
- **需要 C 的输入**只有一件事：报告模板/格式（LaTeX 还是 Word）与图片尺寸规范——决定我出图的格式，越早给越好。
- 反过来，C 的写作不依赖我：引言、论文方法总结、数据描述（等 B）可立即动笔。

## 10. 风险

| 风险 | 应对 |
|---|---|
| 绝对 AUC 对不上（CART≠C4.5、数据版本差异） | 预声明等价判据；报告里把差异归因当分析写 |
| KDDCup99 二分类化规则不一致 | 写进 `PROTOCOL.md`，代码里硬编码并写测试 |
| 内存 7.5 GB 上限 | 大集（Covertype/KDDCup99）分层采样至 ≤100k 行，float32 |
| joblib 在多进程受限（实测退化为串行） | 时间按串行估算，必要时用线程 |
| 答辩超时扣分 | 两次计时彩排，以 5:30 为准 |

## 11. 待你核验确认

- [ ] 选题 SMOTE 与“轻扩展三件套”是否同意
- [ ] 2 个缺失数据集用替代（qsar-biodeg/yeast + KDDCup99）是否接受
- [ ] 分工：B 负责预处理与 EDA、C 负责报告与 PPT、A 负责全部实验代码——是否与组员实际能力匹配
- [ ] 报告格式（LaTeX / Word）由 C 尽快确定并告知 A（影响出图与表格导出）
- [ ] GitHub 目录结构是否照此执行（仓库地址/权限待你提供）
- [ ] 是否同意“A 先建仓库并做 Pima 冒烟，不必等 B 的数据”
