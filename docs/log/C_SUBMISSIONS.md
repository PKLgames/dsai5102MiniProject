# C 的提交记录与报告文件索引

> 维护人：A。每次 `git pull` 后更新。仓库只保留 `main`，C 用 GitHub 网页 "Add files via upload" 上传到 `report/`。
> 本文件只记事实（谁、什么时候、交了什么），不写计划。

## 1. 提交记录

| 时间（+08:00） | commit | 作者 | 提交信息 | 变更文件 | 大小 |
|---|---|---|---|---|---|
| 2026-11-13 18:02 | `18b0c89` | polyu26（C：YUEN Lok Yan） | Add files via upload | `report/DSAI5102_07_Report_draft.docx`（新增） | 164,080 B |
| 2026-11-13 22:07 | `ce7e53e` | polyu26（C） | Add files via upload | `report/DSAI5102_07_Report_draft.docx`（覆盖） | 163,982 B |

- 两次都是整份 docx 覆盖上传，没有 md / 图 / 代码变更。
- A 侧同步动作：`git pull --ff-only` → 本轮已拉到 `ce7e53e`；随后生成 md + PDF（见 §3）。

## 2. 报告文件索引

| 文件 | 类型 | 状态 | 说明 |
|---|---|---|---|
| `report/DSAI5102_07_Report_draft.docx` | C 原稿（二进制） | ✅ 最新（`ce7e53e`） | C 用 Word 写，含 7 张表、1 张内嵌图（Fig.1 流程图）、9 处彩色占位符 |
| `report/DSAI5102_07_Report_v2.md` | 转换稿 + A 填写（本机生成） | ✅ 最新 | 由 `_draft.md` 派生；A 已把 2 处青色占位符换成真实数据，并修正命令块（见 §7）。**不要用 docx 重跑覆盖** |
| `report/DSAI5102_07_Report_v2.pdf` | 渲染稿（本机生成） | ✅ 11 页 | 由 `scripts/build_report_pdf.py` 从 v2 md 生成，样式见 `report/report.css` |
| `report/report.css` | 样式 | ✅ | 与 docx 对齐：正文 12pt、图表标题 9pt 斜体、表格 8.5pt + 表头 `#DBE5F1`、代码 Menlo |
| `report/media/image1.png` | 从 docx 抽出的图 | ✅ | 即 Figure 1 流程图（docx 内嵌，原名 `fig1_method.png`） |
| `report/PLACEHOLDERS.md` | 占位符台账 | ✅ 9 处 | 见 §4，谁填、在哪儿，全部列出 |
| `report/DSAI5102_07_Report_Slides.pdf` | slides | ⚪ 未提交 | C 负责，S6（11-24 12:00） |
| ~~`*_draft.md` / `*_draft.pdf`~~ | 旧文件名 | 🗑 已改名 | 2026-11-13 因 v2 与 docx 分叉改名为 `*_v2.*`；`docx_to_md.py` 重跑会再次生成 `_draft.md` |

## 3. 转换流水线（A 维护，可重跑）

```bash
cd /home/pklgames/coding/dsai5102MiniProject
.venv/bin/python scripts/docx_to_md.py report/DSAI5102_07_Report_draft.docx
.venv/bin/python scripts/build_report_pdf.py report/DSAI5102_07_Report_draft.md
```

- `docx_to_md.py` 解析 `word/document.xml`：按序处理段落/表格/图片，保留表格（pipe table）、字号分段（12pt 正文 / 9pt 斜体图表标题 / Menlo 代码块）、超链接、`SEQ Figure` 域缓存值（Figure/Table 编号）、**彩色高亮**。
- `build_report_pdf.py`：pandoc（`pypandoc-binary`）转 HTML，weasyprint 按 `report/report.css` 渲染 A4 PDF。
- 本机额外依赖（不影响 A/B 的主实验环境）：`pypandoc-binary`、`weasyprint`、`pypdfium2`（仅用于把 PDF 渲染成 PNG 自查）。

## 4. 彩色占位符（Word highlight → md `<mark>`）

| 颜色 | Word 值 | md class | 语义 | 处数 | 谁填 | 位置 |
|---|---|---|---|---|---|---|
| 蓝（青） | `cyan` `#00FFFF` | `hl-a` | A 负责的数据占位符 | 2 | **A** | 附录 B「Measured Wall-Clock Duration」的 `«insert X minutes»`；「Originality Check」的 `«insert X.X»%` |
| 黄 | `yellow` `#FFFF00` | `hl-b` | B 负责的交付物 | 2 | **B** | 第 4 节两处 `[MISSING FIGURE: fig2_qualitative_coil20.png]`、`[MISSING FIGURE: fig3_paper_vs_ours.png]` |
| 紫（品红） | `magenta` `#FF00FF` | `hl-c` | 报告成稿后再填 | 5 | **C**（定稿前） | 第 8 节贡献表 3 个 `«hashes»`；AI 使用声明 `«which paragraphs»`、`«who»` |

- PDF 里已按原色渲染（青/黄/品红），见 `report/DSAI5102_07_Report_draft.pdf` 第 5、8、10 页。
- 机读清单：`report/PLACEHOLDERS.md`（9 行，含位置锚点与占位文本）。
- 新增占位符：C 在 docx 里加高亮 → A 重跑一次转换即可同步，md 不要手工加 `<mark>`。

