# DATA CARD 模板（B 填写，每个数据集一份或一张总表）

> 目的：支撑报告 "Data description" 一节 + 可复现性附录。
> 规则：本节写下的每一步，`src/data_prep.py` 里都必须真的有对应代码；否则删掉这句话。

## 1. 数据集总表

| 名称 | 来源（URL / did） | 样本数（总 / 少数 / 多数） | 不平衡比 IR | 特征数 | 数值/类别 | 缺失 |
|---|---|---|---|---|---|---|
| | | | | | | |

## 2. 预处理步骤（每步写清"为什么"）

- [ ] 缺失值：数值列用什么填充（中位数/均值/模型），类别列缺失是否作为独立类别
- [ ] 类别编码：one-hot / ordinal / target encoding（**target encoding 只能在训练折内做**）
- [ ] 标准化：哪些模型需要（线性/核方法需要，树不需要）
- [ ] 常数列 / 近似常数列是否删除
- [ ] 是否做特征选择（高基数类别列如何处理）
- [ ] **不允许**在划分训练/测试之前做任何依赖标签的变换（重采样、目标编码、特征选择）

## 3. 划分与产物

- `data/processed/{name}_X.csv`（特征）、`data/processed/{name}_y.csv`（单列 `y`，正类 = 少数类/目标类）
- `data/processed/splits.json`：`{name: {"seed", "folds", "repeats", "splits": {rep0_fold1: {train: [...], test: [...]}}}}`，
  由 `scripts/make_splits.py` 生成，**不许手写**
- `data/manifests/{name}.json`：行数、特征数、标签分布、列名、dtype（对拍真值）
- 复核：`python -c "import json;print(json.load(open('data/manifests/<name>.json'))['n'])"`

## 4. 需要报告的 EDA 图（存 `figures/eda/`，英文标注）

- [ ] 类别/目标分布（不平衡数据用对数坐标并标 IR）
- [ ] 关键特征在两类间的分布对比（2–3 个特征）
- [ ] 数值特征相关性热图（≤20 列，标出最高相关对）
- [ ] 缺失率条形图（若 > 0）

## 5. 交付前自检

- [ ] `data/processed/` 每个文件都能被建模脚本直接读（列名、dtype、无 NaN）
- [ ] 与本文件 §1 的样本数一致
- [ ] `pytest tests/ -q` 全绿（数据契约测试）
- [ ] 报告里写的每一步处理都能在 `src/data_prep.py` 里找到对应行
- [ ] 已知数据问题（版本差异、样本数略差、子集化）写在第 6 节
