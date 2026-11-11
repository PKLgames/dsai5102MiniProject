# DATA CARD（数据卡）

> 状态：**骨架（A 预填，B 在 H2/H3 补实测值）** · 2026-11-11
> 填写人：B · 审阅：A · 报告 §3 的唯一来源。
> 规则（沿用 `docs/TEMPLATE_DATA_CARD.md`）：这里写的每一步，`src/data_prep.py` 里都必须有对应代码；否则删掉这句话。每个数字必须来自 `data/manifests/*.json`，不许手抄。
> ⚠️ 与旧模板的差别：UMAP 复现**没有**正类/少数类/不平衡比 IR/重采样，别套分类项目的口径。

## 1. 数据集总表

| 名称 | 来源（URL / OpenML did） | 原文 n × d | 实测 n × d | 类数 | 每类计数 | 用途（C1–C4） | 状态 |
|---|---|---|---|---|---|---|---|
| PenDigits | `sklearn.datasets.load_digits()`（原始 UCI pen-digits 的 8×8 子集） | 1797 × 64 | 1797 × 64 | 10 | 178–183 | C2、C4 | ✅ 已核（冒烟） |
| COIL-20 | https://www.cs.columbia.edu/CAVE/databases/SLAM_coil-20_coil-100/coil-20/coil-20-proc.zip | 1440 × 16384 | 1440 × 16384 | 20 | 72 × 20 | C1、C2、C3、C4 | ✅ 已核（文件 1440 张） |
| Shuttle | OpenML `data_id=40685` | 58000 × 9 | 待 H1 实测 | 7 | 待测（极不平衡，类 1 ≈ 80%） | C2、C3（替代 Flow）、C4 | ⏳ 待 B |
| MNIST | OpenML `data_id=554` | 70000 × 784 | 待实测（应 70000）→ 子采样 20000 | 10 | 子采样后 2000 × 10 | C1、C2、C4 | ⏳ 待 B |
| Fashion-MNIST | OpenML `data_id=40996` | 70000 × 784 | 待实测（应 70000）→ 子采样 20000 | 10 | 子采样后 2000 × 10 | C1、C2、C4 | ⏳ 待 B |

**替换说明**：原文的 COIL-100 / scRNA / Flow Cytometry / GoogleNews 不复现（见 `docs/DEVIATIONS.md` D4/D15）；C3 用 Shuttle + COIL-20 替代 Flow。**PenDigits 用的是 1797 版**（原文 §5 明确 "1797 grayscale images ... 8x8 ... 64 dimensional vector"），不是 OpenML did=32 的 10992 条版本。

## 2. 预处理步骤（每步写清"为什么"）

> 编号对应 `docs/PROTOCOL.md` §3.2 的 P1–P9；B 在每行末尾补 `src/data_prep.py:行号`。

| 编号 | 步骤 | 为什么（写进报告 §3） | 代码位置 |
|---|---|---|---|
| P1 | `X` → float32 C 序；`y` → int64，类别按首次出现排序编码 0..K−1 | 跨脚本/跨机可比；与 sklearn `LabelEncoder` 一致 | `data_prep.py:待填` |
| P2 | 仅 `/255` 落到 [0,1]（MNIST/FMNIST/COIL-20）；PenDigits 已是 0–16 小整数，不再缩放；**不做标准化** | UMAP 的模糊图对均匀缩放不变：σ、ρ 同比缩放，`exp(−(d−ρ)/σ)` 与 `min_dist` 拟合出的 a/b 都不变；因此缩放对 UMAP 是无操作。统一口径是为了不让"预处理差异"被误读成"算法差异" | `data_prep.py:待填` |
| P3 | 图像行优先展平（`(28,28)`→784、`(128,128)`→16384），不转置 | 与原文 "treated as a single ... vector" 一致 | `data_prep.py:待填` |
| P4 | 不去重；只统计重复行数 | 去重会改变 n，破坏与原文计数对齐 | `data_prep.py:待填` |
| P5 | 出现 NaN/inf 立即 fail，不填补 | 这 5 个数据集不该有缺失；出现即 loader bug | `data_prep.py:待填` |
| P6 | 落盘 `{name}.npz`（键 `X`、`y`，`savez_compressed`） | 单文件、无 pickle、可 mmap | `data_prep.py:待填` |
| P7 | manifest 存 `array_sha256 = sha256(X.float32 C 序字节 + y.int64 字节)` | npz 文件哈希含 zip 时间戳、不稳定；数组内容哈希才可重放 | `data_prep.py:待填` |
| P8 | 时间戳 UTC ISO8601 | 跨机交接可读 | `data_prep.py:待填` |
| P9 | MNIST/FMNIST 子采样：每类 `default_rng(42+c)` 取 2000 个（`replace=False`），按原行号排序 | 内存与 t-SNE 时间；且 20 折下测试集 1000 点 < k=3200，20k 下 5 折才能让 k=3200 可训练 | `data_prep.py:待填` |