## 5. 转换保真核对（2026-11-13）

| 项 | docx | md/PDF | 结论 |
|---|---|---|---|
| 表格 | 7 张 | 7 张 pipe table | ✅ |
| 图表标题编号 | `SEQ` 域 1–4、A1 | `Figure 1`…`Table A1` 全部保留 | ✅ |
| 内嵌图 | 1 张（`fig1_method.png`） | `report/media/image1.png` + `<img>` | ✅ |
| 超链接 | 4 个 | 4 个 markdown 链接 | ✅ |
| 章节标题 | 15 个加粗段（无 Heading 样式） | 15 个 `##`/`###` | ✅ |
| 代码块 | Menlo 10pt 段落 | 1 个 ```bash 围栏 | ✅ |
| 正文字符数 | 28,343 | 29,120（+2.7%，来自标记） | ✅ 无缺失段 |
| 占位符 | 9 处高亮 | 9 个 `<mark>` | ✅ 颜色一致 |

## 6. 需要有人处理的差异（不是转换错误）

1. **Figure 2 / 3 仍是黄色占位符**：等 B 的 S4（`figures/results/fig2_qualitative_coil20.png`、`fig3_paper_vs_ours.png`）。
2. **Table 1 的 PenDigits 每类计数写 178–183**，我们实测是 **174–183**（`results/README_numbers.md` / `src/data.py` 输出 `counts[174,183]`）；建议 C 在下一版 docx 改过来。
3. **Table 3 的 `Note` 与 §5 对 D9 的表述**：与 `docs/log/DEVIATIONS.md` D9 执行记录一致，无需改；但 C 若改了数字，必须同步 `results/numbers.json` 的口径。
4. **贡献表的 `«hashes»`** 需要真实 commit 短哈希；A 侧可提供：`184847d`（S3）、`360d8ea`（S1）、`5b3a32e`（P3–P6），C 填自己那次 `ce7e53e`。

## 7. A 的填写记录与 docx ↔ v2 差异（2026-11-13）

基线：docx 停在 `ce7e53e`（C 最后一次上传）。`report/DSAI5102_07_Report_v2.{md,pdf}` = 该 docx 转出的 `_draft.md` + 下列 4 处修改。
**docx 未改，所以 v2 与 docx 已经不同步**；文件名加 `_v2` 就是为了防止误当成 docx 的同步稿。

| # | 位置 | docx / `_draft.md` | v2 | 依据 |
|---|---|---|---|---|
| 1 | 附录 B「Measured Wall-Clock Duration」 | 青色 `«insert X minutes»` | `2.1 minutes` | `bash scripts/repro.sh` 实测 **2m08.6s**（16 vCPU、单核 `NUMBA_NUM_THREADS=1`，含取数/契约检查/400 行网格/计时/数字抽取） |
| 2 | 附录 B「Originality Check」 | 青色 `«insert X.X»%`，日期写 2026-11-19/20 | `0.22%`（11 命中 / 5,097 个 8-gram，全部落在参考文献标题里），日期改为实测日 2026-11-13 | `scripts/similarity_check.py` 实跑 |
| 3 | 附录 B「Reproduction Commands」 | `make_splits.sh`、`make_figures.sh`、`scripts/repro.sh` 均不存在；`run_grid.py/run_runtime.py --config` 参数不存在 | 换成仓库里真实存在的 6 步命令（`fetch_data.sh`、`src.data --sha`、`run_grid.py --recompute`、`run_runtime.py`、`fill_numbers.py`、`similarity_check.py report/*.md`、`make_figures.py`） | `scripts/` 实际内容；`run_grid.py` 的 CLI 只有 `--datasets/--methods/--recompute` |
| 5 | 第 4 节 Table 4 与随后一段 | 旧计时 0.06/9.36/2.69/3.40 s（PenDigits）与 0.62/7.74/7.69/4.68 s（COIL-20） | 同一次 `repro.sh` 运行的新值 0.04/6.00/1.85/2.58 s 与 0.43/6.06/6.29/4.11 s | `results/runtime.csv`、`results/numbers.json` 已同步刷新；相对排序（UMAP < t-SNE）不变，t-SNE 仍单线程（D3） |
| 4 | 附录 B 计时句括号 | "data fetching, split generation, grid search, runtime benchmarks, and plotting" | "one-off data download, data contract check, fixed stratified splits, the 400-row kNN grid, the runtime benchmark, and number extraction" | 与实测覆盖范围一致；绘图属 B 的 S4，未计入 |

为使第 3 条真能执行，新增两个脚本：

- `scripts/fetch_data.sh`：幂等取数（已有 1440 张 PNG 即跳过），写 `data/raw/_fetch_log.json`（zip `sha256=517c5594…`，`n_png=1440`）。
- `scripts/repro.sh`：把 0–5 步串起来并计时；`scripts/make_figures.py` 不存在时打印跳过。

**计时抖动**：单核计时对机器负载敏感，同一脚本重跑中位数可差 ±30%；表内数字是 2026-11-13 一次完整 pipeline 运行的值，`results/runtime.csv` 记录同一次运行的 min/max。

**需要 C 处理**：把上表 5 处同步回 docx（或直接以 v2 为准出终稿），否则两份继续分叉。
v2 里两个已填数字仍保留青色高亮（颜色语义 = A 的数据），定稿时可按需去掉。
