# 成员 C 任务书（报告 + Slides）

> 角色：报告正文与答辩材料。**所有数字必须来自 `results/` 下的汇总表或 `figures/`**，不得估算、不得补写未跑的实验。
> 提纲见 `docs/REPORT_OUTLINE.md`；数据部分从 B 的 `docs/DATA_CARD.md` 摘；方法与结果由 A 提供表格与图。

## 0. 边界

- ✅ 可改：`report/`、`slides/`、`figures/` 下的排版副本（不要改原始结果图，另存排版版）
- ❌ 不改：`src/`、`results/`、`data/`、`docs/PROTOCOL.md`、`docs/DEVIATIONS.md`
- 数字对不上时：先找 A 要"数字来源表"，不要自己调参重跑

## 1. 交付物

### D1 报告正文（`report/`）

- 章节与篇幅按 `docs/REPORT_OUTLINE.md` §1；硬性六节齐全：引言 / 数据描述 / 方法 / 实验结果 / 讨论 / 结论
- 格式：`report/main.tex`（LaTeX）或 `report/main.docx`，二选一（由组内定，格式一旦定下不再换）
- 必备元素：
  - 表 1 数据集摘要（来自 DATA_CARD）
  - 表 2 主结果（均值 ± 标准差，来自 `results/*_summary.csv`）
  - 表 3 原文 vs 我们的差异与判定（复现/部分复现/未复现）
  - 图 1 方法示意图（自绘）、图 2 主结果、图 3 与原文逐点对比
  - 附录 A 偏离清单（`docs/DEVIATIONS.md` 转表）、附录 B 复现指南（环境 + 命令 + 运行时长）
  - **Statement of Individual Contribution**（课程强制，每组员一段，写清负责范围与工作量占比）
- 引用：论文原文 + 每篇被引方法各一条正式引用；数据来源给出 URL/DOI

### D2 Slides（`slides/`，约 8 页，6 分钟）

结构按 `docs/REPORT_OUTLINE.md` §3：标题 → 问题 → 方法示意 → 复现设置 → 主结果 → 与原文差异 → 差异原因 → 结论。
每页 ≤ 6 行字，无代码截图，字号 ≥ 24pt，英文或中文统一（图内文字英文）。

### D3 彩排记录（`slides/rehearsal.md`）

- 至少 2 次计时彩排：记录每次用时、卡壳处、被问到的问题与回答要点
- 第 1 次必须 ≤ 5:00（留 1 分钟缓冲）；超时优先删"扩展实验"页，不删主结果页

### D4 提交前核对

- 报告 ≥ 与 `results/` 完全一致（逐表核对一遍）
- slides 与报告结论一致（措辞可以不同，数字必须相同）
- 文件命名：`report/DSAI5102_Group<编号>_Report.pdf`、`slides/DSAI5102_Group<编号>_Slides.pdf`

## 2. 验收清单（对照评分表自检）

- [ ] Completeness：数据处理、模型训练、结果分析三块都有，且每块能指到具体表/图
- [ ] Methodology：说明了为什么这样选（划分、指标、对照），并解释了偏差
- [ ] Novelty：至少有 1 个原文没有的实验（扩展）并给出结论
- [ ] Team：分工声明完整、可核查
- [ ] Slides：逻辑一条线（问题→方法→结果→差异→结论），无信息过载
- [ ] Time：报告与 slides 按课程截止时间提前 ≥ 24 h 提交

## 3. 协作

- 分支 `report` / `slides`，只提交自己负责的目录，完成后 push，由 A 合入 `main` 并打 tag。
- 数字来源表：A 需在 `results/` 里维护一张 `README_numbers.md`（每个报告里的数字 → 文件名 + 列名），C 只引用不计算。
