# 计划 · UMAP 复现（执行版 v3 · 2026-11-12）

> 论文：[1] McInnes, Healy & Melville, *UMAP*, arXiv:1802.03426 (2018)；配套综述 [2] Healy & McInnes, *Nat. Rev. Methods Primers* 4:82 (2024)。
> 口径（做什么、怎么算成功、原文数字）：`docs/goal/SPEC.md`、`docs/goal/PAPER_DATA.md`。
> 本文件只做两件事：**排节点（P）**、**约定交付物（S）**。每个人的详细做法与验收在 `docs/tasks/`，进度与偏离在 `docs/log/`。

## 编号规则（全文只有两套）

| 编号 | 含义 | 例子 |
|---|---|---|
| **P1–P15** | 工作节点（谁在做什么） | P2 数据契约、P11 结果图 |
| **S1–S6** | 提交成果（发出去的东西） | S2 数据包、S5 报告 PDF |

除此之外**没有第三套计划编号**：旧的 G（质量门）/H（交接点）/V（核验项）编号已全部废除。
- `docs/goal/SPEC.md` 内部用 **R1–R9** 指代预处理规范、**E1/E2/E4** 指代评估口径，仅是条款代号，不参与计划编排。
- **D** 是偏离日志条目（`docs/log/DEVIATIONS.md`），报告中按 D 编号引用，便于附录索引。

## 1. 冻结范围

| 做 | 不做（本轮已预授权放弃） |
|---|---|
| **C2**：kNN 精度随 k 的变化（唯一被复现的主张） | C3 稳定性（Procrustes）、C4 九数据集时间表、超参热力图 |
| **PenDigits 1797×64 + COIL-20 1440×16384**，原规模、10 折分层 | MNIST/Fashion-MNIST（70k）、Shuttle（58k）、COIL-100、scRNA、Flow、GoogleNews |
| k ∈ {10,20,40,80,160}，同一嵌入评 5 个 k | LargeVis、LE、自研 t-SNE、`transform` 泛化 |
| 方法：PCA、t-SNE（sklearn）、UMAP（umap-learn）、UMAP（自研） | 三人盲评 C1 正式评分（图只作定性展示） |
| 附带：COIL-20 定性图 1 张、4 行 fit 时间表 | — |

**算力**：整轮主表 ≈30 min（PenDigits ≈6 min、COIL-20 ≈8 min、重跑 15 min）。真正的成本是开发时间，所以砍的是方法/数据集，不是判据的严格性。

## 2. 节点表（P）

### 轨道 A · 计算（唯一前置：`data/raw` 已在盘上）

| 节点 | 产物 | 完成判据 | 依赖 |
|---|---|---|---|
| **P1** 环境与冒烟 ✅ 11-10 | 环境事实 + 冒烟数字（记入 `docs/log/RUN_LOG.md`） | 依赖可 import；PCA/t-SNE/UMAP 各跑通一次 | — |
| **P2** 数据契约 | `src/data.py`（raw→canonical）、`tests/test_data_contract.py` | `pytest -q` ≥6 用例全绿；两次运行 `array_sha256` 相同；不依赖任何他人文件 | P1 |
| **P3** 自研前两件 | `umap_impl/fuzzy.py`、`umap_impl/spectral.py` | ρ/σ 与 umap-learn 相对误差 <1e-6；谱初始化符号对齐后余弦 >0.99 | P2 |
| **P4** 自研闭环 | `umap_impl/optimize.py`、`umap_impl/umap.py` | PenDigits 上自研 vs 参考 kNN@10 差 ≤0.02；无 NaN；silhouette >0.1 | P3 |
| **P5** 主表 | `results/grid_knn.csv`(400 行)、`runtime.csv`、`paper_vs_ours.csv`、`results/embeddings/coil20_*.npz` | 2 数据 ×10 折×4 方法×5 k = 400 行；**重跑逐折差 = 0**；时间表有实测值 | P2,P4 |
| **P6** 数字终版 | `results/README_numbers.md` 终版 | 每个数字能指到 csv 行；结构与 S1 模板逐键一致；含判定词 | P5 |

