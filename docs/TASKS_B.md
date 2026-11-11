# 成员 B 任务书（数据准备 + EDA）

> 角色：把 5 个公开数据集变成**建模可直接吃的规范数组 + 折划分 + 数据卡 + EDA 图**，写成**独立于 A 建模代码的第二实现**。
> 论文：UMAP（arXiv:1802.03426）。协议：`docs/PROTOCOL.md` §3。交接核验标准：`docs/HANDOFF_B2A.md`（**必须逐条对照**）。
> 本文件替代旧的 SMOTE 口径任务书；旧口径里的"I R / 正类 / 重采样"在 UMAP 复现里**不存在**，不要沿用。

## 0. 边界

- ✅ 可改：`scripts/fetch_data.py`、`src/data_prep.py`、`data/`、`figures/eda/`、`docs/DATA_CARD.md`、`notebooks/`（仅 EDA）
- ❌ 不改：`src/data.py`、`src/umap_impl/`、`src/*_eval.py`、`docs/PROTOCOL.md`、`docs/DEVIATIONS.md`、`results/`、`configs/`
- 为什么必须独立实现：A 的 `src/data.py` 是建模侧 loader，你这份是**审阅侧**。两边独立写、逐个数组对拍，才能抓出"A 的 loader 有 bug 但实验照样出数"这类最贵的错误。**禁止 `import` A 的 loader 来省事**。

## 1. 交付物

### B1 `scripts/fetch_data.py` —— 可重复、可续传的下载器

- 5 个源，各自落到 `data/raw/<name>/`：

| name | 源 | 落地形态 |
|---|---|---|
| `pendigits` | `sklearn.datasets.load_digits()`（离线自带） | 不需要下载；`fetch` 里只做可用性检查 |
| `coil20` | `https://www.cs.columbia.edu/CAVE/databases/SLAM_coil-20_coil-100/coil-20/coil-20-proc.zip` | 解压到 `data/raw/coil20/coil-20-proc/*.png`（1440 张，已有） |
| `shuttle` | OpenML `data_id=40685` | `data/raw/shuttle/shuttle.csv.gz`（或 sklearn cache） |
| `mnist` | OpenML `data_id=554` | `data/raw/mnist/mnist.csv.gz` |
| `fmnist` | OpenML `data_id=40996` | `data/raw/fmnist/fmnist.csv.gz` |

- 要求：`--datasets all|name`；已存在且校验通过则跳过（幂等）；输出每个源的 `sha256` 与字节数到 `data/raw/_fetch_log.json`（含 UTC 时间戳）；
  断网重试 3 次（指数退避），失败**退出码非 0**并打印缺哪个源；**不静默跳过**。
- 注意本机：`~/.cache` 不可写 → `fetch_openml(..., data_home="data/raw/sklearn_cache")`；沙箱里一次只能 curl 一个 URL。

### B2 `src/data_prep.py` —— 独立 loader → 规范数组

- 必须暴露（A 的契约测试会 `import` 它）：

```python
DATASETS = ["pendigits", "coil20", "shuttle", "mnist", "fmnist"]
PAPER_COUNTS = {"pendigits": 1797, "coil20": 1440, "shuttle": 58000, "mnist": 70000, "fmnist": 70000}
SUBSAMPLE = {"mnist": 20000, "fmnist": 20000}   # 其余为 None

def load_raw(name: str) -> tuple[np.ndarray, np.ndarray]:
    """返回原始 (X, y)，未做 P2/P9；用于 A 的对拍。"""

def build(name: str) -> tuple[np.ndarray, np.ndarray]:
    """返回规范 (X float32 C 序 (n,d), y int64 (n,))；按 PROTOCOL §3.2 P1–P9 执行。"""
```

- CLI：
  - `python src/data_prep.py --datasets all` → 写 `data/processed/{name}.npz` + `data/manifests/{name}.json`；`--force` 才重写。
  - `--out DIR`：把产物写到别处（A 做"重放核验"时用，见 `docs/HANDOFF_B2A.md` V2）；**必须支持**。
  - `--emit-card-table`：把数据卡 §1 的 markdown 表格打印到 stdout（A 用它核对数据卡数字与 manifest 一致，见 V7）；**必须支持**。
- 规范决策**照抄** `docs/PROTOCOL.md` §3.2 的 P1–P9（float32 / 不做缩放仅 `/255` / 行优先展平 / 不去重 / fail-on-NaN / npz 键名 / array_sha256 / UTC / 每类 2000 子采样）。**一处都不许自己改**；觉得要改 → 找 A 改协议，不许先斩后奏。

### B3 `data/manifests/{name}.json`（字段固定，A 的 V2 会逐键读）

