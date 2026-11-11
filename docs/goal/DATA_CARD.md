# DATA CARD（数据卡）

> 状态：**骨架（A 预填，B 在 S2/S4 补实测值）** · 2026-11-12
> 填写人：B · 审阅：A · 报告 §3 的唯一来源。
> 规则：这里写的每一步，`src/data_prep.py` 里都必须有对应代码；否则删掉这句话。每个数字必须来自 `data/manifests/*.json`，不许手抄。
> ⚠️ 与旧模板的差别：UMAP 复现**没有**正类/少数类/不平衡比 IR/重采样，别套分类项目的口径。

## 1. 数据集总表

| 名称 | 来源（URL / OpenML did） | 原文 n × d | 实测 n × d | 类数 | 每类计数 | 用途（C1–C4） | 状态 |
|---|---|---|---|---|---|---|---|
| PenDigits | `sklearn.datasets.load_digits()`（原始 UCI pen-digits 的 8×8 子集） | 1797 × 64 | 1797 × 64 | 10 | 178–183 | C2、C4 | ✅ 已核（冒烟） |
| COIL-20 | https://www.cs.columbia.edu/CAVE/databases/SLAM_coil-20_coil-100/coil-20/coil-20-proc.zip | 1440 × 16384 | 1440 × 16384 | 20 | 72 × 20 | C1、C2、C3、C4 | ✅ 已核（文件 1440 张） |
| Shuttle | OpenML `data_id=40685` | 58000 × 9 | 原文口径，本轮不交付（D18） | 7 | ~80% 类 1 | 未使用 | — |
| MNIST | OpenML `data_id=554` | 70000 × 784 | 原文口径，本轮不交付（D18） | 10 | 7000 × 10 | 未使用 | — |
| Fashion-MNIST | OpenML `data_id=40996` | 70000 × 784 | 原文口径，本轮不交付（D18） | 10 | 7000 × 10 | 未使用 | — |

**替换说明**：原文的 COIL-100 / scRNA / Flow Cytometry / GoogleNews 不复现（见 `docs/log/DEVIATIONS.md` D4/D15）；C3 用 Shuttle + COIL-20 替代 Flow。**PenDigits 用的是 1797 版**（原文 §5 明确 "1797 grayscale images ... 8x8 ... 64 dimensional vector"），不是 OpenML did=32 的 10992 条版本。

## 2. 预处理步骤（每步写清"为什么"）

> 编号对应 `docs/goal/SPEC.md` §3 的 R1–R9；B 在每行末尾补 `src/data_prep.py:行号`。

| 编号 | 步骤 | 为什么（写进报告 §3） | 代码位置 |
|---|---|---|---|
| R1 | `X` → float32 C 序；`y` → int64，类别按首次出现排序编码 0..K−1 | 跨脚本/跨机可比；与 sklearn `LabelEncoder` 一致 | `data_prep.py:待填` |
| R2 | COIL-20 仅 `/255` 落到 [0,1]；PenDigits 已是 0–16 小整数，`/16` 到 [0,1]；**不做标准化** | UMAP 的模糊图对均匀缩放不变：σ、ρ 同比缩放，`exp(−(d−ρ)/σ)` 与 `min_dist` 拟合出的 a/b 都不变；因此缩放对 UMAP 是无操作。统一口径是为了不让"预处理差异"被误读成"算法差异" | `data_prep.py:待填` |
| R3 | 图像行优先展平（`(28,28)`→784、`(128,128)`→16384），不转置 | 与原文 "treated as a single ... vector" 一致 | `data_prep.py:待填` |
| R4 | 不去重；只统计重复行数 | 去重会改变 n，破坏与原文计数对齐 | `data_prep.py:待填` |
| R5 | 出现 NaN/inf 立即 fail，不填补 | 这两个数据集不该有缺失；出现即 loader bug | `data_prep.py:待填` |
| R6 | 落盘 `{name}.npz`（键 `X`、`y`，`savez_compressed`） | 单文件、无 pickle、可 mmap | `data_prep.py:待填` |
| R7 | manifest 存 `array_sha256 = sha256(X.float32 C 序字节 + y.int64 字节)` | npz 文件哈希含 zip 时间戳、不稳定；数组内容哈希才可重放 | `data_prep.py:待填` |
| R8 | 时间戳 UTC ISO8601 | 跨机交接可读 | `data_prep.py:待填` |
| R9 | 划分：`StratifiedKFold(10, shuffle=True, random_state=42)`；本轮**无子采样**（子采样口径随 D18 作废） | 与原文 10 折一致；随机性由 seed 冻结承担 | `data_prep.py:待填` |

