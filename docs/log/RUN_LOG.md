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

## 6. 2026-11-16 · P5 重算与 S5 收口（A）

| 事项 | 事实 |
|---|---|
| 折划分缺陷 | 旧 `run_grid.load_splits()` 回退分支用 `np.zeros(n)` 当标签 → 不分层；旧折与 B 的验证折 test 集重合仅 7–15%。已改为 fail-closed 读 `data/manifests/splits.json`（B 的 `run_fixed_evaluation.py` 串起备份→重算→出图） |
| 重算结果 | 400 行 / 10 折 / 2 数据集；旧结果备份在 `results_backup/20261115T155709400559Z/`（gitignore） |
| 判定变化 | PenDigits 5/5 单元复现（不变）；COIL-20 k=40、k=80 由未复现→**复现**（k=80 Δ −0.091→−0.081），k=10/20/160 仍未复现 |
| 报告收口 | C 的 V3 已套用 `results/V3_NUMBERS_PATCH.md`；A 再补 4 处：Table 3 补满 10 行、§4 "gap persists" 句改写、Appendix A 的 D9 改为「已定位」、贡献表 Key Files 去掉不存在的 `src/*_eval.py` 并加工作口径说明 |
| PDF | `report/DSAI5102_Group16_Report.pdf`（17 页，`report.css` 加 `page-break-inside: avoid` 避免 Table 3 跨页） |
| slides | `slides/DSAI5102_Group16_slides_V2.pptx`：第 9 页判定表改为「PenDigits k=10–160 全部 / COIL-20 k=40,80 复现；COIL-20 k=10,20,160 未复现」，第 5 页气泡改写。**本机无 LibreOffice，PDF 需 C 重新导出**；第 5 页红框仍含 k=80（矢量图层，需 C 重画） |
| 未解决 | `results/review_comparison.csv` 末列仍写 "Recompute required unless verified against fixed stratified split file"（B 的脚本产物，待 B 重出）；`docs/goal/DATA_CARD_B.md` 待并入主数据卡 |

## 7. 2026-11-16 · 命名标准化 + 口径统一（A）

| 事项 | 事实 |
|---|---|
| 报告定名 | `report/DSAI5102_Group16_Report_V3.md` → `report/DSAI5102_Group16_Report.md`；PDF 同名（17 页） |
| 报告归档 | `DSAI5102_07_Report_draft.docx` → `report/archive/`（docx 停用，md/PDF 为唯一真值） |
| slides 定名 | `slides/DSAI5102_Group16_slides_V2.pptx` → `slides/DSAI5102_Group16_Slides.pptx`（10 页，页数不变） |
| slides 归档 | 第 1 版 pptx/pdf 与 11-16 旧 PDF → `slides/archive/`；**PDF 待 C 换第 5 页图后导出** |
| 附录 B 重测 | `bash scripts/repro.sh` 实测 **2m14.2s（≈2.2 分钟）**；报告改为「2026-11-16 用 repro.sh 实测 2.2 分钟」，删掉「未对修正后的流程重测」的免责句 |
| 查重重测 | `similarity_check.py` 对本报告：**0.18%**（11 / 6,259 个 8-gram，全部落在参考文献标题） |
| B 的收尾项 | 本机改 `scripts/review_result_summary.py`：`evaluation_status` 由固定文案改为 `recomputed against data/manifests/splits.json (protocol validated-stratified-v1 digest 15eb914e06f8)`；重出 `results/review_comparison.csv`（40 行，旧文案 0 处） |
| 口径统一 | `docs/goal/SPEC.md` §8 新增五条（数字来源唯一 / 判定词唯一 / transductive 写明 / 不跨机比秒数 / 命名与版次），README 指向它 |

## 8. 2026-11-16 23:54 · S6 收口（C 导出 + A 核对）