```json
{
  "dataset": "coil20",
  "n": 1440, "n_features": 16384, "n_classes": 20,
  "class_counts": {"0": 72, "1": 72},
  "label_map": {"0": "obj1"},
  "nan": 0, "inf": 0, "duplicate_rows": 0,
  "min": 0.0, "max": 1.0,
  "array_sha256": "<sha256(X.float32 C 序字节 + y.int64 字节)>",
  "source": "https://www.cs.columbia.edu/CAVE/databases/SLAM_coil-20_coil-100/coil-20/coil-20-proc.zip",
  "source_sha256": "<zip 的 sha256>",
  "retrieved_utc": "2026-11-12T14:03:00Z",
  "prep_seconds": 42.1,
  "notes": "每类 72 张；objK__NN.png 解析；行优先展平；/255"
}
```

- `array_sha256` 的算法必须与 A 完全一致（`hashlib.sha256(np.ascontiguousarray(X, np.float32).tobytes() + np.ascontiguousarray(y, np.int64).tobytes()).hexdigest()`）。**不要**用 npz 文件哈希（zip 时间戳不稳定）。

### B4 `data/manifests/splits.json` —— 折划分

- 用 A 提供的 `scripts/make_splits.py`（参数化到你的 `build()`），**不许手写、不许改脚本逻辑**。
- 折数按 `configs/main.yaml`：pendigits 10、coil20 10、shuttle 10、mnist 5、fmnist 5（原因见 PROTOCOL §3.4：20k 子采样下 k=3200 要求测试集 ≥3200）。
- 内容：`{"seed": 42, "datasets": {name: {"n": int, "n_folds": int, "folds": [{"train": [...], "test": [...]}]}}, "config_sha256": "..."}`，行号指 `data/processed/{name}.npz` 里的行序。
- 落盘 `json.dumps(..., sort_keys=True, indent=1)`；重跑必须**字节相同**（A 会比对 md5）。

### B5 `docs/DATA_CARD.md` —— 数据卡（报告 §3 的唯一来源）

按 `docs/TEMPLATE_DATA_CARD.md` 的六节写，但按 UMAP 改写：**没有不平衡比 IR、没有正类、没有重采样**。必须覆盖：

1. 总表：名称 / 源 URL 或 did / 原文 n×d / 实测 n×d / 类数 / 每类计数 / 用途（对应 C1–C4）/ 许可或引用；
2. 预处理：P1–P9 逐条 + **为什么**（UMAP 的均匀缩放不变性要写进去，这是 P2 的依据）；
3. 划分与产物：折数、seed、子采样规则、文件路径、sha256；
4. EDA 图清单（§B6 的 6 张）；
5. 自检结果（贴 `pytest` 与哈希比对的输出摘要）；
6. 已知问题：数据集版本差异、类别极度不平衡（Shuttle ~80% 类 1）、OpenML 列名可能随版本变、子采样对结论的影响（转 `DEVIATIONS.md` D5/D13）。

**硬要求**：数据卡里每一句"我们做了 X"都要能在 `src/data_prep.py` 找到行号；写 `data_prep.py:88` 这种引用。

### B6 `figures/eda/` —— 6 张图（英文标注，dpi ≥ 160，无中文）

| 文件 | 内容 | 一句结论（图注首句） |
|---|---|---|
| `eda_01_class_counts.png` | 5 数据集的类分布（Shuttle 用对数轴） | 哪些集不平衡 |
| `eda_02_sample_grid.png` | COIL-20/MNIST/FMNIST 各 5×5 样本网格（含标签） | 同一类长什么样 |
| `eda_03_pixel_hist.png` | 像素值直方图（/255 前后各一条） | 预处理前后分布 |
| `eda_04_class_means.png` | COIL-20 每类均值图（20 张小图拼成 4×5） | 类间差异是否显著 |
| `eda_05_pca_scatter.png` | 每集 PCA 前两维散点（按类着色） | 线性方法能不能分开 |
| `eda_06_data_quality.png` | 重复行数 / NaN / 近零方差特征计数（条形） | 数据有多干净 |

### B7 交接（不写代码，但必须做）

- 按 `docs/HANDOFF_B2A.md` 的自查表逐条跑命令、留输出；
- 在 `docs/HANDOFF_LOG.md` 填一行（时间、分支、tag、自查结论、未解决项）；
- 打 tag：`git tag handoff-h1`（11-12 晚）/ `handoff-h2`（11-13 晚）/ `handoff-h3`（11-17，数据卡终版）。

## 2. 三个时点（迟到的后果写在这里）

