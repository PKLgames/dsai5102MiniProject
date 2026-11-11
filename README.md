# DSAI5102 Mini-Project · 论文复现：SMOTE（Chawla et al., JAIR 2002）

复现目标：在可公开获取的不平衡二分类数据集上，验证原文 §5 关于 **SMOTE 有效性的三条主张**（见 `docs/PROTOCOL.md` 的 C1–C3），
记录与原文的差异（`docs/DEVIATIONS.md`），并在原文之外做一组“轻扩展”。

- 论文全文（本地缓存，不入库）：`paper/chawla2002_smote.pdf`
- 计划与分工：`../PLAN.md`
- 复现协议：`docs/PROTOCOL.md` ｜ 偏离清单：`docs/DEVIATIONS.md`

## 目录

```
src/            代码（datasets / samplers / learners / metrics / run_grid）
tests/          单测（pytest，16 条）
scripts/        一次性脚本（下载、出图、显著性检验）
configs/        实验矩阵配置
data/raw/       OpenML 下载的原始 CSV（不入库）
data/processed/ B 处理后的建模数据 + splits.json（不入库）
results/        grid.csv 与汇总表（不入库）
figures/        eda/ 与 results/ 图（入库，报告用）
notebooks/      探索性分析（B）
report/         报告源文件（C）
slides/         答辩 slides（C）
```

## 环境与安装

已验证：16 vCPU / 7.5 GB 内存 / 无 GPU / Python 3.14.7。

```bash
uv venv --python 3.14 .venv
uv pip install --python .venv/bin/python -r requirements.txt
# 或：python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

## 快速开始

```bash
# 1) 下载并校验某个数据集（会与论文 Table 2 的样本数对比）
.venv/bin/python -c "import sys;sys.path.insert(0,'src');import datasets as D;print(D.describe('pima'))"

# 2) 单个数据集冒烟
.venv/bin/python src/run_grid.py --datasets pima --samplers none,rus,smote100,smote200 \
    --learner dt --folds 5 --repeats 2 --out results/smoke_pima.csv

# 3) 全部 8 个数据集 × 完整矩阵（见 configs/）
.venv/bin/python src/run_grid.py --datasets pima,phoneme,adult,satimage,covertype,mammography,oil,qsar-biodeg \
    --samplers none,rus,ros,smote100,smote200,smote500 --learner dt --out results/grid.csv

# 4) 跑测试
.venv/bin/python -m pytest tests -q
```

## 数据集（`src/datasets.py`）

| 名称 | 来源 | 规模（少数/多数） | 状态 |
|---|---|---|---|
| pima | OpenML 37 | 268 / 500 | ✅ 与论文一致 |
| phoneme | OpenML 1489 | 1586 / 3818 | ✅ |
| adult | OpenML 179 | 11687 / 37155 | ✅ |
| satimage | OpenML 182 | 625 / 5805（论文 626 / 5809） | ✅ 版本差异见 D11 |
| covertype | OpenML 150 取 class 3/4 | 2747 / 35754 | ✅ 与论文完全一致 |
| mammography | OpenML 310 | 260 / 10923 | ✅ |
| oil | OpenML 311 | 41 / 896 | ✅ |
| qsar-biodeg | OpenML 1494 | 替代 E-state（D3） | 待验证 |
| kddcup99 | OpenML 1113 | 替代 Can（D4） | 待验证 |
| creditcard | OpenML 1597 | 扩展用外部验证 | 待验证 |

## 当前状态

- ✅ 加载器与论文样本数对齐（7 个原始数据集中 6 个完全一致，satimage 为 OpenML 版本差异）
- ✅ 采样器/学习器/指标/主网格脚本 + 单测
- ✅ Pima 冒烟：剪枝树（C4.5 代理）AUC 约 0.76–0.79，SMOTE(200%) > RUS(1:1)，方向与论文一致
- ⬜ 全部数据集主网格（等 B 的 `data/processed` 与 `splits.json`）
- ⬜ 显著性检验、扩展实验（k 敏感性 / 4 变体 / credit-card 外部验证 / 阈值代价）
- ⬜ 报告与 slides（C）

## 引用

```
@article{chawla2002smote,
  title={SMOTE: synthetic minority over-sampling technique},
  author={Chawla, Nitesh V and Bowyer, Kevin W and Hall, Lawrence O and Kegelmeyer, W Philip},
  journal={Journal of Artificial Intelligence Research},
  volume={16}, pages={321--357}, year={2002}
}
```
