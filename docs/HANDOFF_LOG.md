# 交接记录（Handoff Log）

> 规则见 `docs/HANDOFF_B2A.md` §6。**每一次交接一行**，A 填"结论/未解决项"，B 填"自证"。
> 结论取值：`PASS` / `PASS-WITH-NOTE` / `REJECT`。REJECT 必须在"未解决项"写清哪条 V 挂了。

## 汇总

| 时点 | tag | 交接人 | 核验人 | 核验项 | 结论 | 未解决项 | 日期 |
|---|---|---|---|---|---|---|---|
| H0 环境 | — | A | A | 依赖安装、冒烟 | PASS | 冒烟见 `results/smoke_umap/` | 2026-11-10 |
| H1 数据可达 | `handoff-h1` | B | A | V0/V1 | 待执行 | — | 计划 11-12 12:00 |
| H2 数据包（=P1） | `handoff-h2` | B | A | V1–V6 | 待执行 | — | 计划 11-12 22:00 |
| H3 数据卡+EDA（=P7） | `handoff-h3` | B | A | V7–V8 | 待执行 | — | 计划 11-13 22:00 |
| H2b（如需） | `handoff-h2b` | B | A | V1–V6 | 待执行 | — | 视退回情况 |

## 记录模板（复制下面的块）

```
### H2 · 2026-11-12T22:xxZ · tag `handoff-h2`

- 交接内容：data/processed/*.npz ×5、manifests ×5、splits.json、src/data_prep.py、scripts/fetch_data.py
- B 自证：
  - [x] fetch 幂等（第二次 0 下载）
  - [x] pytest 5 passed
  - [x] sha256 重算一致
  - [ ] 数据卡（H3 交付）
- A 核验输出（粘贴命令 stdout）：
  - V1：`git diff --name-only main...data-prep` → 6 个文件，均在允许路径
  - V2：`V2: PASS`（5/5 OK）  ← 命令见 HANDOFF_B2A §3
  - V3：`5 passed`；folds=10/10/10/5/5；无重叠、全覆盖
  - V4：`max|dX|=0.000e+00`，`y_equal=True` ×5
  - V5：`V5: PASS`；shuttle min_class=10（见 note）
  - V6：Elapsed 7:42，Max RSS 1.9 GB
- 结论：PASS-WITH-NOTE
- 未解决项：
  1. shuttle 最小类 10 个样本 → StratifiedKFold 每折 test 侧该类恰 1 个，A 已确认可运行，无需改协议
  2. mnist 子采样后 k=3200 接近先验分类器（DEVIATIONS D11），报告需注明
```

## 关键未解决项追踪（跨交接）

| # | 事项 | 提出 | 负责 | 状态 | 关闭条件 |
|---|---|---|---|---|---|
| 1 | Shuttle 最小类样本数是否支撑 10 折分层 | H1 | A | 开放 | V3 实测通过并记录 |
| 2 | OpenML target 列名版本差异 | H1 | B | 开放 | 数据卡 §6 写明实际列名 |
| 3 | MNIST/FMNIST 子采样对 C2 的影响 | 协议 D5 | A | 开放 | E5 敏感性出数后写进讨论 |
| 4 | COIL-20 大 k 未复现 | 冒烟 | A | 开放 | D9 的 E5 结论 + §5 讨论 |
