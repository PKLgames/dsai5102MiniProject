# 项目计划 · UMAP 复现（DSAI5102 Mini Project, Format 2.2）

> 版本 v1 · 2026-11-11 · 维护人：A（本机 `/home/pklgames/coding/dsai5102MiniProject`）
> 论文：McInnes, Healy & Melville, *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction*, arXiv:1802.03426 (2018)，DOI `10.48550/arXiv.1802.03426`
> 配套综述（非复现对象）：Healy & McInnes, *Uniform manifold approximation and projection*, Nat. Rev. Methods Primers 4:82 (2024)，DOI `10.1038/s43586-024-00363-x`，`paper/s43586-024-00363-x.pdf`
> 配套文件：`docs/PROTOCOL.md`（做什么 / 怎样算复现）、`docs/TASKS_B.md` + `docs/HANDOFF_B2A.md`（B 的活与交接核验）、`docs/TASKS_C.md`（报告与 slides）、`docs/DEVIATIONS.md`（偏离登记）、`docs/PAPER_NUMBERS.md`（原文数字）、`docs/RUN_STATUS.md`（每日状态）

---

## 0. 一句话

10 天内自己实现 UMAP 的四个算法部件（模糊单纯复形 / SmoothKNNDist / 谱初始化 / 负采样 SGD），在 5 个公开数据集上与 PCA、Laplacian Eigenmaps、t-SNE、`umap-learn` 对照，**逐条复现原文 4 条主张**（视觉质量、kNN 精度、稳定性、运行时间），并把原文只做定性的超参敏感性改造成**定量热力图**作为 Novelty。

不自研 t-SNE、不跑 LargeVis、不碰 GoogleNews——这些是"用别人的结果当基线"最浪费时间的地方。

## 1. 硬约束（来自 `project_request.txt`）

| 交付 | 截止 | 备注 |
|---|---|---|
| Report（PDF，六节 + 数据来源与预处理 + Statement of Individual Contribution） | **2026-11-21 23:59** | 命名 `DSAI5102_<GroupID>_Report.pdf` |
| Slides（8 页） | **2026-11-24 12:00** | 命名 `DSAI5102_<GroupID>_Slides.pdf` |
| Oral defence | 2026-11-25/26 | 6 分钟讲 + 提问 |

评分维度：Time（是否早于新论文）/ Team（分担）/ Slides / Completeness / Methodology / Novelty。
=> 对应策略：选 2018 论文（Time 稳）、B/C 有硬交付物（Team）、幻灯片模板从第 3 天就冻结（Slides）、四条主张全覆盖（Completeness）、有形式化定义与自研实现（Methodology）、有热力图扩展（Novelty）。

## 2. 成功标准（Definition of Done）

1. `docs/PROTOCOL.md` §5 的 C1–C4 每条都有判定：`复现 / 部分复现 / 未复现`，且证据能指到 `results/` 下具体文件的列；
2. 主表 = 5 数据集 × 5 方法 × k 网格，**逐折**结果入库（不是只存均值）；
3. 至少 1 个原文没有的扩展实验（超参热力图）+ 1 个稳健性检查；
4. 报告六节齐全，`docs/DEVIATIONS.md` 与正文"Limitations"一一对应；
5. 附录 B 的可复现命令在本机能一次跑通（`bash scripts/repro.sh`）；
6. slides 8 页、彩排 ≥2 次、6 分钟不超时。

## 3. 范围（Scope）

| 做 | 不做（并写进协议） |
|---|---|
| 自研 UMAP 核心（算法 1–5） | 自研 t-SNE / LargeVis |
| 复用 `umap-learn` 作参考实现与 sanity check | 复现 COIL-100、scRNA、Flow Cytometry、GoogleNews |
| PCA（sklearn）、LE（sklearn SpectralEmbedding）、t-SNE（sklearn） | 原文的 FIt-SNE、MulticoreTSNE（二进制依赖多、收益低） |
| kNN 精度、Procrustes 稳定性、运行时间、视觉质量 | 原文的 soft kNN 分类器（用 sklearn KNeighborsClassifier 代替） |
| 超参热力图（n_neighbors × min_dist） | 理论部分（拓扑推导）只综述不复算 |
| 定性图 5 数据集 | UMAP 的 `transform` 泛化 |

