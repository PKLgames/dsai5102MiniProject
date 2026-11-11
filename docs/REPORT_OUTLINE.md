# 报告大纲（C 用；按评分表逐条对应）

> 评分表六个维度：Time / Team / Slides / Completeness / Methodology / Novelty。
> 每一节后面标注它拿哪一分，缺哪一节就会丢哪一分。

## 0. 封面与团队信息

- 课程、组号、成员（A/B/C）、提交日期。
- **Statement of Individual Contribution**（评分表 Team 维度，必须在报告最后单列一节，写明每人做了什么、占比、以及哪些结果是本人跑的）。

## 1. Introduction（~1 页）

- 不平衡分类为什么重要：真实场景（医疗筛查、欺诈检测、故障诊断）里少数类才是我们关心的类。
- 论文出处：Chawla et al., *SMOTE: Synthetic Minority Over-sampling Technique*, JAIR 16 (2002) 321–357，引用量 2 万+。
- 本文的复现问题（一句话）：**在 2026 年的开源工具链上，SMOTE 原文的三条主张还成立吗？成立到什么程度？**
- 本文贡献 bullet（3 条）：①逐数据集复现 + 与原文数字对照；②替代数据集的偏差分析；③轻扩展（k 敏感性 / 变体 / 外部验证 / 阈值代价）。

## 2. Related Work（~0.5 页，可并入 Introduction）

- SMOTE 之前：随机过采样/降采样、代价敏感学习、one-sided selection。
- SMOTE 之后：Borderline-SMOTE、ADASYN、SMOTE-ENN/Tomek（这四类正是我们的扩展对照）。
- 一句话定位：本文不是提出新算法，而是**复现 + 受控对比**。

## 3. Data Description（~1 页，评分表 Completeness 的“数据处理”）

- 表格：数据集 / 来源 URL / 样本数（总/少/多）/ IR / 特征数 / 类型 / 缺失。
- 数据来源与获取方式（OpenML did、缓存 CSV 的 md5）。
- 预处理步骤逐条写清（缺失填充、one-hot、不使用测试集信息）。
- 两个替代数据集（E-state → qsar-biodeg，Can → kddcup99）必须单独说明理由与影响。
- 引用 `docs/DATA_CARD_TEMPLATE.md` 填好的版本。

## 4. Methodology（~1.5 页，评分表 Methodology 的主战场）

- 4.1 SMOTE 算法：伪代码 + 公式 x_new = x_i + (x̂_i − x_i)·δ，δ~U(0,1)；k 近邻、合成百分比、为什么能缓解过拟合。
- 4.2 实验协议：5×2 分层 CV；重采样只在训练折；C4.5 代理（CART+熵+CCP 剪枝）及其理由（D1/D9）。
- 4.3 判据：C1/C2/C3 的可操作定义（`docs/PROTOCOL.md`）。
- 4.4 指标：AUC 为主，PR-AUC/G-mean/Brier 为辅；为什么单看准确率会骗人。
- 4.5 **与原文的偏离表**（D1–D12 精简成表）：这是 Methodology 维度“严谨性”的加分项，不要藏。

## 5. Experimental Results（~2 页，Completeness 的“模型训练+结果分析”）

- 5.1 主表：8 个数据集 × {none, rus{25,50,100}, ros, smote{100,200,500}} 的 AUC（mean±std）。
- 5.2 C1 判定表：每个数据集“最佳 SMOTE vs 最佳 Under”胜负 + 合计 x/8。
- 5.3 与原文 Table 3 的并排对照（同数据集同列，标注 substitute 行）。
- 5.4 显著性：数据集内配对 Wilcoxon，报告 p 值与效应量。
- 5.5 图：AUC 随过采样率变化的折线图（每数据集一条）；箱线图（各方法分布）；PR 曲线（1–2 个代表数据集）。
- 5.6 敏感性：剪枝强度三档（dt_raw / dt_msl5 / dt）对 C1 的影响（D10）——**这段是诚实性加分**。

## 6. Discussion（~1 页，Novelty + Methodology）

- 哪些主张成立、哪些不成立、为什么不成立（数据版本、学习器差异、CV 协议）。
- k 敏感性：k=1 噪声大、k 大导致合成样本侵入多数类区域（用图说明）。
- 变体对比：Borderline-SMOTE/ADASYN 在高 IR 数据集上是否更稳。
- 外部验证：credit-card（IR 578）上 SMOTE 是否仍然有效——分布差异带来的新发现。
- 阈值与代价：AUC 提升不等于业务收益，代价比 5:1/10:1 下的最优阈值变化。
- 局限：无 GPU、单机、只做二分类、树模型为主。

## 7. Conclusion（~0.3 页）

- 三句话：复现了什么、发现了什么偏差、对实践者的建议。

## 8. 参考文献 + 附录

- 参考文献：原文、Borderline-SMOTE、ADASYN、SMOTE-ENN、imbalanced-learn 论文、scikit-learn。
- 附录 A：完整结果表（全部 sampler × dataset）。
- 附录 B：复现命令（`scripts/run_all.sh`）与环境版本。
- 附录 C：Statement of Individual Contribution（若未放封面后）。

## 图表清单（交付前核对）

| 编号 | 内容 | 数据来源 |
|---|---|---|
| Fig.1 | 不平衡数据示意（两类散点 + SMOTE 合成点） | `figures/results/smote_illustration.png` |
| Fig.2 | 各数据集 AUC vs 过采样率 | `results/grid*_summary.csv` |
| Fig.3 | 方法箱线图 | 同上 |
| Fig.4 | PR 曲线（pima + oil） | 逐折预测概率（需保存 `results/raw/*.npz`） |
| Fig.5 | k 敏感性 | `results/k_sensitivity.csv` |
| Fig.6 | 阈值–代价曲线 | `results/threshold_cost.csv` |
| Tab.1 | 数据集描述 | `docs/DATA_CARD_TEMPLATE.md` |
| Tab.2 | 主结果 | `results/grid*_summary.csv` |
| Tab.3 | C1 判定 | `report/c1_table.md` |
| Tab.4 | 与原文对照 | 手工整理（原文 Table 3 + 我们的数字） |
