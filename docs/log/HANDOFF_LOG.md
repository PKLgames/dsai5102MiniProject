# 交接记录

> 每次交接（S1–S4）留一行。格式固定：**时间 | tag | 核验人 | 跑了哪些检查 | 结论 | 未解决项**。
> 检查项定义见 `docs/tasks/B_ACCEPTANCE.md`（A 验 B）与 `docs/tasks/A_ACCEPTANCE.md`（A 自验）。

## 汇总

| 成果 | 时间 | tag | 核验人 | 结论 | 备注 |
|---|---|---|---|---|---|
| S1 契约 + 模板 | 11-12 12:30 | `s1` | A 自验 | ✅ PASS | `pytest` 20 passed；`load()` 两次 sha 相同（pendigits 8b3b6ae9…、coil20 d3bf54a4…）；`README_numbers.md` 含键名清单 |
| S2 数据包 | Day1 22:00 | `s2` | B 自验 → A 验 | ⚪ 待执行 | 哈希重放 + 双实现对拍 |
| S3 数字终版 | 11-12 21:40 | `s3` | A 自验 | ✅ PASS | 400 行无重复键、两次跑字节一致（`canonicalize`）、`runtime.csv` 8 行、`numbers.json` 98 键与 `README_numbers.md` 对齐、判定见 `results/README_numbers.md` §0（pendigits 复现 / coil20 未复现） |
| S3 数字终版 | Day2 22:00 | `s3` | A 自验 | ⚪ 待执行 | 400 行 + 重跑差 0 |
| S4 结果图 | S3+3h | `s4` | B 自验 → A 验 | ⚪ 待执行 | dpi + 点数与 csv 一致 |
| S5 报告 | 11-21 23:59 | `s5` | A 复核数字 | ⚪ 待执行 | 见 `C_ACCEPTANCE.md` |
| S6 slides | 11-24 12:00 | `s6` | A 复核数字 | ⚪ 待执行 | — |

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