## 4. 里程碑与质量门

`Gx` 是硬门，不达标不进入下一阶段（宁可降级 scope，不可带着坏数据往前走）。

| 门 | 时间 | 负责人 | 产物 | 通过条件 |
|---|---|---|---|---|
| **G0 协议冻结** | ~~11-12 12:00~~ **11-11 22:00 ✅ 已完成** | A | `docs/PROTOCOL.md` v1、`docs/DEVIATIONS.md` | C1–C4 有可判定阈值；数据表出处齐全 |
| **G1 A 侧契约** | 11-13 22:00 | A | `src/data.py` + `tests/test_data_contract.py` 绿 | `pytest -q` 通过；只用 `data/raw` 直读，**不等 B** |
| **H1 数据可达** | **11-13 22:00**（B 11-13 才能开工） | B→A | 每个数据集的 `(n, d)` 实测 + 下载耗时 | 5 数据集全部能 `load_raw()`；A 用 V0–V1 核验通过 |
| **H2 数据包** | **11-14 22:00** | B→A | `data/processed/*.npz` + manifest + `splits.json` | V1–V6 全通过；与 A 的 npz 逐元素相等（V4） |
| **G2 自研可用** | **11-15 22:00** | A | `src/umap_impl/` 在 PenDigits 上 ≈ `umap-learn` | 2D 嵌入 kNN 精度差 ≤0.02；不出现 NaN/塌缩 |
| **G3 主表** | **11-17 22:00** | A | `results/grid_knn*.csv` + 3 张图 | 5 数据集 × 5 方法 × k 全齐，逐折可追 |
| **G5a 数字 v1** | **11-18 22:00** | A→C | `results/README_numbers.md` v1（主表数字 + Fig.2/3） | C 能先写 §4 主体，不必等 G4 |
| **H3 数据卡终版** | **11-18 22:00** | B→A | `docs/DATA_CARD.md` + EDA 图 | V7–V8 通过 |
| **G4 扩展** | **11-19 22:00** | A | 热力图 + `results/extension_*.csv` | 48 配置跑完，结论非平凡 |
| **G5 交付终版** | **11-19 24:00** | A→C | `README_numbers.md` 终版 + 全部图 | C 能只靠该文件写报告 |
| Report v1 | **11-20 12:00** | C | `report/report_v1.pdf` | 六节齐全 |
| Report final | 11-21 23:59 | C（A 审） | 提交版 PDF | 数字全部对齐 `README_numbers.md` |
| Slides | 11-24 12:00 | C | 8 页 PDF | 彩排 2 次，6 分钟 |

**缓冲与空转（2026-11-11 用户决定：允许一定空转）**

- 每个门后面留 **≥3 h 缓冲**，排期不按 100% 利用率算；A 在 11-13 白天等 B 数据的时间是**计划内的空转**，不用拿 B 的活来填。
- 空转的正确用法：A 用自己的 `src/data.py` 直读 `data/raw`（PenDigits 走 sklearn、COIL-20 本地已有）继续推 A2，只把"对拍"留给 H2；**不等于接管 B 的取数脚本**。
- 只有 H1 在 **11-13 24:00 仍未过** 时才触发 R6 兜底（A 自建并标注"A 侧产出，B 未交付"）。
- 顺延规则：H1 每滑 1 天，G2/G3/G5a 各滑 1 天，但 **Report final 11-21 23:59 不动**——从 G4（扩展）里扣，最后 2 天不许再压 C 的写作时间。

## 5. 工作分解（WBS）

### A（主计划 + 主代码 + 出图，本机）