**明确没做的事**（避免报告里被误读）：没做特征选择、没做 PCA 预降维（原文对 scRNA 才做）、没做离群点剔除、没做数据增强、没在折内做任何依赖标签的变换（本来也没有标签依赖步骤）。

## 3. 划分与产物

- 折数：`pendigits 10 / coil20 10 / shuttle 10 / mnist 5 / fmnist 5`（依据 `configs/main.yaml`；MNIST/FMNIST 的 5 折理由见 P9）。
- `splits.json`：`{"seed": 42, "datasets": {name: {"n", "n_folds", "folds": [{"train": [...], "test": [...]}]}}, "config_sha256"}`；行号指 npz 行序；`StratifiedKFold(shuffle=True, random_state=42)`。
- 产物与校验：

| 文件 | 内容 | 复核命令 |
|---|---|---|
| `data/processed/{name}.npz` | `X` float32 (n,d)、`y` int64 (n,) | `python -c "import numpy as np;z=np.load('data/processed/coil20.npz');print(z['X'].shape,z['y'].shape,z['X'].dtype)"` |
| `data/manifests/{name}.json` | §B3 全部键 | `python -c "import json;print(json.load(open('data/manifests/coil20.json'))['n'])"` |
| `data/manifests/splits.json` | 折划分 | 见 `HANDOFF_B2A.md` V3 |
| `data/raw/_fetch_log.json` | 源 URL + sha256 + 字节数 + 时间 | 见 V0 |

- **不入库**：`data/processed/*.npz` 与 `data/raw/*` 被 `.gitignore` 忽略；入库的只有 manifest、splits、脚本。这样别人 clone 后跑 `fetch_data.py` + `data_prep.py` 就能重放（V2 保证逐位相同）。

## 4. EDA 图（`figures/eda/`，英文标注，dpi ≥ 160）

| 文件 | 内容 | 一句结论（图注首句，B 填） | 状态 |
|---|---|---|---|
| `eda_01_class_counts.png` | 5 集类分布（Shuttle 对数轴） | 待填 | ⏳ |
| `eda_02_sample_grid.png` | COIL-20/MNIST/FMNIST 各 5×5 样本 | 待填 | ⏳ |
| `eda_03_pixel_hist.png` | 像素直方图（/255 前后） | 待填 | ⏳ |
| `eda_04_class_means.png` | COIL-20 每类均值图（4×5） | 待填 | ⏳ |
| `eda_05_pca_scatter.png` | 每集 PCA 前两维散点 | 待填 | ⏳ |
| `eda_06_data_quality.png` | 重复行/NaN/近零方差特征计数 | 待填 | ⏳ |

## 5. 自检结果（B 在 H2/H3 贴输出）

```
$ python -m pytest -q tests/test_data_contract.py
（待填）

$ python src/data_prep.py --emit-card-table
（待填，需与 §1 表格逐格一致）

$ sha256 重算（V2）
（待填）
```

- [ ] 5 个 npz 齐全，dtype/shape 正确
- [ ] `n` 与 §1 一致（mnist/fmnist 为 20000 子采样）
- [ ] 无 NaN/inf，`X ∈ [0,1]`
- [ ] `array_sha256` 重放一致
- [ ] `splits.json` 重跑 md5 相同、train∩test=∅、覆盖全部行
- [ ] 每个处理步骤有 `data_prep.py:行号`
- [ ] 图内无中文、dpi ≥ 160

## 6. 已知问题与影响

1. **Shuttle 类别极不平衡**（类 1 ≈ 80%）：kNN 准确率整体偏高（原文 PCA 都有 0.78–0.83），比较要只看**方法间差异**，不看绝对值；分层 10 折时最小类每折 test 侧可能只有 1 个点，方差会大——与原文一致（原文也因类别规模限制用了 10 折）。
2. **MNIST/FMNIST 子采样**：20k vs 70k，C2 只判方向（D5/D11）；大 k（≥1600）时 kNN 接近先验分类器。
3. **OpenML 版本差异**：不同时间拉的 MNIST 行序可能不同 → `array_sha256` 是唯一判据；报告里给 did 而不给具体快照时间，需补 `retrieved_utc`。
4. **COIL-20 图像来源**：`coil-20-proc` 是"已裁剪 + 旋转对齐"的版本（原文用的也是它），像素是否 `/255` 原文未明说 → 已登记 D9，敏感性实验覆盖。
5. **PenDigits 两个版本**：sklearn 1797 条（我们用）vs OpenML 10992 条（16 维）；用错版本会让 C2 完全不可比。

## 7. 交接一句话

B 交 H2 时，本文件只需 §1–§3 与 §5 的前三项为真；H3 时 §4/§6 补齐，且 V7（数据卡数字 = manifest）与 V8（图）通过。核验细节见 `docs/HANDOFF_B2A.md`。
