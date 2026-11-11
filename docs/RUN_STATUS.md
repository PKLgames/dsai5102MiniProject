# 运行状态板（RUN STATUS）

> 每天 22:00 由 A 更新。三行规则：**只写事实**（命令跑过就是跑过）、**只写阻塞**（不是计划）、**每个 pending 都有日期**。
> 交付点 P1–P9 定义见 `PLAN.md` §2；B→A 交接的核验命令见 `docs/HANDOFF_B2A.md`（V0–V8）。

## 当前状态 · 2026-11-11（周三）夜 · 计划 v2

| 项 | 状态 |
|---|---|
| 阶段 | **两日核心计划启动**：只复现 C2，只跑 PenDigits + COIL-20（`PLAN.md` v2，`DEVIATIONS` D18） |
| 为什么缩 | v1 全量 ≈5–6 h 算力 + ≈20 h 开发，两天窗口装不下；砍数据集与方法数，**不砍判据**（C2 仍是原规模、原折数） |
| 已完成 | 论文筛选、候选核验、冒烟（PenDigits/COIL-20 × PCA/t-SNE/UMAP）、环境、数据源试探、书目核对；计划/协议/偏离/交接/任务书成文（PROTOCOL **v2**、D1–D18） |
| 进行中 | A：`src/data.py` + 契约测试（只读 `data/raw`，不等 B）；B/C 任务书已按 2 数据集改写待发 |
| 阻塞 | 无 |
| 下一步 | 11-12：B 交 P1 数据冻结；A 交 P2 契约、P3 自研前两件；C 交 P4 骨架 |

### 交付点追踪（P1–P9，`PLAN.md` §2）

| 点 | 负责人 | 到期 | 状态 | 证据 / 验收命令 |
|---|---|---|---|---|
| **P1** 数据冻结（2 数据集 npz+manifest+splits） | B | 11-12 | ⚪ 未开始 | A 跑 `HANDOFF_B2A.md` V0–V5 |
| **P2** 数据契约（`src/data.py` + pytest） | A | 11-12 | 🟡 进行中 | `pytest -q`；`max|dX|=0` 对 P1 |
| **P3** 自研 fuzzy + spectral | A | 11-12 | ⚪ 未开始 | ρ/σ 相对误差 <1e-6；余弦 >0.99 |
| **P4** 报告骨架 + Fig.1 + §2 | C | 11-12 | ⚪ 未开始 | §3 ≤2 页；引用 ≤15 条 |
| **P5** 自研闭环（SGD） | A | 11-13 | ⚪ 未开始 | PenDigits kNN@10 差 ≤0.02；无 NaN；silhouette >0.1 |
| **P6** 主表（2 数据集 × 10 折 × 4 方法 × 5 k = 400 行） | A | 11-13 | ⚪ 未开始 | 重跑逐折差 = 0；`results/grid_knn.csv` |
| **P7** 数据卡终版 + 3 张 EDA | B | 11-13 | ⚪ 未开始 | V7–V8；dpi≥160 |
| **P8** 数字交底 `README_numbers.md` | A→C | 11-13 | ⚪ 未开始 | 每个数字可指到 csv 行 + 判定词 |
| **P9** §3+§4 成稿（表 1–4、Fig.2/3） | C | 11-13 | ⚪ 未开始 | 用**我们的**数字，不抄原文 |

放弃顺序（`PLAN.md` §4，A 可当场执行）：1) 自研 SGD → 2) COIL-20 的 t-SNE 对照 → 3) 定性图与时间表。**P1/P2/P6/P8 不砍。**

图例：⚪ 未开始 · 🟡 进行中 · 🟢 完成 · 🔴 阻塞/失败 · ⚫ 已降级（写了偏离）

## 已跑的事实（可复现证据）

| 日期 | 内容 | 证据 |
|---|---|---|
| 11-10 | 冒烟：PenDigits + COIL-20，PCA/t-SNE/UMAP(umap-learn)，10 折，k∈{10..160} | `results/smoke_umap/digits.json`、`coil20.json` |
| 11-10 | 环境：Python 3.14.7 + numba 0.68.1 + umap-learn 0.6.0；16 vCPU / ~7.5 GB；无 GPU；joblib 串行 | `pip freeze`、`nproc` |
| 11-11 | 协议/计划/偏离/交接标准成文 | `docs/*.md`、`PLAN.md` |

**冒烟结论（写进报告 §4.0 当"预实验"）**：
- PenDigits：UMAP k=10 .988 / k=160 .921，t-SNE .987/.951 → 与原文（.973/.951）在 k=10 上略高、k=160 接近，**方向一致**；
- COIL-20：UMAP .860/.806/.606（k=10/80/160）vs 原文 .934/.899/.803 → **k=80/160 未复现**（D9），已预登记，主实验要加敏感性分析而不是"跑到过为止"。

## 每日日志

### 2026-11-11（周三）

- 计划：G0（协议冻结）
- 实际：PLAN/PROTOCOL/DEVIATIONS/PAPER_NUMBERS/TASKS_B/HANDOFF_B2A/DATA_CARD/RUN_STATUS 成文；提交先落在 `main-v2`，2026-11-11 夜已合并回 `main` 并删除该分支（远端只留 `origin/main`）
- 偏差：**范围缩减**（用户决定两天交付）→ 落为 `PROTOCOL` v2 §0 + `DEVIATIONS` D18；`configs/*.yaml` 裁到 2 数据集
- 明日：发 B/C 任务书（按 2 数据集版）；`src/data.py` + 契约测试；B 跑 P1

### 模板（复制）

```
### YYYY-MM-DD（周X）
- 计划：
- 实际：
- 偏差（为什么 / 是否触发某个 R）：
- 明日：
```

## 阻塞与决策请求

| # | 阻塞 | 影响 | 需要谁决定 | 截止 |
|---|---|---|---|---|
| 1 | 无 | — | — | — |

（若出现"要不要砍扩展/要不要切 Shuttle 子采样"，在此登记，决定后同步到 `docs/DEVIATIONS.md`。）

## 每日一条命令自查（A 自用）

```bash
cd /home/pklgames/coding/dsai5102MiniProject
git log --oneline -5
ls results/ data/processed/ 2>/dev/null
python -m pytest -q tests/ 2>&1 | tail -3
```
