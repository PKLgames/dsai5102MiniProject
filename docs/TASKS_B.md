# 成员 B 任务书（数据准备 + EDA）

> 角色：数据准备与探索性分析（EDA）。目标是把"原始数据 → 可训练的数据表 + 折划分 + 数据卡 + EDA 图"这条链路做成**独立可复现的第二实现**，并文档化报告 "Data description" 一节。
> 依赖节点：N1（在 A 的主网格定稿前完成）。**不依赖** A 的任何实验结果，可立刻开始。

## 0. 边界（重要）

- ✅ 可以改：`data/`、`src/data_prep.py`、`figures/eda/`、`docs/DATA_CARD.md`、`tests/test_data_contract.py`
- ❌ 不要改：`src/datasets.py`、`src/run_grid.py`、`src/learners.py`、`src/samplers.py`、`docs/PROTOCOL.md`、`results/`
- 单一真值仍是 A 的 `datasets.load(name)`（`src/datasets.py`）：负责任的实现是**第二份独立实现**，用对拍测试证明两者一致，而不是直接 import。理由：报告里"数据来源与预处理"必须有独立于建模代码的实现与记录，同时能交叉验证 A 的管道没有写错。

## 1. 交付物

### D1 `src/data_prep.py`（核心）

从 `data/raw/{name}.csv`（已缓存，见 §5）生成：

- `data/processed/{name}_X.csv`：特征表
- `data/processed/{name}_y.csv`：单列 `y`，`y=1` **必须**是少数类
- CLI：`.venv/bin/python src/data_prep.py --datasets all`（或 `--datasets pima,oil`），幂等可重跑

处理规则（与 A 现有 `datasets.py` 对齐，任何偏离都要写进 DATA_CARD）：

| 项 | 规则 |
|---|---|
| 缺失值 | 数值列中位数填充；类别列把缺失作为一个独立类别（见 §4 adult 的 `?`） |
| 类别编码 | one-hot（`pd.get_dummies`），不删列、不做目标编码 |
| 标准化 | 不做（主模型是树）；`logistic regression` 在同一特征表上跑，标准化留待报告注明局限 |
| 标签二值化 | 每个数据集一条规则：pima `tested_positive`；phoneme `==2`；adult `>50K`；satimage `==4`；covertype 取 class 3/4，`==4` 为少数；mammography/oil/creditcard `==1`；qsar-biodeg 按 OpenML 原始正类；kddcup99 `label != normal`（注意该集攻击反而是多数类） |
| **禁止** | 在切分前重采样 / 过采样 / 依赖标签的变换 |

### D2 `data/processed/splits.json`（不要手写）

直接跑（A 已提供，确定性）：

```bash
.venv/bin/python scripts/make_splits.py --datasets all
```

产出 5×2 分层划分（`rep0_fold1` … `rep1_fold5`，共 10 个索引对），与 `run_grid.py` 的 `StratifiedKFold(shuffle=True, random_state=seed+rep)` 逐索引一致。文件 17.6 MB，已被 `.gitignore` 忽略，**B 本地生成、不要提交**。

### D3 对拍（验收测试）

`tests/test_data_contract.py`（A 已给出骨架，B 补充 B 侧断言）：

- 每个数据集 `data/processed/{name}_X.csv` 的 `shape`、列名、正类数与 `data/manifests/{name}.json` 一致；
- 若 `_X.csv` 不存在则 `pytest.skip`（B 还没生成时不阻塞 CI）；
- 抽样验证：`_X.csv` 第 i 行与 `datasets.load(name)` 第 i 行的特征值一致（数值列 `np.allclose`，one-hot 列逐值相等）。

运行：`.venv/bin/python -m pytest tests/ -q`

### D4 `docs/DATA_CARD.md`