| ID | 任务 | 估时 | 依赖 | 产出 |
|---|---|---|---|---|
| A0 | 协议/偏离日志/论文数字表定稿 | 3 h | — | `docs/PROTOCOL.md`、`DEVIATIONS.md`、`PAPER_NUMBERS.md` |
| A1 | `src/data.py` 独立 loader + 契约测试 | 3 h | A0 | `src/data.py`、`tests/test_data_contract.py` |
| A2 | `src/umap_impl/{fuzzy,spectral,optimize,umap}.py` | 16 h | A1 | 自研实现 + `tests/test_umap_impl.py`（与 `umap-learn` 对拍） |
| A3 | `src/knn_eval.py`、`src/procrustes.py`、`src/timing.py` | 4 h | A1 | 三个评估模块 + 单测 |
| A4 | `scripts/run_grid.py`（主表，支持断点续跑） | 4 h | A3 | `results/grid_knn.csv`（逐折） |
| A5 | `scripts/run_stability.py`、`scripts/run_runtime.py` | 3 h | A3 | `results/stability_*.csv`、`results/runtime_*.csv` |
| A6 | `scripts/run_extension.py`（超参热力图） | 3 h | A4 | `results/extension_heatmap.csv` |
| A7 | `scripts/make_figures.py` → Fig.1–5 | 4 h | A4–A6 | `figures/results/*.png`（300 dpi） |
| A8 | `results/README_numbers.md`（C 的唯一数字来源） | 4 h | A7 | 结论表 + 与原文的差价表 |
| A9 | 敏感性分析（COIL-20 k=160 缺口、缩放不变性、子采样影响） | 6 h | A4 | `results/sensitivity_*.csv` |
| A10 | `scripts/repro.sh`（附录 B 的命令） + README 收尾 | 2 h | 全部 | 一条命令复现主表 |

### B（数据准备 + EDA）

| ID | 任务 | 估时 | 时点 | 产出 |
|---|---|---|---|---|
| B1 | `scripts/fetch_data.py`：5 个源可重复下载（校验 sha256） | 3 h | 11-13 | `data/raw/` |
| B2 | `src/data_prep.py`：独立 loader → 规范 npz + manifest | 5 h | 11-13→14 | `data/processed/*.npz`、`data/manifests/*.json` |
| B3 | `splits.json`（按 `configs/main.yaml` 的折数） | 1 h | 11-14 | `data/manifests/splits.json` |
| B4 | `docs/DATA_CARD.md` 填满（6 节 + 行号引用） | 3 h | 11-14→18 | 数据卡 |
| B5 | 6 张 EDA 图（类分布/样本网格/像素直方/类均值/PCA 散点/重复与缺失） | 4 h | 11-16→18 | `figures/eda/*.png` |
| B6 | 交接（跑 `docs/HANDOFF_B2A.md` 自查表，写 `HANDOFF_LOG.md`） | 2 h | 11-13/14/18 | 交接记录 |

### C（报告 + slides）

| ID | 任务 | 估时 | 时点 | 产出 |
|---|---|---|---|---|
| C1 | 骨架 + Fig.1（方法示意）+ §2 相关工作（读原文 + 综述） | 4 h | 11-13 | `report/outline.md`、`figures/results/fig1_method.png` |
| C2 | §1/§3 方法（按 `PAPER_NUMBERS.md` 与协议写） | 4 h | 11-15 | 草稿 |
| C3 | §4 结果（用 `README_numbers.md` 填表，禁止自算数字） | 6 h | 11-18 | 草稿 + Fig.2/3 |
| C4 | §5 讨论（偏离清单 → Limitations）、§6 结论、贡献声明 | 3 h | 11-19 | 草稿 |
| C5 | 排版、图注、数字复核（与 A 逐项对表） | 3 h | 11-20 | v1 PDF |
| C6 | slides 8 页 + 讲稿 + 彩排 2 次 | 6 h | 11-22/23 | Slides PDF |

## 6. 关键路径

```
A0 ──> A1 ──> A2 ──> A4 ──> A7 ──> A8 ──> C5/C6
        │      └────> A5/A6 ──┘
B1 ──> B2 ──> B3 ──┘
C1（不依赖数据，先写方法与相关工作）
```

- 唯一真正的瓶颈是 **A2（自研 UMAP 正确性）**。**11-15 22:00** 是硬检查点：若 G2 未过，按 §8 R1 降级（不占用 C 的写作时间）。
- **A1 不等 B**：`src/data.py` 直接读 `data/raw`（PenDigits 用 sklearn、COIL-20 已下载），B 的 npz 只用于 V4 对拍。H1 定在 **11-13 22:00**（B 11-13 才能开工）；11-13 24:00 还没过才走 R6 兜底。
- C 的 C1 不依赖任何数据，必须并行启动，避免最后两天才写。

