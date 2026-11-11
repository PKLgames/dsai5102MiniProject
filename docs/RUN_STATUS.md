# 运行状态快照（RUN STATUS）

记录时间：2026-11-11 14:25（本地，UTC+8 未确认）
用途：任务被主动暂停/中断时，记录"哪些结果已经是真的、哪些还没跑完"，避免后续误把缺失当失败、或重跑时覆盖已有结果。

---

## 1. 已完成（结果文件已落盘，可直接用于报告）

| 结果文件 | 内容 | 规模 |
|---|---|---|
| `results/smoke_pima.csv` / `_summary.csv` | Pima 冒烟，5×2 CV，dt / dt_raw / dt_msl5 | 3 learner × 8 sampler |
| `results/sens_pima_dt_raw.csv` | 剪枝敏感性：未剪枝 CART | Pima 8 sampler |
| `results/sens_pima_dt_msl5.csv` | 剪枝敏感性：`min_samples_leaf=5` | Pima 8 sampler |
| `results/grid_small.csv` / `_summary.csv` | 主网格：pima, phoneme, mammography, oil, satimage | 5 数据集 × 8 sampler × 10 折 |
| `results/grid_qsar.csv` / `_summary.csv` | 主网格：qsar-biodeg（E-state 的替代） | 1 数据集 × 8 sampler × 10 折 |
| `results/ext_variants.csv` / `_summary.csv` | 扩展：k∈{1,3,10}、Borderline、ADASYN、SMOTE-ENN、SMOTE-Tomek | pima/phoneme/mammography × 11 配置 |
| `report/c1_table.md` | C1 判定表 + 单侧 Wilcoxon | 6 数据集，SMOTE 5/6 胜 |
| `figures/results/auc_by_sampler.png` `box_auc.png` | Fig.2 / Fig.3 | 6 面板 + 汇总箱线 |

结论状态：主网格 **6/9 数据集**完成（pima, phoneme, mammography, oil, satimage, qsar）；论文原表 9 行中除 adult / covertype / Can(→credit-card) 外均可比。

## 2. 已暂停（进程 SIGSTOP，内存中进度未落盘）

`src/run_grid.py` 只在全部数据集跑完时才写 CSV，**暂停状态下没有任何中间文件**；杀掉即丢失全部计算进度。

| PID | 任务 | 已跑 | 预计产出 | 状态 |
|---|---|---|---|---|
| 30851 | `adult,covertype`，8 sampler，n_alphas=8 | 20m41s（约 95% CPU 单核） | `results/grid_big.csv` | 暂停（STAT `Tl`），占内存 ~526 MB |
| 32524 | `creditcard`（35% 子集，99,682×30），6 sampler，5×1 折，n_alphas=6 | 7m35s | `results/grid_creditcard.csv` | 暂停（STAT `Tl`），占内存 ~347 MB |

### 恢复 / 放弃

```bash
# 恢复（原地继续，不丢进度）
kill -CONT 30851 32524

# 放弃（释放内存；之后按下面命令重跑）
kill -9 30851 32524
```

重跑命令（与暂停时完全一致，保证结果可复现）：

```bash
.venv/bin/python src/run_grid.py --datasets adult,covertype \
  --samplers none,rus25,rus50,rus100,ros,smote100,smote200,smote500 \
  --learner dt --n-alphas 8 --out results/grid_big.csv

.venv/bin/python src/run_grid.py --datasets creditcard \
  --samplers none,rus50,rus100,ros,smote100,smote200 \
  --learner dt --n-alphas 6 --folds 5 --repeats 1 --out results/grid_creditcard.csv
```

注意：`adult` 与 `covertype` 的耗时主要在 `PrunedDecisionTree` 的内层 3 折 × `n_alphas` 剪枝路径计算；若时间紧张，可把两者拆成两条命令并行跑（各占 1 核），或把 `n_alphas` 降到 4（已在 DEVIATIONS 预留说明位置，尚未写入）。

## 3. 尚未开始

- credit-card 的扩展实验（k 敏感性 / 变体）：先等主网格结果，判断是否值得。
- 阈值移动与代价敏感层（代价比 1:1 / 5:1 / 10:1）：需要保存测试折概率，当前 `run_grid.py` **未保存概率**，要加 `--save-proba` 才能做 PR 曲线与阈值分析。
- kddcup99 补充实验（已降级为可选，IR 0.25 方向不对，不进主表）。
- 交叉学习器稳健性（rf / lr）：`LEARNERS` 已实现，未跑。
- B 的 `data/processed/*.csv` + `splits.json` + `DATA_CARD.md`（模板已给）。
- C 的报告格式确认（LaTeX / Word）→ 决定出图 dpi 与字体。
- git push（缺凭据）。

## 4. 数值速查（暂停时点的真实结果）

| 数据集 | Under 最佳 | SMOTE 最佳 | 胜者 |
|---|---|---|---|
| pima | rus100 0.7880 | smote200 0.7817 | Under（Δ−0.0063） |
| phoneme | rus100 0.8941 | smote200 0.9026 | SMOTE |
| mammography | rus100 0.8938 | smote200 0.8977 | SMOTE |
| oil | rus50 0.7924 | smote500 0.8280 | SMOTE |
| satimage | rus50 0.9070 | smote100 0.9095 | SMOTE |
| qsar-biodeg | rus100 0.8405 | smote500 0.8724 | SMOTE |
