# PROTOCOL ｜ 复现协议 v0.1

> owner: A ｜ 状态：Pima 冒烟通过后冻结字段；任何改动记入 DEVIATIONS.md
> 对应论文：Chawla et al., *SMOTE*, JAIR 16 (2002) 321–357，§5 与 Tables 2–3

## 1. 主张与判据

| 编号 | 主张（论文原话范围） | 判定标准 |
|---|---|---|
| C1 | SMOTE + 多数类降采样在**多数**数据集上 AUC 优于纯随机降采样 | 逐数据集比较“最佳 SMOTE 列”与“Under 列”，统计胜负数量 ≥ 6/8 |
| C2 | 增益与不平衡比/类重叠正相关 | 各数据集 AUC 增益 vs IR 的 Spearman 相关 > 0 |
| C3 | 合成过采样优于简单复制（复制导致树更大、少数类召回更低） | SMOTE vs ROS：树节点数更小、少数类召回更高 |

**等价判据**：方向一致 + 方法排序一致 + 绝对差值 ≤ 0.02（AUC，10 折均值）。不追求小数位完全一致。

## 2. 交叉验证

- 5×2 分层 CV：`StratifiedKFold(n_splits=5, shuffle=True, random_state=seed+repeat)`，`repeats=2`；
- 折内重采样：`imblearn.pipeline.Pipeline`，采样器只在训练折上 `fit`（**禁止**先对全量重采样再切分）；
- 报告：10 个折分数的 mean ± std（论文用 10-fold 单次，我们只多一个 repeat）。

### C1 的“Under 列”怎么取

论文 Table 3 的 Under 列是**多个降采样率里的最佳值**，因此我们对每个数据集取 `rus25`、`rus50`、`rus100`
三个点中的最高 AUC 作为“Under 列”，再与“最佳 SMOTE 列”比较。

## 3. 学习器

| 别名 | 实现 | 说明 |
|---|---|---|
| `dt` | `PrunedDecisionTree`（`src/learners.py`）：熵准则 CART + 训练折内 CCP 剪枝 | **C4.5 的代理**：补上 C4.5 的剪枝行为，未剪枝 CART 在 Pima 只有 0.673 AUC（D9/D10） |
| `dt_raw` / `dt_msl5` | 未剪枝 / `min_samples_leaf=5` | 剪枝强度敏感性对照（D10），只出现在 Discussion |
| `rf` | `RandomForestClassifier(n_estimators=300, n_jobs=1)` | 稳健性检查，非论文内容 |
| `lr` | `LogisticRegression(max_iter=2000)` | 稳健性检查 + 阈值/代价分析的主模型 |

## 4. 采样器 spec（`src/samplers.py`）

| spec | 含义 |
|---|---|
| `none` | 不平滑 |
| `rus` | 随机降采样多数类到 1:1 |
| `rus{N}` | 保留多数类原数量的 N%（不低于少数类数量），对应论文的降采样率扫描 |
| `ros` | 随机复制少数类到 1:1（C3 的对照） |
| `smote{N}` | SMOTE 合成 N% 额外少数类样本（N=100 → 少数类翻倍），默认 k=5；`smote{N}_k{K}` 指定 k |
| `borderline` / `adasyn` / `smoteenn` / `smotetomek` | 扩展对比（非论文原表内容） |

注意：论文的 N% 是“合成量为原少数类的 N%”，与 imblearn `sampling_strategy` 浮点语义不同，换算在 `samplers._ratio_for_percent()`，并有单测。

## 5. 指标

AUC（主）｜PR-AUC ｜ G-mean（阈值 0.5，√(TPR·TNR)）｜少数类 F1 ｜ Brier。
阈值/代价分析（扩展）单独用 `predict_proba` 扫 0–1 阈值，最小化 `C_FN·FN + C_FP·FP`，代价比取 1:1、5:1、10:1。

## 6. 数据与标签

| 数据集 | did | 目标列 | 少数类标签 | 备注 |
|---|---|---|---|---|
| pima | 37 | `class` | `1`（tested_positive） | 268/500，与论文 Table 2 一致 |
| phoneme | 1489 | `Class` | `1` | 1586/3818 |
| adult | 179 | `class` | `>50K` | 11687/37155（多余类取最少的那个） |
| satimage | 182 | `class` | 类 4（最少）  | 论文“最小类为少数、其余合并” |
| covertype | 150 | `class` | 类 1（Cottonwood/Willow） | 需取 2 类子集，与论文 2747/35754 对应 |
| mammography | 310 | `class` | `1` | 260/10923 |
| oil | 311 | `class` | `1` | 41/896 |
| qsar-biodeg（替代 E-state） | 1494 | `class` | 最少类（356/699，IR 1.96） | 替代理由见 DEVIATIONS D3 |
| kddcup99（可选补充） | 1113 | `label` | 非 `normal` | **二分类化规则：`y = (label != "normal")`**，10% 分层子集；该集“攻击”是多数类（IR 0.25），只适合作为异常类语义的补充，不进主表 |
| creditcard（外部 + Can 角色） | 1597 | `Class` | `1` | 35% 分层子集（99,682 行，IR 578:1）；全量留扩展 |

编码：数值列中位数填充；类别列 one-hot（`datasets._encode`）。B 可在 `src/data_prep.py` 提供更细策略，但必须产出同样的 `data/processed/*.csv` + `splits.json`，并保证与 `run_grid.py` 一致的切分种子。

## 7. 随机性

- CV 划分种子：`seed + repeat`，`seed=0`；
- 采样器种子：`seed*1000 + repeat*10 + fold`；
- 学习器种子：`seed + repeat`；
- 不设全局 `np.random.seed`，全部走显式 `random_state`。

## 8. 机器与耗时

16 vCPU / 7.5 GB / 无 GPU；joblib 在本环境退化为 `n_jobs=1`，耗时按串行估算。
