# 成员 C 任务书（报告 + Slides）

> 角色：报告正文与答辩材料。**所有数字必须来自 `results/README_numbers.md`**（A 维护的唯一数字来源），图用 `figures/results/*.png`；不得估算、不得补写未跑的实验。
> 提纲：`docs/REPORT_OUTLINE.md`；数据：`docs/DATA_CARD.md`（B）；协议与判据：`docs/PROTOCOL.md`；原文数字：`docs/PAPER_NUMBERS.md`；偏离：`docs/DEVIATIONS.md`。

## 0. 边界

- ✅ 可改：`report/`、`slides/`
- ❌ 不改：`src/`、`results/`、`data/`、`configs/`、`docs/PROTOCOL.md`、`docs/DEVIATIONS.md`、`docs/PAPER_NUMBERS.md`、`figures/results/*.png`（要改版式请另存 `report/figs/`）
- 数字对不上：找 A 要 `README_numbers.md` 的对应行，**不要自己重跑**（重跑会引入未记录的 seed/硬件差异，反而更不可信）

## 1. 交付物

### C1 报告（`report/`）

- 章节按 `docs/REPORT_OUTLINE.md` §1，六节 + 数据来源与预处理 + Statement of Individual Contribution（课程强制）；篇幅 **6–8 页**（不含附录），其中 **§3 只写我们自己的实现，硬上限 2 页**。
- ⚠️ 范围修订 v2（`deviations` D18）：本轮**只复现 C2**。报告里不得出现稳定性曲线、九数据集时间表、超参热力图；未做的部分写进 §5 Limitations / Future work，**不写成已复现**。
- 格式二选一：`report/main.tex`（推荐，投稿风格）或 `report/main.docx`；**11-13 定下后不再换**。
- 必备元素（缺一不可）：

| 元素 | 来源 |
|---|---|
| 表 1 数据集摘要（源、n×d、类数、用途、替换说明） | `docs/DATA_CARD.md` §1 |
| 表 2 主结果（均值 ± 折间 std，方法 × 数据集） | `results/grid_knn_summary.csv` |
| 表 3 原文 vs 我们 + 判定（复现/部分复现/未复现/unverifiable） | `results/paper_vs_ours.csv` + `docs/PAPER_NUMBERS.md` |
| 表 4 运行时间（同机，标注硬件） | `results/runtime.csv` |
| Fig.1 方法示意（自绘，不截图） | 自己画（用 matplotlib/tikz 都行） |
| Fig.2 定性嵌入（**只 COIL-20**，UMAP-ours vs t-SNE 两联图） | `figures/results/fig2_qualitative_coil20.png`（**B 的 P7c 渲染**，你只插图） |
| Fig.3 原文 vs 我们 散点（y=x 参考线） | `figures/results/fig3_paper_vs_ours.png`（**B 渲染**；底层数据 `results/paper_vs_ours.csv`） |
| 附录 A 偏离清单表 | `docs/DEVIATIONS.md` 转表（**D1–D18**，含影响方向；D18 必须出现） |
| 附录 B 复现指南（环境 + 命令 + 实测时长） | `scripts/repro.sh` + `PLAN.md` §7 |
| Statement of Individual Contribution | 每人一段：负责范围 + 工作量占比 + 对应 commit/文件 |