| 事项 | 事实 |
|---|---|
| slides 源文件 | `slides/DSAI5102_Group16_Slides.pptx`（10 页）：第 5 页已换成 C 的新图（COIL-20 k=80 我们的 UMAP 0.817 > t-SNE 0.783，失败点在 k=160） |
| slides PDF | `slides/DSAI5102_Group16_Slides.pdf`（959,918 B，10 页），由同一 pptx 导出；第 9 页判定表与 `results/numbers.json` 一致 |
| 删除旧件 | `slides/Final_DSAI5102_Group16_slides.{pptx,pdf}` 已删（第 9 页为旧判定） |
| 提交包 | `/home/pklgames/coding/dsai5102_group16_submission.zip`（21 MB，87 文件，sha256 `5d77fff3…`）；包内 report PDF、slides pptx+pdf 与仓库同源 |

## 9. 2026-11-17 00:20 · 报告版式学术化（A）

| 事项 | 事实 |
|---|---|
| 旧档归档 | `report/archive/DSAI5102_Group16_Report_2026-11-16_preprint.{md,pdf}` + `report/archive/report.css.preprint` |
| 版式 | 单栏 A4（边距 2.45/2.3/2.3/2.3 cm）；正文 10.5pt Latin Modern Roman（回退 DejaVu Serif）、行高 1.42、两端对齐 + 自动断字、首行缩进 1.1em；标题 15.5pt 居中；页脚页码居中；书眉为当前章节名（首页不显示）；表格改 booktabs（只有上下横线，去掉竖线与底色）；图注/表注 8.8pt 斜体、编号加粗；参考文献悬挂缩进 |
| 实现 | `report/report.css` 全量重写 + `scripts/build_report_pdf.py` 的 `postprocess()`（只包 `<div class="abstract">`/`<div class="refs">`、给图片段落加 `class="figure"`、给图注编号加 `<b>`，不触碰任何文字与数字） |
| 内容零改动 | `git diff --stat report/DSAI5102_Group16_Report.md` 为空；Markdown 未改，只有 CSS/渲染脚本变化 |
| 产物 | `report/DSAI5102_Group16_Report.pdf` 16 页（原 17 页），sha256 `cdf67b87…` |
| 图 1 修复 | `report/media/` 之前被归档，导致 Figure 1 只剩 alt 文字；已从 `report/archive/media/image1.png` 恢复到 `report/media/image1.png`（103,770 B），并纳入版本控制以保证 PDF 可重建 |
| 提交包 | `report/DSAI5102_Group16_Report.pdf` 已同步（与仓库同 sha256 `cdf67b87…`）；`dsai5102_group16_submission.zip` 重打为 21.5 MB / 68 文件，sha256 `5112137927629d2a92d0e88e4ebda675c123212cabed8b5a4270cdf98e32855a`（README §7 已把「17 页」改为「16 页，学术单栏版式」） |

## 10. 2026-11-17 19:35 · C 上传新版报告/slides 后重新打包（A）

| 事项 | 事实 |
|---|---|
| 拉取 | `git pull --ff-only`：`e36eed6..901d62f`（12 个提交，全部 C 上传）；报告 md 改 102 行、PDF 21 页、新增 `report/media/{pipeline_evaluation.png, umap_pipeline_original_updated.png/.svg}`、`report/report.css` 换为 C 的版式；slides pptx/pdf 各更新一次 |
| 报告核对 | 新 PDF 21 页；关键数字仍在（0.857 / 0.849 / 0.817 / 0.578 / −0.082 / 0.225），图表编号 Figure 1–4 + S1–S3、Table 1/1b/2a/2b/3/4 |
| 包内复跑 | `bash scripts/repro_submission.sh` 全程通过：26 测试 → 400 行主表 → 计时 → `numbers.json` 90 个非计时键全一致 → `PASS`（PenDigits 复现 73% / COIL-20 未复现 60%）；复跑后已用 `expected/results/` 复原包内 `results/`，并删除解包出来的 `data/raw/coil20/coil-20-proc/` |
| 包内容 | 新增 `report/{DSAI5102_Group16_Report.md, report.css, media/}`；report PDF 与 slides PDF 与仓库字节相同（`cd1700ac…` / `5d100b84…`） |
| zip | `dsai5102_group16_submission.zip` 21.7 MB / 75 文件，sha256 `6d1be23bb2e70e168f8f9b0c27b1c3797a264da399adc7e035085e53b2152e71` |