### 轨道 B · 数据（唯一前置：S1 的签名）

| 节点 | 产物 | 完成判据 | 依赖 |
|---|---|---|---|
| **P7** 数据包 | `data/processed/*.npz`、`data/manifests/*.json` | n/d 精确（1797×64 / 1440×16384）；dtype/取值域/`array_sha256` 自洽 | S1 |
| **P8** 折划分 | `scripts/make_splits.py`、`splits.json` | 10 折、`train∩test=∅`、折大小差 ≤1、重跑字节相同 | P7 |
| **P9** 审计对拍 | `docs/log/HANDOFF_LOG.md` 一行 | 自己 npz vs A canonical 数组 `max|dX|=0`、标签全等；不等则开 D 条目 | P7,P2 |
| **P10** 数据卡 + EDA | `docs/goal/DATA_CARD.md` 终版、`figures/eda/eda_01..03` | 每条流程带 `data_prep.py:行号`；dpi ≥160；无中文方框 | P7 |
| **P11** 结果图 | `figures/results/fig2_*.png`、`fig3_*.png` | 300 dpi；点数与 `paper_vs_ours.csv` 一致；英文标注 | S3 |

### 轨道 C · 写作（唯一前置：S1 的占位模板）

| 节点 | 产物 | 完成判据 | 依赖 |
|---|---|---|---|
| **P12** 骨架 + 无数字章节 | `report/` 骨架、Fig.1、§1/§2/§3 | §3 ≤2 页；引用 ≤15 条；图全部自绘 | S1 |
| **P13** 结果节（占位版） | §4 + 表 1–4 版式 | 数字全部写成占位符，无手打数字 | P12 |
| **P14** 替换定稿 | §4 + 表 1–4 终值 | `grep '{{'` 为空；逐项与 `README_numbers.md` 一致 | P13,S3 |
| **P15** 报告终稿 + slides | S5、S6 | 见 `docs/tasks/C_ACCEPTANCE.md` | P14 |

## 3. 交付物表（S）与流程依赖图

| 成果 | 内容 | 谁发 | 给谁 | 时间 |
|---|---|---|---|---|
| **S1** | `src/data.py` 签名 + `tests/` + `results/README_numbers.md` 占位模板 | A | B、C | Day1 10:00 |
| **S2** | npz + manifest + splits + `make_splits.py` | B | A（审计） | Day1 22:00 |
| **S3** | `results/*.csv` + `embeddings/*.npz` + 数字终版 | A | C、B | Day2 22:00 |
| **S4** | `figures/results/fig2_*.png`、`fig3_*.png` | B | C | S3 + 3 h |
| **S5** | `DSAI5102_<GroupID>_Report.pdf` | C | 课程 | 11-21 23:59 |
| **S6** | `DSAI5102_<GroupID>_Slides.pdf` | C | 课程 | 11-24 12:00 |

```
Day1 10:00         Day1 22:00            Day2 22:00        +3 h
   S1                 S2                    S3              S4
    │                  │                     │               │
────┴──────────────────┴─────────────────────┴───────────────┴──────
A  P1 ─► P2 ─► P3 ─► P4 ─► P5 ─► P6
         │                          └─► S3（csv + embeddings 导出）
         └─► S1（签名 + tests + 数字模板）

B  P7 ─► P8 ─► P10 ────────────────(读 S3)──► P11 ─► S4
    └─► P9（对拍 A 的 canonical，不进 A 的计算路径）
   S1 ─┘（只等签名）

C  P12 ─► P13 ───────────(S3 到达)──► P14 ─► P15 ─► S5/S6
    └─ S1 的占位模板
```

