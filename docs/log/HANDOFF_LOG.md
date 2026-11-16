# 交接记录

> 每次交接（S1–S4）留一行。格式固定：**时间 | tag | 核验人 | 跑了哪些检查 | 结论 | 未解决项**。
> 检查项定义见 `docs/tasks/B_ACCEPTANCE.md`（A 验 B）与 `docs/tasks/A_ACCEPTANCE.md`（A 自验）。

## 汇总

| 成果 | 时间 | tag | 核验人 | 结论 | 备注 |
|---|---|---|---|---|---|
| S1 契约 + 模板 | 11-12 12:30 | `s1` | A 自验 | ✅ PASS | `pytest` 20 passed；`load()` 两次 sha 相同（pendigits 8b3b6ae9…、coil20 d3bf54a4…）；`README_numbers.md` 含键名清单 |
| S2 数据包 | 11-15 06:53 | 未打 tag | B 自验 + A 审计 | ✅ PASS（形式改为 loader + manifest） | `VALIDATION.json`：`max_abs_difference_vs_A = 0.0`、`labels_equal = true`、`array_sha256` 与 A 一致；`splits.json` 逐折 = `StratifiedKFold(10, shuffle=True, random_state=42)` 真标签；`pytest` 26 passed |
| S3 数字终版 | 11-12 21:40 | `s3` | A 自验 | ✅ PASS | 400 行无重复键、两次跑字节一致（`canonicalize`）、`runtime.csv` 8 行、`numbers.json` 98 键与 `README_numbers.md` 对齐、判定见 `results/README_numbers.md` §0（pendigits 复现 / coil20 未复现） |
| S3 数字终版（重算） | 11-16 21:30 | `s3` | A 自验 | ✅ PASS | 按 B 的验证划分重算 400 行；`results/evaluation_protocol.json` 记协议哈希；判定：PenDigits 5/5 复现，COIL-20 k=40/80 复现、k=10/20/160 未复现 |
| S4 结果图 | 11-15 06:53 | 未打 tag | B 自验 + A 抽验 | ✅ PASS | fig2/3/4 + 3 张 EDA，dpi = 300；fig3 有 40 个点 = `paper_vs_ours.csv` 中 `paper_acc` 非空行数 |
| S5 报告 | 11-16 22:50 | `s5` | A 渲染 + 数字复核 | ✅ PASS（A 侧） | `report/DSAI5102_Group16_Report.pdf`（17 页，由 C 的 V3 md 渲染）；Table 3 补满 10 行、§4 句、D9、贡献表 Key Files 已修；数字全部来自 `results/numbers.json` |
| S6 slides | 11-16 23:30 | 待打 `s6` | A 文本核对 | ⚠️ 待 C 导 PDF | 源文件名为 `slides/DSAI5102_Group16_Slides.pptx`（10 页，页数不变）：第 5 页气泡与第 9 页判定表已按 `numbers.json` 修正；第 5 页红色 "Fails here" 仍把 k=80 圈在内 → 需 C 换第 5 页新图后导出 `DSAI5102_Group16_Slides.pdf` |

## 记录模板

```markdown
### S2 · 2026-11-12 22:10 · tag s2 · 核验人 A
- 路径边界：`git diff --name-only main...data-prep` → 7 个文件，全在白名单
- 哈希重放：`pendigits OK / coil20 OK`（`max|dX| = 0.0e+00`）
- 契约与划分：pytest 8 passed；两数据集 10 折、无交集、全覆盖
- 完整性：n=1797/1440，NaN/inf=0，X∈[0,1]
- 结论：**PASS**，合入 main
- 未解决项：无
```

## 跨交接的未解决项

| 项 | 现状 | 谁跟 |
|---|---|---|
| COIL-20 k=80/160 偏低（D9） | 冒烟已见；主表跑完后写归因 | A |
| t-SNE 单线程导致加速比偏乐观（D3） | 报告/slides 必须标注方向 | C |
| 自研 SGD 与参考实现的差异幅度 | P4 用 kNN 差 ≤0.02 判定，超出即降级 | A |

## B delivery · 2026-11-15
- LU Yuqing / B: independent preprocessing, manifests, real-label stratified folds, data card, 3 EDA figures, 2 required result figures and 1 supplementary curve prepared locally.
- Exact A/B equality on both datasets: max|dX|=0, labels equal; array hashes match the canonical loader and previously logged prefixes.
- Verification outputs: handoff_B/VALIDATION.json, validation_stdout.txt, PYTEST.txt.
- Pending A review: split reader uses the wrong schema and an all-zero-label fallback. Patch supplied separately, not applied; existing result tables not recomputed.
- Result figures describe the supplied snapshot and are not certified final evaluation figures.
- No Git tag/push or A acceptance claimed.
