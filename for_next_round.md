# 下一轮交接（换论文后从零开始复现）

> ⚠️ **本文档是 2026-11-11 日间"换论文"时的交接说明，已进入执行阶段。**
> 现在要开工请读：`PLAN.md`（计划与质量门）→ `docs/PROTOCOL.md`（冻结的协议）→ `docs/RUN_STATUS.md`（今天该干什么）。
> 下文 §1–§6 仍是环境与经验的可靠参考；§7 的候选池结论已定稿为 UMAP。

> 读这一页 + `selecting_exp.md` 就可以开始，不需要读上一轮的对话或代码。
> 上一轮（SMOTE 复现）的工作区内容已全部删除，仅保留在 git tag `smote-repro-v1` 里（见 §8）。

## 1. 任务背景（不变）

- 任务原文：`/home/pklgames/coding/dsai5102MiniProject/project_request.txt`（Format 2.2 学术论文复现）
- 交付：报告 **2026-11-21 23:59**、Slides **2026-11-24 12:00**、答辩 **2026-11-25/26（6 分钟）**
- 评分维度：Time / Team / Slides / Completeness / Methodology / Novelty（映射见 `docs/REPORT_OUTLINE.md`）
- 报告硬性六节：引言 / 数据描述 / 方法 / 实验结果 / 讨论 / 结论；须写明数据来源与预处理
- 分工：**A**（主计划 + 主代码，与 agent 结对）、**B**（数据准备 + EDA）、**C**（报告 + slides）
- **新一轮新增约束：论文发表年份 2010 年至今**，其余筛选口径不变（统计数据挖掘/机器学习核心方法、可复现、易写报告）

今天是 2026-11-11，距报告截止 10 天：**选题必须在 11-12 内定下**，否则报告时间不够。

## 2. 工作区当前状态

> **2026-11-11 22:00 更新**：下表是"换论文时"的快照。此后已补齐执行期文件，以下条目**已被取代**，不要照旧读：
> `docs/PROTOCOL.md`（已写，v1 冻结）、`PLAN.md`（已写）、`docs/TASKS_B.md`（已按 UMAP 重写）、`docs/DATA_CARD.md`（A 已预填骨架）、
> `docs/DEVIATIONS.md`、`docs/PAPER_NUMBERS.md`、`docs/HANDOFF_B2A.md`、`docs/RUN_STATUS.md`、`configs/main.yaml`、`configs/extension.yaml`
> 均已新建；`docs/` 下两个 TEMPLATE_* 仅作历史模板保留，**新工作不再按它们写**。

已保留（可直接用）：

| 项 | 说明 |
|---|---|
| `.venv/` | Python 3.14.7，已装 numpy/scipy/scikit-learn/pandas/matplotlib/pyyaml/tabulate/pytest/pypdf，无需重建 |
| `README.md` | 目录树、环境命令、协作约定（种子/数据契约/偏离日志/等价判据） |
| `docs/TEMPLATE_PROTOCOL.md` | 复现协议模板：主张 C1–Cn、等价判据、实验矩阵、偏离日志 |
| `docs/TEMPLATE_DATA_CARD.md` | 数据卡模板（B 用） |
| `docs/REPORT_OUTLINE.md` | 报告章节 → 评分维度映射、图表清单、8 页答辩结构、时间锚点 |
| `docs/TASKS_B.md` / `docs/TASKS_C.md` | 通用版分工任务书（含验收清单） |
| `docs/templates/` | `make_splits.py.template`、`cv_grid.py.template`、`test_data_contract.py.template`（可直接落地为新论文骨架） |
| `docs/CANDIDATE_ASSESSMENT.md` | 2026-11-11 选题评估：筛选口径 + 其他候选各一句话否决理由 + UMAP 9 项核验 + 冒烟结果 + 复现框架 |
| `paper/umap_arxiv2018.{pdf,txt}` | 选定论文原文与抽取文本（其余候选 PDF 已按用户要求删除，只留否决理由） |
| `scripts/smoke_umap.py` + `results/smoke_umap/{digits,coil20}.json` | UMAP 冒烟脚本与结果（PenDigits/COIL-20 的 kNN 表） |
| `data/raw/coil20/coil-20-proc/` | COIL-20 解压后的 1440 张 128×128 PNG（不入库，可重下） |
| `configs/ data/ results/ figures/ notebooks/ report/ slides/ src/ scripts/ tests/` | 空目录结构 + `.gitkeep` |

已删除（服务于上一轮论文）：`paper/`（PDF 与抽文本）、`data/raw|processed|manifests`、`results/*`、`figures/*`、
`report/c1_table.md`、`PLAN.md`、`src/*.py`、`scripts/*.py`、`tests/*.py`、`docs/PROTOCOL.md`、`docs/DEVIATIONS.md`、
`docs/RUN_STATUS.md`、`docs/DATA_CARD_TEMPLATE.md`、`docs/TASKS_B.md`（旧版）、旧 `requirements.txt`，以及离线交付包 tar.gz。

## 3. 第一步做什么（建议顺序，别跳）

1. ✅ **列候选池**（2026-11-11 完成）：9 篇，筛选理由见 §7 与 `docs/CANDIDATE_ASSESSMENT.md`。
2. ✅ **核验**（2026-11-11 完成）：9 篇按 9 项检查表核验，仅 UMAP 全过；PDF 只保留 UMAP，其余否决理由见 §7。
3. ✅ **1 小时冒烟**（2026-11-11 完成，UMAP）：`scripts/smoke_umap.py`，PenDigits 方向与绝对值均复现（|Δ|≤0.03），
   COIL-20 仅 k=80 复现、k=160 未复现（0.606 vs 0.803）→ 见 `docs/CANDIDATE_ASSESSMENT.md` §3。
