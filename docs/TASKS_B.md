# 成员 B 任务书（数据准备 + EDA）

> 角色：数据准备与探索性分析。把"原始数据 → 建模数据表 + 折划分 + 数据卡 + EDA 图"做成**独立可复现的第二实现**，
> 并文档化报告 "Data description" 一节。**不依赖** A 的任何实验结果，论文与数据集确定后即可开始。

## 0. 边界

- ✅ 可改：`data/`、`src/data_prep.py`、`figures/eda/`、`docs/DATA_CARD.md`、`tests/test_data_contract.py`
- ❌ 不改：`src/` 下的建模代码、`docs/PROTOCOL.md`、`results/`
- 为什么是"第二实现"：报告里的数据处理必须独立于建模代码、可单独审阅；同时用对拍证明两侧一致，能抓到 A 的管道错误。
  若论文只有一侧实现，另一侧 `import` 复用，不要各写一份。

## 1. 交付物

### D1 `src/data_prep.py`

- 输入：`data/raw/{name}.csv`（原始数据缓存）
- 输出：`data/processed/{name}_X.csv`（特征）、`data/processed/{name}_y.csv`（单列 `y`，正类 = 少数类/目标类）
- CLI：`.venv/bin/python src/data_prep.py --datasets all`，幂等可重跑
- 规则（与 A 对齐，任何偏离写进数据卡）：数值列中位数填充；类别列缺失作为独立类别；one-hot；不做标准化（线性模型另说）；
  **切分前不做任何依赖标签的变换**

### D2 `data/processed/splits.json`

只允许用 `scripts/make_splits.py`（A 提供，参数化到你的数据加载函数）+ 固定种子生成；文件较大（数十 MB），已被 `.gitignore` 忽略，**不入库**。

### D3 对拍（`tests/test_data_contract.py`）

- `data/processed/{name}_X.csv` 的 shape、列名、正类数与 `data/manifests/{name}.json` 完全一致
- 抽样与 A 的 `load()` 逐值对拍（数值列 `allclose`，one-hot 列逐值相等）
- 缺 CSV 时 `pytest.skip`，不阻塞他人

### D4 `docs/DATA_CARD.md`

按 `docs/TEMPLATE_DATA_CARD.md` 填终版：数据集总表（含替代说明）+ 每个数据集"为什么这么处理" + 已知数据问题。
**报告 Data description 一节直接从这里摘。**

### D5 `figures/eda/`（≥4 类图，dpi≥160，英文标注）

类别/目标分布（不平衡时对数轴 + IR）、关键特征两类对比、相关性热图、缺失率。

### D6 一页交接说明（`DATA_CARD.md` 末尾）

哪些处理判断可能影响结论；与 A 的实现差异；已知数据问题（版本差异、样本数略差、子集化）。

## 2. 验收清单

- [ ] 所有数据集齐全，无 NaN，dtype 为数值
- [ ] 正类数量与 `data/manifests/*.json` 一致
- [ ] `.venv/bin/python -m pytest tests/ -q` 全绿
- [ ] `make_splits.py` 重跑后 `splits.json` 与首次生成 `md5sum` 相同
- [ ] 数据卡里每句话都能在 `data_prep.py` 找到对应行
- [ ] EDA 图脱离正文也能看懂

## 3. 协作

- 分支：`git checkout -b data-prep`，只提交 §0 允许的路径，完成后 push 该分支，由 A 合入 `main`。
- 卡住时先看 `docs/TEMPLATE_PROTOCOL.md` 的偏离清单（数据集替换/版本差异都记在那里）。

## 4. 第一轮踩过的坑（同类问题在新论文里大概率复现）

1. 标签是字符串（`tested_positive` 之类），直接 `==1` 会得到 0 个正类 → 先 `value_counts()` 看原始取值。
2. 缺失值是 `'?'` 而不是 NaN → `isna()` 查不到；要么 `na_values='?'`，要么当独立类别，并写进数据卡。
3. 公开镜像的版本可能与论文不同（少几个样本）→ 加载后立即与论文样本数比对，差异记数据卡。
4. 类别极多的列 one-hot 后维度爆炸（如 adult 108 列）→ 在数据卡里给出编码后维度。
