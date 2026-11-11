# 运行状态板（RUN STATUS）

> 每天 22:00 由 A 更新。三行规则：**只写事实**（命令跑过就是跑过）、**只写阻塞**（不是计划）、**每个 pending 都有日期**。
> 质量门定义见 `PLAN.md` §4；交接见 `docs/HANDOFF_B2A.md`。

## 当前状态 · 2026-11-11（周三）夜

| 项 | 状态 |
|---|---|
| 阶段 | 协议冻结（G0 进行中） |
| 已完成 | 论文筛选、候选核验、冒烟实验（PenDigits/COIL-20 × PCA/t-SNE/UMAP）、环境安装、数据源试探 |
| 进行中 | 写 PLAN / PROTOCOL / DEVIATIONS / PAPER_NUMBERS / TASKS_B / HANDOFF_B2A |
| 阻塞 | 无 |
| 明日首要 | 发 B/C 任务书；A 开始 `src/data.py` + 契约测试；B 跑 H1 |

### 质量门追踪

| 门 | 到期 | 状态 | 证据 | 备注 |
|---|---|---|---|---|
| G0 协议冻结 | 11-12 12:00 | 🟡 进行中 | `docs/PROTOCOL.md` v1 已成文 | 待 A 自检 §5 每条主张都有判据 |
| H1 数据可达 | 11-12 22:00 | ⚪ 未开始 | — | B 负责 |
| G1 环境与契约 | 11-13 12:00 | ⚪ 未开始 | `src/data.py`、`tests/test_data_contract.py` | 依赖 H1 的 `(n,d)` |
| H2 数据包 | 11-13 22:00 | ⚪ 未开始 | npz + manifest + splits | B 负责 |
| G2 自研可用 | 11-14 22:00 | ⚪ 未开始 | `src/umap_impl/` 在 PenDigits ≈ umap-learn | **最关键的门**，不过则触发 R1 降级 |
| G3 主表 | 11-16 22:00 | ⚪ 未开始 | `results/grid_knn*.csv` | |
| H3 数据卡 | 11-17 22:00 | ⚪ 未开始 | `docs/DATA_CARD.md` + EDA | B 负责 |
| G4 扩展 | 11-18 22:00 | ⚪ 未开始 | 热力图 | 可砍项（R7） |
| G5 交付 C | 11-19 22:00 | ⚪ 未开始 | `results/README_numbers.md` | |
| 报告 v1 / final | 11-19 / 11-21 | ⚪ 未开始 | `report/` | C 负责 |
| Slides / 彩排 | 11-24 12:00 | ⚪ 未开始 | `slides/` | C 负责 |

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
- 实际：PLAN/PROTOCOL/DEVIATIONS/PAPER_NUMBERS/TASKS_B/HANDOFF_B2A/DATA_CARD/RUN_STATUS 成文；git 分支 `main-v2`
- 偏差：无
- 明日：发任务书；`src/data.py` + `tests/test_data_contract.py`；B 跑 H1

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
