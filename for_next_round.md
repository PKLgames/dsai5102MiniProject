# 下一轮交接（换论文后从零开始复现）

> 读这一页 + `selecting_exp.md` 就可以开始，不需要读上一轮的对话或代码。
> 上一轮（SMOTE 复现）的工作区内容已全部删除，仅保留在 git tag `smote-repro-v1` 里（见 §8）。

## 1. 任务背景（不变）

- 任务原文：`/home/pklgames/coding/dsai5102MiniProject/project_request.txt`（Format 2.2 学术论文复现）
- 交付：报告 **2026-11-21 23:59**、Slides **2026-11-24 12:00**、答辩 **2026-11-25/26（6 分钟）**
- 评分维度：Time / Team / Slides / Completeness / Methodology / Novelty（映射见 `docs/REPORT_OUTLINE.md`）
- 报告硬性六节：引言 / 数据描述 / 方法 / 实验结果 / 讨论 / 结论；须写明数据来源与预处理
- 分工：**A**（主计划 + 主代码，与 agent 结对）、**B**（数据准备 + EDA）、**C**（报告 + slides）
- **新一轮新增约束：论文发表年份 2010–2020**，其余筛选口径不变（统计数据挖掘/机器学习核心方法、可复现、易写报告）

今天是 2026-11-11，距报告截止 10 天：**选题必须在 11-12 内定下**，否则报告时间不够。

## 2. 工作区当前状态

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
| `configs/ data/ results/ figures/ notebooks/ report/ slides/ src/ scripts/ tests/` | 空目录结构 + `.gitkeep` |

已删除（服务于上一轮论文）：`paper/`（PDF 与抽文本）、`data/raw|processed|manifests`、`results/*`、`figures/*`、
`report/c1_table.md`、`PLAN.md`、`src/*.py`、`scripts/*.py`、`tests/*.py`、`docs/PROTOCOL.md`、`docs/DEVIATIONS.md`、
`docs/RUN_STATUS.md`、`docs/DATA_CARD_TEMPLATE.md`、`docs/TASKS_B.md`（旧版）、旧 `requirements.txt`，以及离线交付包 tar.gz。

## 3. 第一步做什么（建议顺序，别跳）

1. **列候选池**：按 `selecting_exp.md` §5 的检查表，从 2010–2020 窗口里选 5–8 篇（§7 有候选池草稿，但**都未核验**）。
2. **核验 Top-2（约 20 分钟/篇）**：PDF 可取 → 实验表有 dataset+样本数 → 逐个数据集找 did/URL → 每个 baseline 能否直接 import。
3. **1 小时冒烟**：最好的一篇，单数据集 × 2 条件，看方向是否与原文一致；同时估单配置耗时。
4. **写协议**：`cp docs/TEMPLATE_PROTOCOL.md docs/PROTOCOL.md` 并填写（主张、等价判据、实验矩阵、偏离日志）。
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

## 7. 候选池草稿（年份已筛，**可复现性未核验**，下一篇会话第一步就是核验）

| 候选 | 年份 | 一句话 | 预期成本 | 报告可写性 | 待核验点 |
|---|---|---|---|---|---|
| HDBSCAN（Campello et al., PAKDD 2013 / JMLR 2015 扩展版） | 2013/2015 | 层次密度聚类，参数少、自动选簇数 | 低（`hdbscan` 包，CPU 分钟级） | 中（聚类评估需自选指标与数据集，原表可复现部分） | 原文数据集清单与评估协议；官方实现与论文版本差异 |
| SHAP（Lundberg & Lee, NeurIPS 2017） | 2017 | 加性特征归因的统一框架 | 低–中（`shap` 包，小表格数据集秒级） | 中–高（可做"一致性/局部准确性"实验 + 案例） | 原文的 human study 部分不可复现，需明确替换为定量实验 |
| Neural Collaborative Filtering（He et al., WWW 2017） | 2017 | 用 MLP 替代内积的协同过滤 | 中（MovieLens 1M，CPU 数小时，需 torch） | 高（协议争议本身可写一节，但复现难度上升） | 负采样数量/切分协议必须一致，否则结论不可比 |
| LightGBM（Ke et al., NeurIPS 2017） | 2017 | GBDT + 直方图/GOSS/EFB | 中–高（原文含 Higgs 等大集，7.5 GB 内存吃紧） | 高（加速比表格直观） | 需确认能否用小数据集复现其"速度/精度"主张 |
| UMAP（McInnes et al., arXiv 2018） | 2018 | 拓扑启发的降维 | 低（`umap-learn`，CPU 分钟级） | 中（可视化为主，定量指标弱，需自己加下游分类实验） | 原文对比方法与参数敏感性部分是否可完整复算 |
| （备选）CatBoost / TabNet / AutoInt | 2018–2019 | 梯度提升类别特征 / 表格深度模型 | 高（训练成本大） | 高 | 除非前五个都不可行，一般不选 |

选择建议：先核验 **HDBSCAN 与 SHAP**（成本最低、数据最容易齐），若两者都通过检查表，优先 HDBSCAN
（方法学分量更"统计 DM"、评估协议更唯一）；若需要更强的 Novelty 分，再考虑 NCF（但必须接受协议解释成本）。

## 8. 上一轮内容怎么找回（如果确实需要）

```bash
git tag -l                      # smote-repro-v1
git show smote-repro-v1:docs/PROTOCOL.md | head
git worktree add ../smote-old smote-repro-v1   # 完整检出到旁路目录（含当时的 src/ 与 results/）
```

git 仓库：`https://github.com/PKLgames/dsai5102MiniProject.git`（远程仍为空，**push 尚未成功**——
上一轮报错 `fatal: could not read Username for 'https://github.com': terminal prompts disabled`，需要 PAT 或 SSH key）。
