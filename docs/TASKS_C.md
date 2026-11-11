# 成员 C 任务书（报告 + Slides）

> 角色：报告正文与答辩材料。**所有数字必须来自 `results/README_numbers.md`**（A 维护的唯一数字来源），图用 `figures/results/*.png`；不得估算、不得补写未跑的实验。
> 提纲：`docs/REPORT_OUTLINE.md`；数据：`docs/DATA_CARD.md`（B）；协议与判据：`docs/PROTOCOL.md`；原文数字：`docs/PAPER_NUMBERS.md`；偏离：`docs/DEVIATIONS.md`。

## 0. 边界

- ✅ 可改：`report/`、`slides/`
- ❌ 不改：`src/`、`results/`、`data/`、`configs/`、`docs/PROTOCOL.md`、`docs/DEVIATIONS.md`、`docs/PAPER_NUMBERS.md`、`figures/results/*.png`（要改版式请另存 `report/figs/`）
- 数字对不上：找 A 要 `README_numbers.md` 的对应行，**不要自己重跑**（重跑会引入未记录的 seed/硬件差异，反而更不可信）

## 1. 交付物

### C1 报告（`report/`）

- 章节按 `docs/REPORT_OUTLINE.md` §1，六节 + 数据来源与预处理 + Statement of Individual Contribution（课程强制）；篇幅 6–8 页（不含附录）。
- 格式二选一：`report/main.tex`（推荐，投稿风格）或 `report/main.docx`；**11-13 定下后不再换**。
- 必备元素（缺一不可）：

| 元素 | 来源 |
|---|---|
| 表 1 数据集摘要（源、n×d、类数、用途、替换说明） | `docs/DATA_CARD.md` §1 |
| 表 2 主结果（均值 ± 折间 std，方法 × 数据集） | `results/grid_knn_summary.csv` |
| 表 3 原文 vs 我们 + 判定（复现/部分复现/未复现） | `results/paper_vs_ours.csv` + `docs/PAPER_NUMBERS.md` |
| 表 4 运行时间（同机，标注硬件） | `results/runtime.csv` |
| Fig.1 方法示意（自绘，不截图） | 自己画（用 matplotlib/tikz 都行） |
| Fig.2 定性嵌入网格（5 数据集 × 4 方法） | `figures/results/fig2_qualitative.png` |
| Fig.3 原文 vs 我们 散点（y=x 参考线） | `results/paper_vs_ours.csv` |
| Fig.4 稳定性曲线（dP vs 子采样率） | `results/stability_procrustes.csv` |
| Fig.5 超参热力图（扩展，Novelty 的落点） | `figures/results/fig5_extension_heatmap.png` |
| 附录 A 偏离清单表 | `docs/DEVIATIONS.md` 转表（D1–D16，含影响方向） |
| 附录 B 复现指南（环境 + 命令 + 实测时长） | `scripts/repro.sh` + `PLAN.md` §7 |
| Statement of Individual Contribution | 每人一段：负责范围 + 工作量占比 + 对应 commit/文件 |

- 写作规范：
  - 每个数字后标注 `n_folds`；表格下注写清"transductive 嵌入"（见 PROTOCOL §4 E2），避免被读成数据泄漏；
  - 图注首句必须是**结论**，不是"图 X 展示…"；
  - 引用：**UMAP 必须两篇并列引用并说明关系**——[1] McInnes, Healy & Melville (2018) arXiv:1802.03426（预印本，被复现对象，全部数字来源）；[2] Healy & McInnes (2024) Nature Reviews Methods Primers 4:82, DOI 10.1038/s43586-024-00363-x（同作者正式发表综述，仅补默认超参与方法学）。模板与禁忌见 `docs/PROTOCOL.md` §1「引用规范」；其余每个被引方法一条正式引用（t-SNE/LE/PCA/LargeVis）；数据给 URL 或 OpenML did；
  - **图内文字英文**（本机无中文字体），正文语言全组统一（建议英文，便于引用原文术语）。

### C2 Slides（8 页，6 分钟）

结构按 `docs/REPORT_OUTLINE.md` §3：标题+结论 → 问题 → 方法示意 → 复现设置 → 主结果 → 与原文差异 → 差异原因 → 结论与局限。
- 每页 ≤ 6 行字，字号 ≥ 24pt，无代码截图；
- 第 5 页只放**一个**结论（"UMAP 在小 k 与原文一致，大 k 在 COIL-20 上未复现"），不要堆 45 个数字；
- 第 7 页讲 D3（t-SNE 用 sklearn 单线程 → 加速比偏乐观）——这是**加分点**（显示你懂偏差方向），不要回避。

### C3 彩排记录（`slides/rehearsal.md`）

- ≥ 2 次计时彩排：用时、卡壳处、被问的问题 + 回答要点；
- 第 1 次 ≤ 5:00（留 1 分钟缓冲）；超时优先删"扩展实验"页，绝不删主结果页；
- 预演 3 个必被问的问题：① 为什么 COIL-20 大 k 没复现？② 你的 t-SNE 公平吗？③ 自研实现与 umap-learn 的差异在哪？

### C4 提交与命名

- `report/DSAI5102_<GroupID>_Report.pdf`（≤ 2026-11-21 23:59）
- `slides/DSAI5102_<GroupID>_Slides.pdf`（≤ 2026-11-24 12:00）
- 提交前 24 h 交给 A 复核数字（A 只核数字与图，不改文字）。

## 2. 时间线（C 的部分）

| 时点 | 交付 | 依赖 |
|---|---|---|
| 11-13 | 骨架 + Fig.1 + §2 相关工作 | 无（先写不依赖数据的两节） |
| 11-15 | §1/§3 方法草稿 | `PROTOCOL.md`、`DATA_CARD.md`（可先占位） |
| 11-18 | §4 结果主体 + 表 2/3/4 + Fig.2/3/4 | `results/README_numbers.md` v1（G5a，11-18 22:00 到） |
| 11-19 24:00 | **报告 v1（全文）** | G5 |
| 11-20 | 数字复核 + 排版 + 附录 A/B | A 复核 |
| 11-21 23:59 | **提交版 PDF** | — |
| 11-22/23 | slides + 讲稿 + 彩排 ×2 | 报告定稿 |
| 11-24 12:00 | **Slides PDF** | — |

## 3. 验收清单（对照评分表）

- [ ] Completeness：数据、方法、结果三块都有，且每块能指到具体表/图/文件
- [ ] Methodology：写清划分、种子、指标、对照、判定阈值（引用 PROTOCOL §5），并解释每个偏差
- [ ] Novelty：扩展实验（超参热力图）有结论句，不是"我们也画了个图"
- [ ] Team：贡献声明完整、可核查（能对到 commit / 文件）
- [ ] Slides：一条逻辑线，6 分钟内讲完，每页 ≤ 6 行
- [ ] Time：提前 ≥ 24 h 提交
- [ ] 数字一致性：报告 ↔ slides ↔ `README_numbers.md` 三者逐项相同（A 会抽查 10 处）

## 4. 协作

- 分支 `report` / `slides`，只提交自己目录，push 后由 A 合入 `main` 并打 tag（`report-v1`、`slides-final`）。
- 数字来源表：A 在 `results/README_numbers.md` 维护"报告里的每个数字 → 文件名 + 列名 + 行"；C 只引用不计算。
- 引用与 AI 使用：若用 AI 辅助润色/改写，必须在 Statement of Individual Contribution 里披露范围（哪些段落、由谁审校）。
