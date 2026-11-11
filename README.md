# DSAI5102 Mini-Project · 论文复现（第二轮）

**选题已定：UMAP**（McInnes, Healy & Melville, *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction*, arXiv:1802.03426, 2018；DOI `10.48550/arXiv.1802.03426`）。配套读物（非被复现对象）：Healy & McInnes, *Uniform manifold approximation and projection*, Nature Reviews Methods Primers 4:82 (2024)，DOI `10.1038/s43586-024-00363-x`。
筛选过程与证据见 `docs/CANDIDATE_ASSESSMENT.md`；**项目计划见 `PLAN.md`；复现协议见 `docs/PROTOCOL.md`（v1，2026-11-11 冻结）**。

Format 2.2「学术论文复现」的工作区。上一轮复现的 SMOTE（Chawla et al., JAIR 2002）已按用户要求移出工作区，
其完整内容保留在 git tag `smote-repro-v1`（见 `for_next_round.md` §2）。

**新一轮约束**：论文发表年份 **2010 年至今**（用户 2026-11-11 放宽）；其余要求不变（核心统计 DM / ML 方法、可复现、易写报告）。
任务原文见 `project_request.txt`。

### 从哪读起

| 想做的事 | 读这个 |
|---|---|
| 知道这两天怎么排、谁交什么（三条独立轨道 + P1–P9 + S1–S3 同步点） | **`PLAN.md`** §2 |
| 知道"做什么、怎样算复现成功" | `docs/PROTOCOL.md`（v2 §0 范围修订 + C2 判据阈值） |
| 知道哪些地方和原文不一样、影响哪条结论 | `docs/DEVIATIONS.md`（D1–D18） |
| 要原文数字做图/做表 | `docs/PAPER_NUMBERS.md`（Table 1/2/3 全量） |
| 做数据准备（B） | `docs/TASKS_B.md` |
| 验收数据（A） | **`docs/HANDOFF_B2A.md`**（V0–V9 命令级核验 + 拒收条件） |
| 写报告/slides（C） | `docs/TASKS_C.md`（含 C1b 占位符写作法）+ `docs/REPORT_OUTLINE.md` |
| 报告里要填的数字（唯一来源） | **`results/README_numbers.md`**（模板 v0，`{{...}}` 占位符） |
| 每天进度 | `docs/RUN_STATUS.md`；交接记录 `docs/HANDOFF_LOG.md` |
| 第一轮选题经验 | `selecting_exp.md`；交接背景 `for_next_round.md` |
| 选题评估与冒烟 | `docs/CANDIDATE_ASSESSMENT.md` |

论文 PDF 与抽取文本：`paper/umap_arxiv2018.pdf`、`paper/umap_arxiv2018.txt`（被复现的 2018 预印本）；`paper/s43586-024-00363-x.pdf`（2024 Nature Reviews Methods Primers 配套综述，用于核对默认超参，非复现对象）。其余候选已删，否决理由见评估文档 §2。

## 目录

```
src/              UMAP 自研实现（umap_impl/：fuzzy / spectral / optimize / umap）+ data.py + 评估模块
src/data.py       建模侧 loader（A）；B 的 src/data_prep.py 是独立第二实现，两者对拍
scripts/          一次性脚本（fetch_data、make_splits、run_grid、run_runtime、run_extension、make_figures、similarity_check、repro.sh）
tests/            pytest（数据契约、划分重放、自研实现与 umap-learn 对拍）
configs/          main.yaml（2 数据集 × 4 方法）/ extension.yaml（未执行，标 executed:false）—— 协议 §6 的机器可读版
docs/             协议 / 偏离 / 原文数字 / 数据卡 / 交接核验 / 任务书 / 报告大纲 / 运行状态
paper/            论文 PDF 与抽取文本（本地保留，按 .gitignore 不入库）
data/raw/         原始数据（不入库）
data/processed/   {name}.npz（不入库）
data/manifests/   {name}.json 与 splits.json（入库，契约真值）
figures/          eda/（B）与 results/（A）
notebooks/        探索性分析（B 组员）
report/           报告源文件（C 组员）
slides/           答辩 slides（C 组员）
```

## 环境

已验证：16 vCPU / 7.5 GB 内存（available ~4 GB）/ 无 GPU / Python 3.14.7（`.venv` 已就绪，无需重建）。
关键事实：`joblib` 在本机只能串行（会打印 `[Errno 13] Permission denied ... serial mode`）；numba 需 `NUMBA_NUM_THREADS=1`；无中文字体（图内全英文）；`~/.cache` 不可写。

```bash
# 补装/升级依赖（沙箱内需要指定缓存与 Python 目录）
UV_CACHE_DIR=/home/pklgames/coding/.uvcache \
UV_PYTHON_INSTALL_DIR=/home/pklgames/coding/.uvpython \
uv pip install --python .venv/bin/python -r requirements.txt

# 测试（A 在 P2 之后提供 tests/）
.venv/bin/python -m pytest tests/ -q
```

## 约定（与第一轮相同，仍然有效）

- **折划分固定种子**（`seed=42`，`StratifiedKFold`），任何人重跑得到同一数字；UMAP 复现**不做重采样/不做过采样**，也没有"只在训练折内"的标签依赖步骤；
- **transductive 说明**：降维用到全体点的无标签坐标，kNN 分类器只在 train 折上训练——报告必须写明（见 `docs/PROTOCOL.md` E2）；
- **数据契约优先级**：`data/manifests/*.json` 是样本数真值，加载即校验，不符直接报错；用 `array_sha256`（不是 npz 文件哈希）判断可重放；
- **偏离日志**：与原文的每一处不同都写进 `docs/DEVIATIONS.md`，并写清方向性影响；
- **等价判据**：「方向一致 + 排序一致 + |Δ| ≤ 阈值」三件套，阈值在 `docs/PROTOCOL.md` §5.2 冻结，事后不得放宽；
- **数字纪律**：报告/幻灯片里每个数字必须能指到 `results/` 的具体行（`results/README_numbers.md` 为唯一来源）；
- 图与表都用英文标注（本机 matplotlib 无中文字体）。
