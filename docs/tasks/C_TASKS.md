# C 任务书（报告 · Slides · 答辩）

> 你负责 **P12–P15**，交 **S5**（11-21 23:59 报告 PDF）与 **S6**（11-24 12:00 slides PDF）。
> 数字只来自 `results/README_numbers.md`（A 维护），图只用 `figures/results/*.png`（B 渲染）；**不得估算、不得补写没跑的实验**。
> 材料：口径与判据 `docs/goal/SPEC.md`、原文数字 `docs/goal/PAPER_DATA.md`、数据 `docs/goal/DATA_CARD.md`、偏离 `docs/log/DEVIATIONS.md`、结果映射 `results/REPORT_MAP.md`。

## 0. 边界

- ✅ 可改：`report/`、`slides/`
- ❌ 不改：`src/`、`results/`、`data/`、`configs/`、`docs/goal/**`（除 DATA_CARD 由 B 填）、`figures/results/*.png`
- 数字对不上：去 `README_numbers.md` 找对应行并问 A，**不要自己重跑**（重跑引入未记录的 seed/硬件差异，更不可信）。
- 要改图版式：找 B；B 掉线就把图另存到 `report/figs/` 自己调，但报告里注明"版式经调整"。

## 1. 报告（`report/`，6–8 页不含附录）

六节 + 数据来源与预处理 + Statement of Individual Contribution。**§3 只写我们的实现，硬上限 2 页。**

| 元素 | 来源 |
|---|---|
| 表 1 数据集摘要（源、n×d、类数、用途、替换说明） | `docs/goal/DATA_CARD.md` §1 |
| 表 2 主结果（mean ± std，方法 × 数据集） | `results/grid_knn_summary.csv` |
| 表 3 原文 vs 我们 + 判定 | `results/paper_vs_ours.csv` + `docs/goal/PAPER_DATA.md` |
| 表 4 运行时间（同机，标硬件） | `results/runtime.csv` |
| Fig.1 方法示意（自绘） | 自己画（matplotlib/tikz） |
| Fig.2 定性嵌入（COIL-20，UMAP-ours vs t-SNE） | `figures/results/fig2_qualitative_coil20.png`（B 出图，你只插图+图注） |
| Fig.3 原文 vs 我们散点（y=x 参考线） | `figures/results/fig3_paper_vs_ours.png`（B 出图） |
| 附录 A 偏离清单（D1–D18，含影响方向，D18 必现） | `docs/log/DEVIATIONS.md` 转表 |
| 附录 B 复现指南（环境 + 命令 + 实测时长） | `PLAN.md` §6 + `docs/goal/SPEC.md` §7 |
| 贡献声明 | 每人：负责范围 + 工作量占比 + 对应 commit/文件 |

**写作规范**
- 数字旁标 `n_folds`；表下注写「transductive 嵌入，kNN 衡量的是嵌入保留的类结构，不是泛化」（SPEC §4 E2），否则会被读成数据泄漏。
- 图注首句是**结论**，不是「图 X 展示…」；图内文字英文（本机无中文字体）。
- 引用：`[1]` McInnes et al. 2018（预印本，被复现对象，全部数字来源）+ `[2]` Healy & McInnes 2024 NRMP 4:82（正式综述，仅补默认超参与方法学）；两者并列且说明关系，禁用「预印本/正式版」错误表述（SPEC §1.1）。t-SNE/LE/PCA/LargeVis 各一条正式引用；数据给 URL。
- 范围：本轮只复现 **C2**。不得出现稳定性曲线、九数据集时间表、超参热力图；未做的写进 Limitations/Future work，**不写成已复现**。
- **降重（硬性）**：与原文 8-gram 重合率 **<5%**（`python scripts/similarity_check.py`，11-19、11-20 各跑一次）。做法：§3 不复述公式推导（三句话 + 自绘示意图），主体写「我们的过程 / 我们的数字 / 我们的诊断」，结构用「主张→判据→结果→诊断」。

## 2. 占位符写法（让你 Day1 就能写完 §4）

1. S1 里 A 会发 `results/README_numbers.md` **模板**，键名固定：`{{knn.<dataset>.<method>.k<k>.mean|.std}}`、`{{runtime.<dataset>.<method>.fit_s}}`、`{{verdict.<dataset>.k<k>}}`。
2. 正文与表格**禁止手打数字**，一律占位符。
3. 需要「大概什么量级」写句子时，可用 11-10 冒烟实测（**只作方向参考，禁止当结论**）：PenDigits k=10 t-SNE .987 / UMAP-ref .988，k=160 .951/.921；COIL-20 k=10 .958/.860，k=80 .765/.806，k=160 .640/.606。
4. S3 到达后（P14）：`grep -n '{{' report/*` 必须为空；逐项对 `README_numbers.md`；抽查 3 处对 csv。**替换是机械动作，不要重写句子。**

## 3. Slides（8 页，6 分钟）

标题+结论 → 问题 → 方法示意 → 复现设置 → 主结果(1 张表/图) → 与原文差异 → 差异原因 → 结论与局限。
- 每页 ≤6 行、字号 ≥24pt、无代码截图；第 5 页只放一个结论（「小 k 与原文一致，COIL-20 大 k 未复现」）。
- 第 7 页主动讲 **D3**（t-SNE 用 sklearn 单线程 → 加速比偏乐观）与 **D9**（COIL-20 偏低）——讲清偏差方向是加分点，不要回避。
- 彩排 ≥2 次并记 `slides/rehearsal.md`：用时、卡壳处、被问的问题+回答要点；第 1 次 ≤5:00；超时先删扩展页，不删主结果页。
- 预演 3 个必被问：① 为什么 COIL-20 大 k 没复现？② 你的 t-SNE 公平吗？③ 自研与 umap-learn 差在哪？

## 4. 时间线

| 时点 | 交付 | 依赖 |
|---|---|---|
| Day1（11-12） | **P12**：骨架 + Fig.1 + §1/§2/§3 | 无（不依赖数字） |
| Day2（11-13） | **P13**：§4 占位符版 + 表 1–4 版式、Fig.2/3 就位 | S1 模板 |
| S3 到达后 | **P14**：替换定稿 | S3、S4 |
| 11-14～11-17 | §1/§5（诊断与偏离）/§6 成稿 | 数据卡终版、DEVIATIONS |
| 11-18 | 报告 v1（六节齐全） | 三块素材齐 |
| 11-19～11-20 | 查重 + 图注 + 参考文献 + 附录 + 贡献声明；A 复核数字 | — |
| 11-21 23:59 | **S5** 提交 | — |
| 11-22/23 | slides + 讲稿 + 彩排 ×2 | 报告定稿 |
| 11-24 12:00 | **S6** 提交 | — |

## 5. 提交与协作

- 命名：`report/DSAI5102_<GroupID>_Report.pdf`、`slides/DSAI5102_<GroupID>_Slides.pdf`。
- 分支 `report` / `slides`，只提交自己目录，push 后 A 合入 `main` 并打 tag（`s5`、`s6`）。
- 提交前 ≥24 h 交 A 复核数字（A 只核数字与图，不改文字）。
- 用了 AI 润色/改写：在贡献声明里披露范围（哪些段落、谁审校）。
