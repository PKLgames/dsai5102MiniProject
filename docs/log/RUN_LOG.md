# 运行日志

> 每天 22:00 由 A 更新一行。规则：**只写事实**（跑过就是跑过）、**只写阻塞**（不是计划）、**每个 pending 带日期**。
> 节点 P1–P15 定义见 `PLAN.md` §2；交付物 S1–S6 见 §3。

## 1. 当前状态 · 2026-11-13

| 项 | 状态 |
|---|---|
| 阶段 | 两日执行（11-12 → 11-13）：只复现 C2，PenDigits + COIL-20（D18） |
| 已完成 | 论文筛选与核验、逐格校对原文 Table 1/2/3、环境确认、冒烟实验、文档重构（PLAN v3 + goal/log/tasks 三层）；**A 的 P2–P6 全部跑通**（契约/自研 UMAP/主表 400 行/数字终版） |
| 进行中 | B：P7–P11（数据包/划分/审计/数据卡/结果图）；C：P12–P15（报告已出 docx v1，A 已回填两处数据 → `report/*_v2.{md,pdf}`）|
| 阻塞 | 无 |
| 下一步（11-12 晚） | A 发 S3（`README_numbers.md` + `grid_knn.csv` + embeddings）；B 交 S2；C 交 P12 骨架 |

## 2. 节点追踪

| P | 谁 | 到期 | 状态 | 证据 |
|---|---|---|---|---|
| P1 环境与冒烟 | A | ✅ 11-10 | 完成 | 本文 §3 |
| P2 数据契约 | A | ✅ 11-12 | 完成 | `pytest -q` 20 passed；两次 sha 相同 |
| P3 fuzzy + spectral | A | ✅ 11-12 | 完成 | ρ/σ 相对误差 0.0；余弦 1.000000（同一距离矩阵） |
| P4 自研 SGD | A | ✅ 11-12 | 完成 | PenDigits 0.9877 vs ref 0.9877；silhouette 0.657 |
| P5 主表 | A | ✅ 11-12 | 完成 | 400 行 + 8 行运行时间 + 2 个 embeddings |
| P6 数字终版 | A | ✅ 11-12 | 完成 | `README_numbers.md` 152 行；每数带行号；判定 pendigits 复现 / coil20 未复现 |
| P7 数据包 | B | 11-12 | ⚪ | n/d 精确；sha 自洽 |
| P8 折划分 | B | 11-12 | ⚪ | 10 折、无交集、字节相同 |
| P9 审计对拍 | B | 11-13 | ⚪ | `max|dX|=0` |
| P10 数据卡 + EDA | B | 11-13 | ⚪ | 行号可追溯；dpi≥160 |
| P11 结果图 | B | S3+3h | ⚪ | 300 dpi；点数 = csv |
| P12 骨架 + §1/§2/§3 | C | 11-12 | ⚪ | §3 ≤2 页；引用 ≤15 |
| P13 §4 占位版 | C | 11-13 | ⚪ | 无手打数字 |
| P14 替换定稿 | C | S3 后 | ⚪ | `grep '{{'` 为空 |
| P15 报告 + slides | C | 11-21 / 11-24 | ⚪ | 见 `C_ACCEPTANCE.md` |

## 3. 冒烟实测（2026-11-10，`scripts/smoke_umap.py`，记录用，**不是结论**）

| 数据集 | 方法 | k=10 | k=80 | k=160 | fit 耗时 |
|---|---|---|---|---|---|
| PenDigits | PCA | .649 | — | .640 | 0.007 s |
| PenDigits | t-SNE | .987 | — | .951 | 10.8 s |
| PenDigits | UMAP-ref | .988 | — | .921 | 12.2 s |
| COIL-20 | PCA | .720 | — | — | 1.45 s |
| COIL-20 | t-SNE | .958 | .765 | .640 | 9.5 s |
| COIL-20 | UMAP-ref | .860 | .806 | .606 | 17.4 s |

结论：PenDigits 方向与原文一致；COIL-20 偏低（原文 .934/.899/.803）→ 已预登记 D9，报告必须写归因。

## 4. 每日一行

| 日期 | 做了什么 | 结果 | 阻塞 |
|---|---|---|---|
| 11-10 | 环境核对 + 冒烟 | 见 §3 | 无 |
| 11-11 | 论文核验、协议/计划成文 | D1–D18 预登记 | 无 |
| 11-12 | 文档重构 + A 侧 P2–P6 全跑通；主表重跑校验 | S1/S3 已 tag；400 行两次字节一致；pendigits 复现、coil20 未复现；`numbers.json` 98 键 | 无 |
| 11-13 | 拉 C 的 docx（`ce7e53e`）→ 转 md/PDF；新增 `fetch_data.sh`/`repro.sh`；填报告 A 占位符 → `report/DSAI5102_07_Report_v2.{md,pdf}` | 8-gram 0.22%（11/5097）；端到端 2m08.6s；Table 4 计时按同一次运行刷新 | 无 |

## 5. 排障记录（11-12，P3/P4 期间）

| # | 症状 | 根因 | 修法 |
|---|---|---|---|
| 1 | σ 相对误差 0.9936，图和 1370 vs 1841 | `smooth_knn_dist` 二分里 `d<=0` 的项被 `exp(0)` 与 `count_nonzero` 各算一次 | `np.where(d > 0.0, np.exp(-(d / mid)), 1.0).sum()`，保持 float32 相减后再升 float64 |
| 2 | digits kNN@10 只有 0.9605 | `find_ab_params` 拟合支撑集写错（应为 `xv<min_dist → 1`，其后 `exp(-(xv-min_dist)/spread)`） | 照 umap 口径重写，得到 a=1.576943、b=0.895061 |
| 3 | 首个 epoch 后 3594 个坐标全 NaN | `d2 ** b`（b≈11.44）在 float32 溢出成 inf，`inf/inf = nan` | 梯度全程 float64，回写 `.astype(np.float32)` |
| 4 | `AttributeError: Module 'scipy.sparse' has no attribute 'sparse'` | `sp.sparse.identity` 是笔误 | 改 `sp.identity` |

另记两条对拍事实（不是 bug，是口径差异，已写进 `docs/log/DEVIATIONS.md`）：
- COIL-20 上 umap-learn 用近似 kNN（pynndescent），把相距 2.13e-06 的近重复点当自身吞掉（ρ=29.35），我们精确 kNN 的 σ 因此更大；两者 kNN@10 差 0.0007。
- 敏感性探针：COIL-20 `n_neighbors` 15→30→100，我们 kNN@10 = 0.8569→0.8458→0.8799（原文 0.921）——差距不只在邻居数。