| 时点 | 交付 | 迟到后果 |
|---|---|---|
| **H1 · 11-12 22:00** | B1 完成 + 每个数据集的 `(n, d)` 实测值 + 下载耗时 | A 的 A1 空转 → 11-13 起 A 用自建 loader 顶上，B 改为只交 EDA |
| **H2 · 11-13 22:00** | B2/B3/B4 全量 + 自查通过 | A 用 `src/data.py` 自建 processed（数据卡由 A 代笔）；Team 维度在报告里如实写分工 |
| **H3 · 11-17 22:00** | B5/B6 终版 + 哈希复核 | 报告的 Data 一节降级为 A 的简版，EDA 图从报告里删掉 |

**提前交付**优先于完美：H2 时 manifest 里 `notes` 可以粗糙，但 `array_sha256` 必须对。

## 3. 自检清单（交接前自己先跑一遍）

```bash
cd /home/pklgames/coding/dsai5102MiniProject
source .venv/bin/activate

python scripts/fetch_data.py --datasets all           # 幂等，第二次应 0 下载
python src/data_prep.py --datasets all --force
python scripts/make_splits.py
python -m pytest -q tests/test_data_contract.py       # 由 A 提供，你只跑
python scripts/check_manifest.py                      # A 提供，逐键核对 manifest 与数组
git status --short                                    # 只应有 §0 允许的路径
```

- [ ] 5 个 npz 齐全，`X.dtype=float32`、`y.dtype=int64`、`X.shape[0]==y.shape[0]`
- [ ] `n` 与 `PAPER_COUNTS` 一致（mnist/fmnist 为 20000 子采样，需在数据卡注明）
- [ ] 每类计数 ≥ 该数据集 k 网格的最大 k 的 1/10（10 折时每折 train 侧每类 ≥ k）——**先算再写**，Shuttle 类 2/3/6 只有几十个样本，注意 10 折分层是否可行
- [ ] 无 NaN/inf，`0 ≤ X.min() ≤ X.max() ≤ 1+1e-6`
- [ ] `array_sha256` 重算一致（`python -c` 一行即可）
- [ ] `splits.json` 重跑 md5 相同；train/test 无交集且并集 = 全部行号
- [ ] 数据卡里每个数字都来自 manifest，没有手抄

> Shuttle 分层 10 折的坑：最小类只有 ~10 个样本（原文说 "due to constraints imposed by class sizes and the stratified sampling"）。若某类 < 10，`StratifiedKFold` 仍可跑但每折 test 可能 1 个；**不要自行改成非分层**，先报给 A，由 A 决定是否在协议里加一条（偏离 D 编号）。

## 4. 针对本论文的已知坑（从旧项目迁移 + 新增）

1. **COIL-20 文件命名**是 `obj{K}__{NN}.png`（两个下划线），K=1..20，NN=0..71。用正则 `obj(\d+)__(\d+)\.png` 解析，不要 `split('_')`（会切错）。
2. **图像 dtype**：PNG 读出可能是 `uint8` 或 `float64`（`plt.imread` 会给 0–1 浮点）。统一 `np.asarray(Image.open(p), dtype=np.float32) / 255.0`，并在数据卡写清用的是 PIL 还是 matplotlib（两者对灰度/调色板图行为不同）。
3. **OpenML 的 target 列名**通常是 `"class"`，但随版本可能变；先 `df.columns` + `df.iloc[:, -1].value_counts()` 核对，别硬编码。MNIST/FMNIST 的 target 是字符串数字，`astype(int)` 前先看有没有缺失。
4. **Shuttle 标签是 1..7**，不是 0..6；P1 的重编码会改变显示，但 `label_map` 必须记录原值。
5. **样本数核对**：MNIST/FMNIST 若从 OpenML 拿到的是 70000（应为），子采样后 20000；`PAPER_COUNTS` 对 mnist/fmnist 检查的是**原始** 70000，别把 20000 当成错。
6. **子采样必须在折划分之前**（P9），否则同一类在折内分布会变；且子采样要按类内 `default_rng(42+c)`，不要用全局 rng（顺序依赖）。
7. 别把 `data/processed/*.npz` 提交进 git（`.gitignore` 已忽略）；只提交 manifest 与脚本。
8. 内存：MNIST 70000×784 float32 = 220 MB，子采样前不要同时保留 int64 副本（会 440 MB）；用 `np.empty(..., dtype=np.float32)` 逐块填。

## 5. 分支与协作

- 分支：`git checkout -b data-prep`；只提交 §0 允许的路径；push 后由 A 合并并打 tag。
- 卡住：先查 `docs/PROTOCOL.md` §3 与 `docs/HANDOFF_B2A.md`；仍不清楚再问 A，**不要**自行改协议。
- 与 C 的接口：C 只读 `docs/DATA_CARD.md` 与 `figures/eda/*`，不读你的脚本。