**读法**：箭头是「产物流向」，不是「人停机」。除 S1/S2/S3/S4 四次取文件外，三条轨道互不等待；S2 晚只让 P7/P9/P10 变红，S3 晚只让 P14 保留占位符。

## 4. 放弃顺序与降级（按轨道各自降，不连带别人）

1. 先砍**自研 SGD**：P3+P4 降级为「自研 fuzzy + 谱初始化 + 参考实现 SGD」，报告写"部分自研"；
2. 再砍 **COIL-20 的 t-SNE 对照**（只报 UMAP vs PCA）——尽量不砍；
3. 再砍 **定性图（Fig.2）与时间表**；
4. **绝不砍**：P2（契约）、P5（主表）、P6（数字）。

| 谁掉线 | 别人照常 | 缺的怎么补 |
|---|---|---|
| B 的 P7/P8 晚 | A 用 canonical 跑完；C 写 §1/§2/§3 | 报告 §3 用 A 的数据卡简版，注明「B 侧未完成」 |
| B 的 P10 晚 | A/C 不等 | EDA 图从报告删除 |
| B 的 P11 晚 | A 的 P6、C 的 P13 不受影响 | A 用同一脚本 30 min 出 Fig.2 简版 |
| A 的 P4 失败 | B/C 不受影响 | 报告写「部分自研」，C 用 `umap_ref` 数字先填 |
| A 的 P6 晚 | C 保留占位符 | 11-18 报告 v1 前补上即可 |
| C 的 P12 晚 | A/B 不受影响 | A 在 11-14 顶替骨架 |

## 5. 两天之外的里程碑

| 日期 | 交付 |
|---|---|
| 11-14 → 11-17 | C 写 §1/§5/§6；A 补「我们 vs 原文」诊断（COIL-20 大 k 未复现的归因，见 D9）；B 维护数据卡 |
| 11-18 | 报告 v1（六节齐全，数字与 `README_numbers.md` 对齐） |
| 11-19 → 11-20 | 查重（8-gram <5%）、图注、参考文献、贡献声明；A 复核数字 |
| 11-21 23:59 | **S5 提交** |
| 11-22 → 11-24 12:00 | **S6** slides 8 页 + 2 次彩排（6 分钟） |

## 6. 团队约定

- 在线 **09:00–23:00**；每天 10:00 / 15:00 / 22:00 三次同步，每次 10 分钟，只报「节点状态 + 阻塞」。
- 阻塞 30 min 内提出；跨角色改动在 `docs/log/HANDOFF_LOG.md` 留一行。
- 谁延期由 **A 当场按 §4 改派**；不新增实验、不新增数据集。
- 仓库只有 `main` 一个分支；B/C 需要时开短命分支，合并后删掉。

## 7. 文件地图（谁看什么、填什么）

| 角色 | 必读 | 要填 | 要产出 |
|---|---|---|---|
| A | `PLAN.md`、`docs/goal/SPEC.md`、`docs/tasks/A_TASKS.md`、`docs/goal/PAPER_DATA.md` | `docs/log/RUN_LOG.md`、`docs/log/DEVIATIONS.md`、`results/README_numbers.md` | P2–P6 的代码与结果；S1、S3 |
| B | `PLAN.md`、`docs/tasks/B_TASKS.md`、`docs/tasks/B_ACCEPTANCE.md`、`docs/goal/SPEC.md` §2–§3 | `docs/goal/DATA_CARD.md`、`docs/log/HANDOFF_LOG.md` | P7–P11 的数据与图；S2、S4 |
| C | `PLAN.md`、`docs/tasks/C_TASKS.md`、`docs/tasks/C_ACCEPTANCE.md`、`results/REPORT_MAP.md` | `report/`、`slides/` | P12–P15；S5、S6 |
| 三人 | `docs/log/RUN_LOG.md`（每天一眼）、`docs/log/DEVIATIONS.md`（改口径前必读） | — | — |