## 7. 算力与内存预算（本机 16 vCPU / ~7.5 GB / 无 GPU / 单线程有效）

冒烟实测（`results/smoke_umap/*.json`）：PenDigits t-SNE 10.8 s、UMAP 12.2 s；COIL-20（1440×16384）t-SNE 9.5 s、UMAP 17.4 s。

| 实验 | 规模 | 单次预估 | 次数 | 合计 |
|---|---|---|---|---|
| 主表嵌入 | PenDigits 1797×64 | ~15 s | 5 方法 | <2 min |
| 主表嵌入 | COIL-20 1440×16384 | ~20 s | 5 方法 | <3 min |
| 主表嵌入 | Shuttle 58k×9 | PCA 2 s / LE 2–5 min / t-SNE **8–20 min** / UMAP 2–3 min | 5 方法 | 15–30 min |
| 主表嵌入 | MNIST 20k×784、F-MNIST 20k×784 | t-SNE 2–4 min / UMAP 1–2 min | 各 5 方法 | 30–50 min |
| 分类评估 | 25 组嵌入 × ≤5 个 k × 5–10 折 | 秒级 | 全覆盖 | <20 min |
| 稳定性 | Shuttle/COIL-20 × 4 个采样率 × 3 方法 × 3 seed | 分钟级 | 72 次嵌入 | 1.5–3 h |
| 运行时间 | 5 数据集 × 4 方法 × 3 次 | 同上 | 60 次 | 1–2 h |
| 扩展热力图 | PenDigits + COIL-20 × 6×4 配置 | ~12–20 s | 48 次 | ~15 min |
| 敏感性 | COIL-20 k=160 变体 × ~8 组 + 缩放 3 组 | 分钟级 | ~11 | ~30 min |

总量约 **5–6 小时纯计算**，10 天窗口内可从容重跑 2 次。内存：MNIST 20k 的 kNN 图最坏 20000² 稠密 = 3.2 GB（float32）——**必须稀疏化**（`scipy.sparse` 每点 ≤ n_neighbors×3 nnz），否则会 OOM。

## 8. 风险登记

| ID | 风险 | 触发信号 | 缓解 | 降级方案（预案） |
|---|---|---|---|---|
| R1 | 自研实现不收敛 / 与 `umap-learn` 差太远 | 11-15 22:00 前 PenDigits 精度差 >0.02 或 NaN | 逐部件对拍（先只换 fuzzy 图，再换谱初始化，再换 SGD）；用 `umap-learn` 的 4 个部件做参照 | 自研只保留 fuzzy + 谱初始化（可证明正确），SGD 用 `umap-learn` 的 `optimize_layout_euclidean`；报告如实写"部分自研"，Methodology 打分不受致命影响 |
| R2 | OpenML 下载慢/失败（MNIST 70k、Shuttle） | H1 时单集 >20 min 或 5xx | 重试 + 镜像（`data.ilarum` / sklearn `fetch_openml` cache）；npz 缓存 | 用许可的镜像存档（HuggingFace `ylecun/mnist` parquet）并在数据卡注明；F-MNIST 用 `zalando` 官方 GitHub 的 4 个 gz |
| R3 | Shuttle 58k 上 sklearn t-SNE 超 30 min | A5 预跑测得 | 先 5k 子采样测速 ×12 外推 | **对 Shuttle 全部方法统一用 20k 分层子采样**（同 seed），C2 中 Shuttle 标注"缩小口径"，进偏离日志；不比不齐的数据 |
| R4 | LE（谱嵌入）在 58k 上 eigensolver 失败 | `ArpackError` / 内存 | `eigsh` + `which='SM'`，或先 PCA-50 再 LE | 只在小数据集上跑 LE，报告注明（原文本来就只在小数据上有 LE 数字） |
| R5 | COIL-20 大 k 复现失败（已发生：k=80 我们 .806 vs 原文 .899） | 已在冒烟中 | 按协议降级为"部分复现"，补敏感性分析定位原因（像素缩放、n_neighbors=15 vs 原文未披露、2D 维数） | 已在 `DEVIATIONS.md` 登记，报告 §5 用一段讨论，不算失败而是"可解释的偏差" |
| R6 | B 交接迟到 / 质量不过 | H1 到 11-13 24:00 仍未过 V0–V1，或 H2 到 11-14 24:00 未过 V1–V6 | A 用 `src/data.py` 自建 processed（B 的 loader 本来就要求独立实现，A 这份是"第二实现"） | B 转为只交 EDA + 数据卡；Team 维度在报告里如实写分工 |
| R7 | 时间滑到 11-18 还未出主表 | G3 未过 | 砍扩展（A6）与 A9，保主表 | 最小可交付 = PenDigits + COIL-20 + Shuttle 三集 × 4 方法；MNIST 系列降为附录单 k |
| R8 | 内存 OOM（7.5 GB，available ~4 GB） | 进程被 OOM kill | 稀疏化、float32、`n_epochs` 分批、避免 3 份拷贝 | 降低 MNIST 子采样到 10k×5 折（偏离日志） |
| R9 | 无中文字体导致图内乱码 | 图出现方框 | 图内全部英文（已定） | 报告正文中文、图英文，不影响评分 |

