# DATA CARD 模板（B 填写，每个数据集一份或一张总表）

> 目的：报告里“Data description”一节 + 可复现性附录。凡是本节写下的处理步骤，`src/data_prep.py` 都必须真的有对应代码。

## 1. 数据集总表

| 名称 | 来源（URL / OpenML did） | 样本数（总 / 少数 / 多数） | 不平衡比 IR | 特征数 | 数值/类别 | 缺失 |
|---|---|---|---|---|---|---|
| pima | OpenML 37 | 768 / 268 / 500 | 1.87 | 8 | 全数值 | 无 |
| phoneme | OpenML 1489 | 5404 / 1586 / 3818 | 2.41 | 5 | 全数值 | 无 |
| adult | OpenML 179 | 48842 / 11687 / 37155 | 3.18 | 14（编码后 108） | 混合 | 有（workclass 等） |
| satimage | OpenML 182 | 6430 / 625 / 5805 | 9.29 | 36 | 全数值 | 无 |
| covertype | OpenML 150 取 class 3/4 | 38501 / 2747 / 35754 | 13.02 | 54 | 全数值（含 one-hot 土壤类型） | 无 |
| mammography | OpenML 310 | 11183 / 260 / 10923 | 42.01 | 6 | 全数值 | 无 |
| oil | OpenML 311 | 937 / 41 / 896 | 21.85 | 49 | 全数值 | 无 |
| qsar-biodeg | OpenML 1494 | 1055 / ? / ? | ? | 41 | 混合 | 待查 |
| kddcup99 | OpenML 1113 | 494021 / ? / ? | ? | 41 | 混合（多为类别） | 无 |
| creditcard | OpenML 1597 | 284807 / 492 / 284315 | 577.9 | 30 | 全数值 | 无 |

## 2. 预处理步骤（每步写清“为什么”）

- [ ] 缺失值：数值列中位数、类别列众数/单列众数？（当前基线用的是中位数填充）
- [ ] 类别编码：one-hot 还是 ordinal？稀疏维度如何处理（adult/kddcup99 类别很多）
- [ ] 标准化：树模型不需要，但如果保留 LogisticRegression 则需要（当前 `lr` 未标准化，需确认）
- [ ] 常数列 / 近似常数列是否删除
- [ ] 是否做特征选择（如 kddcup99 的高基数类别列）
- [ ] **不允许**在划分训练/测试之前做任何依赖标签的变换（重采样、SMOTE、目标编码）

## 3. 划分与产物

- 产出 `data/processed/{name}.csv`（特征）+ `data/processed/{name}_labels.csv`（标签）或单文件含 `y` 列；
- 产出 `data/processed/splits.json`：`{name: {"seed": 0, "folds": [[train_idx...], [test_idx...]]}}`，与 `run_grid.py` 的 5×2 分层划分**逐索引对齐**；
- 用 `.venv/bin/python -c "import sys;sys.path.insert(0,'src');import datasets as D;print(D.describe('name'))"` 复核样本数。

## 4. 需要报告的 EDA 图（存 `figures/eda/`）

- [ ] 每个数据集的类别分布条形图（对数坐标）
- [ ] 少数类 vs 多数类在 2–3 个关键特征上的分布对比（pima 的 glucose/bmi、oil 的前两个特征）
- [ ] 特征相关性热图（只对数值列，最多 20 个特征）
- [ ] 缺失率条形图（若 > 0）

## 5. 交付前自检

- [ ] `data/processed/` 里的每个文件都能被 `src/run_grid.py` 直接读（列名、dtype、无 NaN）
- [ ] 与本文件 §1 的样本数一致
- [ ] 报告里写的每一步处理都能在 `src/data_prep.py` 里找到对应行