4. **写协议**（下一步）：`cp docs/TEMPLATE_PROTOCOL.md docs/PROTOCOL.md` 并填写（主张、等价判据、实验矩阵、偏离日志）。
5. **铺开代码**：从 `docs/templates/` 复制三个骨架到 `src/`、`scripts/`、`tests/`，改数据入口 `load(name)`。
6. **交 B/C**：`docs/TASKS_B.md`、`docs/TASKS_C.md` 已是通用版，只补数据集清单与截止节点。
7. **git**：`git checkout -b main-v2` 后开始提交；B 用 `data-prep` 分支，C 用 `report`/`slides` 分支。

## 4. 环境事实（省得重测）

- 硬件：16 vCPU / 7.5 GB 内存 / **无 GPU** / 磁盘充足
- 装包：`UV_CACHE_DIR=/home/pklgames/coding/.uvcache UV_PYTHON_INSTALL_DIR=/home/pklgames/coding/.uvpython uv pip install --python .venv/bin/python <pkg>`
  （默认 `~/.cache` 不可写；系统 `python3 -m venv` 缺 ensurepip；`pyarrow` wheel 会下载超时 → 用 CSV）
- joblib：沙箱下 `n_jobs>1` 退化为串行（`[Errno 13] Permission denied`）→ 估时按单核
- 网络：PyPI / arXiv / OpenML / GitHub 可用；ODDS 站 HEAD 探测 403（未验证下载）
- matplotlib：无中文字体 → 图内文字一律英文
- 沙箱安全策略：一次 curl 只查一个 URL；带凭证样式的命令会被拦
- 已验证的 OpenML 数据集（上一轮）仍在 `data/raw` 曾缓存过，但已删除；需要时用 `datasets.fetch` 式逻辑重新下载（模板里保留写法）

## 5. 不要再犯的（来自 `selecting_exp.md` §2）

1. 核心 baseline 在 sklearn 里没有实现 → 换题（上一轮 C4.5 代理 CART，剪枝强度直接翻转结论）。
2. 评估口径是"整条 ROC / 凸包 / loss-ratio 扫描"→ 换题（只能算单点 AUC）。
3. 数据集要联系作者才能拿到（老论文常见）→ 换题；替代会破坏可比性。
4. 数据没对齐就写建模代码 → 上一轮 5.5 h 里 1.5 h 花在这，且方向错了两轮。
5. 把"复现"当"原创"：Novelty 维度必须至少有一个自己设计的扩展实验。

## 6. 目录索引

```
FOR_NEXT_ROUND.md            本文件（先读）
selecting_exp.md             论文筛选经验 + 评分卡 + 检查表
README.md                    目录树 / 环境 / 协作约定
project_request.txt          课程要求原文
docs/TEMPLATE_PROTOCOL.md    协议模板（复制为 docs/PROTOCOL.md）
docs/TEMPLATE_DATA_CARD.md   数据卡模板（复制为 docs/DATA_CARD.md）
docs/REPORT_OUTLINE.md       报告与答辩结构
docs/TASKS_B.md              成员 B 任务书
docs/TASKS_C.md              成员 C 任务书
docs/templates/              三个代码骨架（划分 / CV 网格 / 数据契约测试）
```

## 7. 候选池与核验结论（2026-11-11 已核验 → **选定 UMAP**）

**选定：UMAP**（McInnes, Healy & Melville, arXiv:1802.03426, 2018），加权 93——唯一同时通过 9 项核验、1 小时冒烟与算力闸门的对象。
核验表、冒烟数据、评分与复现框架见 `docs/CANDIDATE_ASSESSMENT.md`；原文 `paper/umap_arxiv2018.{pdf,txt}`。

其余候选（各一句话，完整理由见评估文档 §2）：

| 候选 | 年份 | 否决理由 |
|---|---|---|
| HDBSCAN | 2013/2015 | 正文 PDF 全渠道不可得（ACM TKDD / Springer / JCU 仓库 401，无 arXiv）→ 协议不可核验 |
| LightGBM | 2017 | 原文实验为 LETOR/Allstate/KDD10 19M×29M 等，多需 Kaggle，7.5 GB 内存不可行 |
| NCF | 2017 | 核心 baseline eALS 无标准库实现 + 负采样/切分协议争议 |
| Geometric SMOTE | 2019 | 无官方代码 + 网格取最高分口径膨胀 + 与上轮 SMOTE 同族 |
| SHAP | 2017 | 核心主张依赖人因研究（不可复现）+ 需 TF1 时代 DeepLIFT 预训练 |
| TabPFN | 2023/2025 | 本体 8 GPU×20 h 预训练，只能「使用权重」而非复现 |
| Class-Balanced Loss | 2019 | 算力闸门：ResNet-32 CPU 实测 8.0 h/配置，主表约 20 天，无 GPU |
| Kovács 过采样基准比较 | 2019 | 算力闸门：全量 104×85 外推 ≈258 h 单核；列为备选 #2 |

出处更正：HDBSCAN 扩展版是 **ACM TKDD 10(1), 2015, DOI 10.1145/2733381**，不是 JMLR 2015。