按 `docs/DATA_CARD_TEMPLATE.md` 填成终版：数据集总表（10 行，含替代说明）、每个数据集"为什么这么处理"的一段话（缺失、编码、异常值）、`data_prep.py` 与 `datasets.py` 的差异清单。**报告 Data description 一节直接从这里摘。**

### D5 `figures/eda/`（至少 4 类图，dpi≥160，英文标签）

1. 每个数据集类别分布条形图（y 轴对数坐标，标注 IR）；
2. 少数类 vs 多数类在 2–3 个关键特征上的分布对比（pima：glucose/bmi；oil：前两个特征；mammography：前两个特征）；
3. 数值特征相关性热图（≤20 列，标注最高相关对）；
4. 缺失率条形图（adult 有 `?`，其余接近 0，可合并成一张小图）。

### D6 一页交接说明（放进 `docs/DATA_CARD.md` 末尾）

- 每个数据集的处理与你做过的**判断**（哪一步可能影响结论）；
- A 的管道与你不同的地方（例如 A 用 `astype(str)` 把 `?` 当独立类别——如果你选择众数填充，必须在这里说明并解释为什么）；
- 已知数据问题：satimage 少 5 例（DEVIATIONS D11）、oil 只有 41 个少数类（EDA 图会很难看，属正常）、credit-card 是 35% 子集（D12）。

## 2. 验收清单（自检，逐条打勾再交付）

- [ ] `data/processed/` 下 10 个数据集齐全，无 NaN，dtype 全为数值
- [ ] `y=1` 的数量与 `data/manifests/*.json` 的 `n_minority` 完全一致
- [ ] `.venv/bin/python -m pytest tests/ -q` 全绿（含 A 原有 16 个测试）
- [ ] `scripts/make_splits.py` 重跑后 `splits.json` 与首次生成完全一致（`md5sum` 相同）
- [ ] `docs/DATA_CARD.md` 里写的每一步，`src/data_prep.py` 都能找到对应行
- [ ] 4 类 EDA 图已生成，能在报告里独立看懂（标题/轴标签/单位齐全）

## 3. 时间与协作

- 不设日历日期，按依赖：**N1 = B 的 D1–D5 完成** → A 用它复跑主网格（与 A 现有 `datasets.py` 结果对齐后，报告里用 B 的管道作为正式数据路径）。
- 分支约定：`git checkout -b data-prep`，只提交上面 §0 允许的路径，完成后开 PR 或直接 push 到该分支，由 A 合入 `main`。
- 卡住时优先看 `docs/DEVIATIONS.md`（D3/D4/D11/D12/D13 记录了两个替代数据集与 satimage 版本差），以及 `docs/RUN_STATUS.md`（当前哪些结果是真的）。

## 4. 两个容易踩的坑

1. **pima 标签是字符串**：原始值是 `tested_negative` / `tested_positive`，不是 0/1。直接 `==1` 会得到 0 个正类（A 踩过，见 git 历史）。
2. **adult 的缺失是 `?` 不是 NaN**：`workclass` / `occupation`（各 331/5000 行）与 `native-country`（97/5000）。`pd.read_csv` 默认读成字符串 `'?'`，`isna()` 查不到；要么归为独立类别，要么 `na_values='?'` 后填充——两种选择都行，但必须在 DATA_CARD 写明，因为它会改变 one-hot 维度（108 列里有 3 列来自"缺失"类别）。

## 5. 原始数据位置

`data/raw/{name}.csv` 已缓存（共 334 MB，`.gitignore` 已排除，不入库）：adult、covertype、creditcard、kddcup99、mammography、oil、phoneme、pima、qsar-biodeg、satimage。缺失时运行：

```bash
.venv/bin/python -c "import sys;sys.path.insert(0,'src');import datasets as D;D.fetch('<name>')"
```

OpenML did：pima 37、phoneme 1489、adult 179、satimage 182、covertype 150、mammography 310、oil 311、qsar-biodeg 1494、kddcup99 1113、creditcard 1597。
