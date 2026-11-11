# 下一轮交接（换论文后从零开始复现）

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
| `docs/CANDIDATE_ASSESSMENT.md` | 2026-11-11 候选池可行性评估（9 项核验表 + 评分卡 + 冒烟结果 + 选定后框架 + 预登记偏离） |
| `paper/` | 6 篇候选 PDF + 抽取文本（umap/shap/ncf/lightgbm/tabpfn/gsmote）；HDBSCAN 正文不可得，未存 |
| `scripts/smoke_umap.py` + `results/smoke_umap/{digits,coil20}.json` | UMAP 冒烟脚本与结果（PenDigits/COIL-20 的 kNN 表） |
| `data/raw/coil20/coil-20-proc/` | COIL-20 解压后的 1440 张 128×128 PNG（不入库，可重下） |
| `configs/ data/ results/ figures/ notebooks/ report/ slides/ src/ scripts/ tests/` | 空目录结构 + `.gitkeep` |

已删除（服务于上一轮论文）：`paper/`（PDF 与抽文本）、`data/raw|processed|manifests`、`results/*`、`figures/*`、
`report/c1_table.md`、`PLAN.md`、`src/*.py`、`scripts/*.py`、`tests/*.py`、`docs/PROTOCOL.md`、`docs/DEVIATIONS.md`、
`docs/RUN_STATUS.md`、`docs/DATA_CARD_TEMPLATE.md`、`docs/TASKS_B.md`（旧版）、旧 `requirements.txt`，以及离线交付包 tar.gz。

## 3. 第一步做什么（建议顺序，别跳）

1. ✅ **列候选池**（2026-11-11 完成）：7 篇，见 §7 与 `docs/CANDIDATE_ASSESSMENT.md`。
2. ✅ **核验**（2026-11-11 完成）：7 篇全部过检查表，PDF 已入 `paper/`（HDBSCAN 正文不可得，一票否决）。
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

## 7. 候选池与核验结论（2026-11-11 已核验 → **选定 UMAP**，详见 `docs/CANDIDATE_ASSESSMENT.md`）

| 候选 | 年份 | 一句话 | 预期成本 | 报告可写性 | 核验结果 |
|---|---|---|---|---|---|
| **UMAP**（McInnes et al., arXiv:1802.03426） | 2018 | 拓扑启发的降维 | 低（`umap-learn`，CPU 分钟级） | 中（可视化为主，定量指标弱，需自己加下游分类实验） | ✅ **通过，加权 93，选定**：5 个有标签数据集全部可核；kNN 口径可三行复算；单次嵌入秒级；仅 LargeVis 无 pip 实现（写偏离） |
| HDBSCAN（Campello et al., PAKDD 2013 / 扩展版 **ACM TKDD 10(1) 2015**, DOI 10.1145/2733381） | 2013/2015 | 层次密度聚类，参数少、自动选簇数 | 低（`hdbscan` 包，CPU 分钟级） | 中（聚类评估需自选指标与数据集，原表可复现部分） | ❌ **一票否决**：正文 PDF 全渠道不可得（Semantic Scholar CLOSED、OpenAlex is_oa=false、JCU 401、ACM/Springer 拦截）→ 无法核对实验表 |
| SHAP（Lundberg & Lee, NeurIPS 2017） | 2017 | 加性特征归因的统一框架 | 低–中（`shap` 包，小表格数据集秒级） | 中–高（可做"一致性/局部准确性"实验 + 案例） | ⚠️ 备选，加权 78：§5.2 人因研究（MTurk 30/52 人）不可复现、§5.3 依赖 TF1 的 DeepLIFT 预训练；Fig.3 训练数据正文未给 |
| Neural Collaborative Filtering（He et al., WWW 2017） | 2017 | 用 MLP 替代内积的协同过滤 | 中（MovieLens 1M，CPU 数小时，需 torch） | 高（协议争议本身可写一节，但复现难度上升） | ❌ 加权 68：核心 baseline **eALS 无标准库**（必须自实现）+ leave-one-out/4 负样本协议争议 |
| LightGBM（Ke et al., NeurIPS 2017） | 2017 | GBDT + 直方图/GOSS/EFB | 中–高（原文含 Higgs 等大集，7.5 GB 内存吃紧） | 高（加速比表格直观） | ❌ 加权 53：原文实验为 LETOR/Allstate/KDD10 19M×29M/KDD12 119M×54M，多需 Kaggle，7.5 GB 内存不可行 |
| Geometric SMOTE（Douzas & Bacao, *Information Sciences* 501:118–135） | 2019 | 在少数类超球体内按截断因子生成样本，"drop-in 替换 SMOTE" | 低（算法本体 <400 行，CPU 分钟级） | 中–高（几何直觉好讲；但原表是 30+ 数据集的 AUC 大表，需挑 6–8 个复现） | ❌ 加权 71：**无官方代码**（作者 GitHub 404、PyPI 404、imbalanced-learn 0.14.2 无此类）；13 数据集 × 2 分类器 × 网格取最高 CV 分的口径重且易膨胀；与上轮 SMOTE 同族 |
| TabPFN / 表格基础模型（Hollmann et al., *Nature* 637:319–326；源头 ICLR 2023） | 2025 | 先验数据拟合网络（PFN），一次前向完成小表格分类 | 中–高（需 torch + 预训练权重；`tabpfn` 9.2.0 要求 Python ≥3.10，本机 3.14 兼容性未知；CPU 可推理但"打败调参树模型"的基准本身很重） | 高（"基础模型 vs 调参树模型"话题性强，答辩好讲） | ❌ 加权 80 但**只能"使用"权重**：核心方法 8 GPU×20 h 预训练，本体无 GPU；flagship 对比需每数据集 1 h AutoML（AutoGluon），18 数据集不可行 |
| （备选）CatBoost / TabNet / AutoInt | 2018–2019 | 梯度提升类别特征 / 表格深度模型 | 高（训练成本大） | 高 | 未核验（按需再议，不推荐） |

核验后的选择（取代旧建议）：**UMAP 为主复现对象**；SHAP 作备选（若 11-12 前 UMAP 自研实现遇阻）。
历史建议（保留备查）：原计划先核验 HDBSCAN 与 SHAP、都过则优先 HDBSCAN——实际 HDBSCAN 因正文 PDF 不可得被否。

增补说明（用户 m00654 点名加入；m00715 把年份窗口放宽到「2010 至今」）：

- **Geometric SMOTE**：年份 2019 合规，但它是"又一个采样器变体"，与刚放弃的 SMOTE 同族，题面差异化弱；
  且作者未公开代码，等于要连算法带基准一起重写，报告里"复现"的分量反而下降。
- **TabPFN**：年份窗口已不再是障碍（m00715 裁决：窗口放到 2010 至今）。剩下两个真实风险：
  ① 工程：torch + 预训练权重 + Python 3.14 兼容性，需要一次安装冒烟；
  ② 方法学：只跑官方模型是"使用"不是"复现"，要复现其"打败调参树集成"的主张，得自己搭多数据集 + 固定调参预算的基准，
     这部分工作量大于 HDBSCAN/SHAP，但报告 Novelty 与答辩效果也最好。
  可折中：主体复现一篇 2010 之后的表格方法（如 HDBSCAN/SHAP），把 TabPFN 作为扩展对照基线。
