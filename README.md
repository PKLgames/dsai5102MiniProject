# DSAI5102 Mini-Project · 论文复现（第二轮，待选题）

Format 2.2「学术论文复现」的工作区。上一轮复现的 SMOTE（Chawla et al., JAIR 2002）已按用户要求移出工作区，
其完整内容保留在 git tag `smote-repro-v1`（见 `FOR_NEXT_ROUND.md` §9）。

**新一轮约束**：论文发表年份 **2010 年至今**（用户 2026-11-11 放宽）；其余要求不变（核心统计 DM / ML 方法、可复现、易写报告）。
任务原文见 `project_request.txt`。

- 交接说明（先读这个）：`FOR_NEXT_ROUND.md`
- 第一轮选题经验与检查表：`selecting_exp.md`
- 报告结构（按评分表映射）：`docs/REPORT_OUTLINE.md`
- 复现协议模板 / 数据卡模板：`docs/TEMPLATE_PROTOCOL.md`、`docs/TEMPLATE_DATA_CARD.md`
- 分工任务书：`docs/TASKS_B.md`（数据准备 + EDA）、`docs/TASKS_C.md`（报告 + slides）

## 目录

```
src/              建模与实验代码（待新论文确定后填充）
scripts/          一次性脚本（取数、划分、出图、检验）
tests/            pytest 单测（数据契约、划分重放、指标）
configs/          实验矩阵配置（yaml）
docs/             协议、数据卡、报告大纲、任务书、代码模板
data/raw/         原始数据（不入库）
data/processed/   建模数据表 + splits.json（不入库）
data/manifests/   数据契约清单（行数/特征/标签分布，入库）
results/          逐折结果与汇总表（入库）
figures/          eda/ 与 results/ 图（入库）
notebooks/        探索性分析（B 组员）
report/           报告源文件（C 组员）
slides/           答辩 slides（C 组员）
```

## 环境

已验证：16 vCPU / 7.5 GB 内存 / 无 GPU / Python 3.14.7（`.venv` 已就绪，无需重建）。

```bash
# 补装/升级依赖（沙箱内需要指定缓存与 Python 目录）
UV_CACHE_DIR=/home/pklgames/coding/.uvcache \
UV_PYTHON_INSTALL_DIR=/home/pklgames/coding/.uvpython \
uv pip install --python .venv/bin/python -r requirements.txt

# 测试：目前 tests/ 为空（骨架在 docs/templates/test_data_contract.py.template），
# 新论文落地后 .venv/bin/python -m pytest tests/ -q
```

## 约定（与第一轮相同，仍然有效）

- **重采样/特征变换只在训练折内**，折划分固定种子，任何人重跑得到同一数字；
- **数据契约优先级**：`data/manifests/*.json` 是样本数真值，加载即校验，不符直接报错；
- **偏离日志**：与原文的每一处不同都写进 `docs/DEVIATIONS.md`（模板见 PROTOCOL 模板末节）；
- **等价判据**：复现不追求绝对小数复刻，用「方向一致 + 排序一致 + |Δ| ≤ 阈值」三件套；
- 图与表都用英文标注（本机 matplotlib 无中文字体）。
