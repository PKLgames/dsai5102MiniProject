# DSAI5102 Mini-Project · UMAP 复现

被复现对象：[1] McInnes, Healy & Melville, *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction*, arXiv:1802.03426 (2018)。
配套读物（非复现对象）：[2] Healy & McInnes, *Uniform manifold approximation and projection*, Nat. Rev. Methods Primers 4:82 (2024)。

Format 2.2「学术论文复现」。课程要求见 `project_request.txt`；上一轮 SMOTE 的内容保留在 git tag `smote-repro-v1`。

## 从哪读起（四类文件，一类一目录）

| 类 | 目录 | 内容 |
|---|---|---|
| **计划** | `PLAN.md` | 节点 P1–P15、交付物 S1–S6、依赖图、降级顺序、文件地图 |
| **总目标/口径** | `docs/goal/` | `SPEC.md`（复现什么/怎么算/判据）、`PAPER_DATA.md`（原文 Table 1/2/3）、`DATA_CARD.md`（B 填） |
| **日志** | `docs/log/` | `RUN_LOG.md`（每天一行）、`HANDOFF_LOG.md`（每次交接一行）、`DEVIATIONS.md`（D1–D18） |
| **任务书 + 交付标准** | `docs/tasks/` | 每人两份：`A_TASKS.md`/`A_ACCEPTANCE.md`、`B_TASKS.md`/`B_ACCEPTANCE.md`、`C_TASKS.md`/`C_ACCEPTANCE.md` |
| **结果** | `results/` | `README_numbers.md`（唯一数字来源）、`REPORT_MAP.md`（结果→报告映射）、`*.csv`、`embeddings/` |

| 我想… | 读 |
|---|---|
| 知道这两天谁做什么、谁交什么 | `PLAN.md` §2–§3 |
| 知道怎样算复现成功 | `docs/goal/SPEC.md` §5（三件套 + tol） |
| 要原文数字 | `docs/goal/PAPER_DATA.md` |
| 干活 | 自己那份 `docs/tasks/X_TASKS.md`，发出去前对照 `X_ACCEPTANCE.md` |
| 看进度 / 交接 | `docs/log/RUN_LOG.md`、`docs/log/HANDOFF_LOG.md` |
| 知道哪些地方和原文不一样 | `docs/log/DEVIATIONS.md` |

## 目录

```
PLAN.md                    计划（节点 P / 交付物 S）
docs/goal/                 口径：SPEC / PAPER_DATA / DATA_CARD
docs/log/                  日志：RUN_LOG / HANDOFF_LOG / DEVIATIONS
docs/tasks/                任务书 + 验收：A_ / B_ / C_
paper/                     论文 PDF 与抽取文本（.gitignore，不入库）
data/raw/                  原始数据（COIL-20 已就位；不入库）
data/processed/            npz（不入库，由脚本重放）
data/manifests/            manifest + splits.json（入库，是契约真值）
src/                       data.py（A）、data_prep.py（B）、umap_impl/（A）、*_eval.py（A）
scripts/                   fetch_data、make_splits、run_grid、run_runtime、make_figures、similarity_check、repro.sh
configs/                   main.yaml（本轮）、extension.yaml（未执行）
results/                   README_numbers.md、REPORT_MAP.md、*.csv、embeddings/
figures/                   eda/（B）、results/（B 出图）
report/ slides/            C 的产出
tests/                     A 的契约测试
```

## 环境

- `.venv`：Python 3.14.7、numpy 2.5.4、scipy 1.18.1、scikit-learn 1.9.1、umap-learn 0.6.0、numba 0.68.1、matplotlib 3.11.2、pandas 3.1.1、pytest 9.2.0。
- 16 vCPU / 7.5 GB RAM / 无 GPU。`export NUMBA_NUM_THREADS=1`；joblib 会报 `serial mode` 警告 → **按单核算力**。
- matplotlib 无中文字体 → 图内英文。pyarrow 装不上 → 一律 CSV/npz。
- `~/.cache` 不可写：装包用 `UV_CACHE_DIR=$PWD/.uvcache UV_PYTHON_INSTALL_DIR=$PWD/.uvpython`。

## 团队约定

- 仓库只有 `main`；B/C 开短命分支（`data-prep`/`report`/`slides`），合并后删除。交接靠 **push + tag `s1`…`s6`**，不在聊天里发文件。
- **编号只有两套**：节点 `P`、交付物 `S`；偏离用 `D`（日志编号）。
- **数字纪律**：报告/slides 的数字只能来自 `results/README_numbers.md`；`transductive` 口径必须写明（SPEC §4 E2）；判据与 tol 冻结后不得事后放宽。
- **不互相等**：A 从 `data/raw` 自建数组，不等 B 的 npz；C 用占位符写作，不等 A 的数字。详见 `PLAN.md` §3–§4。

## 报告转换（C 的 docx → md → PDF）

```bash
.venv/bin/python scripts/docx_to_md.py report/DSAI5102_07_Report_draft.docx   # docx → md（表格/字号/高亮/图片全保留）
.venv/bin/python scripts/build_report_pdf.py report/DSAI5102_07_Report_draft.md  # md → PDF（report/report.css）
```

- 彩色占位符：**蓝=A 数据**、**黄=B 交付物**、**紫=成稿后填写**；清单见 `report/PLACEHOLDERS.md`。
- C 的提交记录与报告文件索引：`docs/log/C_SUBMISSIONS.md`。