**明确没做的事**（避免报告里被误读）：没做特征选择、没做 PCA 预降维（原文对 scRNA 才做）、没做离群点剔除、没做数据增强、没在折内做任何依赖标签的变换（本来也没有标签依赖步骤）。

## 3. 划分与产物

- 折数：`pendigits 10 / coil20 10`（依据 `configs/main.yaml`；其余数据集不交付）。
- `splits.json`：`{"seed": 42, "datasets": {name: {"n", "n_folds", "folds": [{"train": [...], "test": [...]}]}}, "config_sha256"}`；行号指 npz 行序；`StratifiedKFold(shuffle=True, random_state=42)`。
- 产物与校验：

| 文件 | 内容 | 复核命令 |
|---|---|---|
| `data/processed/{name}.npz` | `X` float32 (n,d)、`y` int64 (n,) | `python -c "import numpy as np;z=np.load('data/processed/coil20.npz');print(z['X'].shape,z['y'].shape,z['X'].dtype)"` |
| `data/manifests/{name}.json` | §B3 全部键 | `python -c "import json;print(json.load(open('data/manifests/coil20.json'))['n'])"` |
| `data/manifests/splits.json` | 折划分 | 见 `docs/tasks/B_ACCEPTANCE.md`「契约与划分不变量」 |
| `data/raw/_fetch_log.json` | 源 URL + sha256 + 字节数 + 时间 | 见 `docs/tasks/B_ACCEPTANCE.md`「源可追溯」 |

- **不入库**：`data/processed/*.npz` 与 `data/raw/*` 被 `.gitignore` 忽略；入库的只有 manifest、splits、脚本。这样别人 clone 后跑 `fetch_data.py` + `data_prep.py` 就能重放（「哈希重放」保证逐位相同）。

## 4. EDA 图（`figures/eda/`，英文标注，dpi ≥ 160）

| 文件 | 内容 | 一句结论（图注首句，B 填） | 状态 |
|---|---|---|---|
| `eda_01_class_counts.png` | 2 集类分布（PenDigits 10 类、COIL-20 20 类） | 待填 | ⏳ |
| `eda_02_sample_grid.png` | COIL-20 各 5×5 样本网格 | 待填 | ⏳ |
| `eda_03_pixel_hist.png` | 像素直方图（/255 前后） | 待填 | ⏳ |
| ~~`eda_04`~~ | 本轮不做（D18） | — | ⚫ |
| ~~`eda_05`~~ | 本轮不做（D18） | — | ⚫ |
| ~~`eda_06`~~ | 本轮不做（D18） | — | ⚫ |

## 5. 自检结果（B 在 S2 时贴输出）

```
$ python -m pytest -q tests/test_data_contract.py
（待填）

$ python src/data_prep.py --emit-card-table
（待填，需与 §1 表格逐格一致）

$ 哈希重放（见 `docs/tasks/B_ACCEPTANCE.md`）
（待填）
```

- [ ] 2 个 npz 齐全（`pendigits.npz`、`coil20.npz`），dtype/shape 正确
- [ ] `n` 与 §1 一致（1797 / 1440，精确相等）
- [ ] 无 NaN/inf，`X ∈ [0,1]`
- [ ] `array_sha256` 重放一致
- [ ] `splits.json` 重跑 md5 相同、train∩test=∅、覆盖全部行
- [ ] 每个处理步骤有 `data_prep.py:行号`
- [ ] 图内无中文、dpi ≥ 160

## 6. 已知问题与影响

1. **COIL-20 类别平衡但样本少**（每类 72）：10 折后每折 test 侧每类 7 张，kNN 在大 k（≥80）时方差增大，比较只看方法间差异。
2. **原文未披露的预处理**：COIL-20 像素是否 `/255`、UMAP 超参取值原文均未明说 → 已登记 D2/D9。
3. **数据版本**：PenDigits 用 sklearn 的 1797 条（非 OpenML did=32 的 10992 条）；MNIST/FMNIST/Shuttle 本轮不交付（D18）。
4. **COIL-20 图像来源**：`coil-20-proc` 是"已裁剪 + 旋转对齐"的版本（原文用的也是它），像素是否 `/255` 原文未明说 → 已登记 D9，敏感性实验覆盖。
5. **PenDigits 两个版本**：sklearn 1797 条（我们用）vs OpenML 10992 条（16 维）；用错版本会让 C2 完全不可比。

## 7. 交接一句话

B 交 **S2** 时本文件只需 §1–§3 与 §5 的前三项为真；**S4** 前补齐 §4/§6，并让「数据卡数字 = manifest」与「图可读」两项检查通过。核验细节见 `docs/tasks/B_ACCEPTANCE.md`。