## 9. 协作与所有权

- **分支**：`main`（稳定，只由 A 合并）、`feat-umap`（A）、`data-prep`（B）、`report`（C）。B/C 只在自己的分支上提交，A 用 `git merge --no-ff` 合并并打 tag（`handoff-h1` / `handoff-h2` / `handoff-h3`）。
- **文件所有权**（防止互相覆盖）：

| 路径 | 所有者 | 其他人 |
|---|---|---|
| `src/umap_impl/**`、`src/knn_eval.py`、`src/procrustes.py`、`scripts/run_*.py`、`configs/**` | A | 只读 |
| `src/data.py`、`tests/**` | A | 只读 |
| `src/data_prep.py`、`scripts/fetch_data.py`、`data/**`、`docs/DATA_CARD.md` | B | A 只读 `data/processed`；不得改 B 的脚本 |
| `docs/PROTOCOL.md`、`docs/DEVIATIONS.md`、`docs/HANDOFF_B2A.md`、`PLAN.md` | A | B/C 可提 issue，不改 |
| `report/**`、`slides/**` | C | A 只审不改 |
| `docs/TASKS_*.md`、`docs/REPORT_OUTLINE.md` | A 起草，C 可补 | — |

- **每日 22:00** 更新 `docs/RUN_STATUS.md`（负责人 + 计划 vs 实际 + 阻塞）。
- **commit 规范**：`<area>: <what>`，area ∈ {data, impl, eval, fig, docs, report}；每个 commit 只做一件事。
- **数字纪律**：报告里每个数字必须能在 `results/` 找到对应行；禁止口头/手抄数字（C 只从 `results/README_numbers.md` 取值）。
- **AI 使用**：本项目的 AI 辅助范围写入报告 Statement of Individual Contribution（哪些代码/文字由 AI 生成、由谁审校）。

## 10. 结果 → 报告映射

| 报告位置 | 数据来源 |
|---|---|
| Fig.1 方法流程 | 手绘/`figures/results/fig1_method.png`（C 负责） |
| Fig.2 定性对比（5 数据集 × 4 方法） | `figures/results/fig2_qualitative.png`（A7） |
| Table 1 kNN 精度（本机 vs 原文） | `results/grid_knn_summary.csv` + `docs/PAPER_NUMBERS.md` |
| Fig.3 原文 vs 我们 散点（45 点） | `results/paper_vs_ours.csv`（A8） |
| Fig.4 稳定性 | `results/stability_procrustes.csv` |
| Fig.5 超参热力图 | `results/extension_heatmap.csv` |
| Table 2 运行时间 | `results/runtime.csv` |
| §5 Limitations | `docs/DEVIATIONS.md` 逐条转写 |

## 11. 第一天就做的三件事（今天 11-11 夜）

1. `git checkout -b main-v2`，提交本计划 + 协议 + 偏离日志 + 论文数字表（本文件即为第一步）；
2. 给 B 发 `docs/TASKS_B.md` + `docs/HANDOFF_B2A.md`，明确 H1 = **11-13 22:00**（B 11-13 开工）；
3. 给 C 发 `docs/TASKS_C.md` + `docs/PAPER_NUMBERS.md`，要求 11-13 交骨架与 Fig.1。