- **图不由你改版式**：Fig.2/Fig.3 由 B（P7c）出图，你只负责插入 + 写图注；需要改字号/图例时找 B，别自己动 `figures/results/`（会让「图与 csv 一致」的核验失效）。B 掉线时用 A 的简版，并在 contributor 声明里写明。
- **降重要求（硬性）**：与原文的 8-gram 重合率 **<5%**（`scripts/similarity_check.py` 自查，11-19 与 11-20 各跑一次）。做法：§3 不复述原文公式推导（理论三句话 + 一张自绘示意图即可），主体写「我们的过程 / 我们的数字 / 我们的诊断」，结构用「主张→判据→结果→诊断」而不是照抄原文 §5.1→§5.4。
- 写作规范：
  - 每个数字后标注 `n_folds`；表格下注写清"transductive 嵌入"（见 PROTOCOL §4 E2），避免被读成数据泄漏；
  - 图注首句必须是**结论**，不是"图 X 展示…"；
  - 引用：**UMAP 必须两篇并列引用并说明关系**——[1] McInnes, Healy & Melville (2018) arXiv:1802.03426（预印本，被复现对象，全部数字来源）；[2] Healy & McInnes (2024) Nature Reviews Methods Primers 4:82, DOI 10.1038/s43586-024-00363-x（同作者正式发表综述，仅补默认超参与方法学）。模板与禁忌见 `docs/PROTOCOL.md` §1「引用规范」；其余每个被引方法一条正式引用（t-SNE/LE/PCA/LargeVis）；数据给 URL 或 OpenML did；
  - **图内文字英文**（本机无中文字体），正文语言全组统一（建议英文，便于引用原文术语）。

### C1b 占位符写作法（让你不等 A 的数字）

**问题**：结果节的数字来自 A 的计算，如果等数字到位才动笔，C 有 1–2 天空转。
**解法**：先把「结构」和「措辞」写完，数字留占位符，最后 30 分钟机械替换。

1. S1（Day 1 10:00）A 会发布 `results/README_numbers.md` **模板**，键名固定，例如：
   `{{knn.<dataset>.<method>.k<k>.mean}}`、`{{knn.<dataset>.<method>.k<k>.std}}`、`{{runtime.<dataset>.<method>.fit_s}}`、`{{verdict.<dataset>.k<k>}}`。
2. 正文里**禁止手打数字**，一律用占位符；表格里同理。这样 §4 可以 Day 1 就写完。
3. 需要"大概什么量级"来写句子时，用 11-10 的**冒烟实测值**（只作方向参考，禁止当结论）：

   | 数据集 | k | t-SNE | UMAP-ref（冒烟） | PCA |
   |---|---|---|---|---|
   | PenDigits | 10 | 0.987 | 0.988 | 0.649 |
   | PenDigits | 160 | 0.951 | 0.921 | 0.640 |
   | COIL-20 | 10 | 0.958 | 0.860 | 0.720 |
   | COIL-20 | 80 | 0.765 | 0.806 | — |
   | COIL-20 | 160 | 0.640 | 0.606 | — |

   > 这些只是方向提示（例如「COIL-20 大 k 偏低」是已知的 D9 现象），**终值以 S3 的 `README_numbers.md` 为准**。
4. P9b（S3 到达后）：`grep -n '{{' report/*` 必须为空；逐项与 `README_numbers.md` 对一遍；表格数值与 csv 抽查 3 处。**替换是机械动作，不要重写句子。**
5. S3 迟到也不空转：报告 v1（11-18）之前有 4 天余量，占位符版本可以先给导师/组内看结构。

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
| **11-12** | **P4**：骨架 + Fig.1 + §1 + §2 + §3（≤2 页） | 无（全是不依赖数字的章节） |
| **11-13** | **P9** §4 占位符版 + 表 1–4 版式、Fig.2/3 就位；**P9b** S3 到达后替换定稿 | S1 模板（不依赖 A 的时间表） |
| 11-14～11-17 | §1 / §5（诊断与偏离）/ §6 成稿；补 §3 的示意图说明 | `DATA_CARD.md` 终版、`DEVIATIONS.md` |
| 11-18 | **报告 v1（全文六节）** | 三块素材齐 |
| 11-19～11-20 | 8-gram 查重（目标 <5%，跑两次）+ 图注 + 参考文献 + 附录 A/B + 贡献声明 | A 复核数字 |
| 11-21 23:59 | **提交版 PDF** | — |
| 11-22/23 | slides 8 页 + 讲稿 + 彩排 ×2 | 报告定稿 |
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
