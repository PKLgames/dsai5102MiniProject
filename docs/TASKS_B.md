# 成员 B 任务书（数据准备 + EDA）

> 角色：把**本轮 2 个公开数据集（`pendigits`、`coil20`）**变成**建模可直接吃的规范数组 + 折划分 + 数据卡 + EDA 图**，写成**独立于 A 建模代码的第二实现**。
> ⚠️ 范围修订 v2（2026-11-12，`docs/DEVIATIONS.md` D18）：`shuttle` / `mnist` / `fmnist` **本轮不交付**。下文凡出现这 3 个名字，都是「代码保留但不启用」或「通用规则示例」，不要为它们花时间。
> 论文：UMAP（arXiv:1802.03426）。协议：`docs/PROTOCOL.md` §3。交接核验标准：`docs/HANDOFF_B2A.md`（**必须逐条对照**）。
> 本文件替代旧的 SMOTE 口径任务书；旧口径里的"I R / 正类 / 重采样"在 UMAP 复现里**不存在**，不要沿用。

## 0. 边界

- ✅ 可改：`scripts/fetch_data.py`、`src/data_prep.py`、`scripts/make_splits.py`（P2b）、`scripts/make_figures.py`（P7c）、`data/`、`figures/eda/`、`figures/results/`、`docs/DATA_CARD.md`、`notebooks/`（仅 EDA）
- ❌ 不改：`src/data.py`、`src/umap_impl/`、`src/*_eval.py`、`docs/PROTOCOL.md`、`docs/DEVIATIONS.md`、`results/`、`configs/`
- 为什么必须独立实现：A 的 `src/data.py` 是建模侧 loader，你这份是**审阅侧**。两边独立写、逐个数组对拍，才能抓出"A 的 loader 有 bug 但实验照样出数"这类最贵的错误。**禁止 `import` A 的 loader 来省事**。

## 0.1 你的位置：审计，不是上游（重要）

`PLAN.md` §2 把依赖改成三条独立轨道。对你的三条后果：

1. **A 不等你的 npz**：A 直接从 `data/raw` 算 canonical 数组并跑主表；你的 `data/processed/*.npz` 是**对拍用的审计产物**，不进入主表计算路径。
2. 所以你的价值在**独立实现 + 对拍**：两边都按 `PROTOCOL.md` P1–P9 写，`max|dX|` 必须是 0；不为 0 就说明其中一方错了 → 开 D 条目、写清差在哪一步（这一步的诊断比数据本身更值钱）。
3. 你**不需要**等人：唯一前置是 S1（A 在 Day 1 10:00 发的 `src/data.py` 签名 + `tests/`）。S1 晚了就照本文件 §1 的字段表自己定签名，A 事后对齐——不要空等。
4. P1 交付后立刻做 **P7b 自审**：把自己的 npz 与 A 的 canonical 数组对拍（命令见 `HANDOFF_B2A.md` V4），把 `max|dX|` 与结论写进 `HANDOFF_LOG.md`。**不用等 A 来叫你做**。

## 1. 交付物

### B1 `scripts/fetch_data.py` —— 可重复、可续传的下载器

- 本轮 2 个源，各自落到 `data/raw/<name>/`（另 3 个已移出范围，`fetch` 里保留入口但默认不跑）：

| name | 源 | 落地形态 |
|---|---|---|
| `pendigits` | `sklearn.datasets.load_digits()`（离线自带） | 不需要下载；`fetch` 里只做可用性检查 |
| `coil20` | `https://www.cs.columbia.edu/CAVE/databases/SLAM_coil-20_coil-100/coil-20/coil-20-proc.zip` | 解压到 `data/raw/coil20/coil-20-proc/*.png`（1440 张，已有） |
| ~~`shuttle`~~ | ~~OpenML `data_id=40685`~~ | 本轮不交付（D18） |
| ~~`mnist`~~ | ~~OpenML `data_id=554`~~ | 本轮不交付（D18） |
| ~~`fmnist`~~ | ~~OpenML `data_id=40996`~~ | 本轮不交付（D18） |

- 要求：`--datasets all|name`；已存在且校验通过则跳过（幂等）；输出每个源的 `sha256` 与字节数到 `data/raw/_fetch_log.json`（含 UTC 时间戳）；
  断网重试 3 次（指数退避），失败**退出码非 0**并打印缺哪个源；**不静默跳过**。
- 注意本机：`~/.cache` 不可写 → `fetch_openml(..., data_home="data/raw/sklearn_cache")`；沙箱里一次只能 curl 一个 URL。

### B2 `src/data_prep.py` —— 独立 loader → 规范数组

- 必须暴露（A 的契约测试会 `import` 它）：

```python
# 本轮只启用前两个（D18）；其余保留在清单里，供 11-18 后有余量时直接打开
DATASETS = ["pendigits", "coil20"]  # 全量清单：pendigits, coil20, shuttle, mnist, fmnist
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

- **这个脚本归你（P2b）**：从 `docs/templates/make_splits.py.template`（75 行，已含 StratifiedKFold + 折大小检查 + 字节稳定落盘）落地，参数化到你的 `build()`。A 只跑 pytest 验不变量，**不写这个脚本、也不改你的逻辑**。
- 折数按 `configs/main.yaml`：**pendigits 10、coil20 10**（本轮只这两个；shuttle/mnist/fmnist 的 10/5/5 折已随 D18 移出）。
- 内容：`{"seed": 42, "datasets": {name: {"n": int, "n_folds": int, "folds": [{"train": [...], "test": [...]}]}}, "config_sha256": "..."}`，行号指 `data/processed/{name}.npz` 里的行序。
- 落盘 `json.dumps(..., sort_keys=True, indent=1)`；重跑必须**字节相同**（A 会比对 md5）。

### B5 `docs/DATA_CARD.md` —— 数据卡（报告 §3 的唯一来源）

按 `docs/TEMPLATE_DATA_CARD.md` 的六节写，但按 UMAP 改写：**没有不平衡比 IR、没有正类、没有重采样**。必须覆盖：

1. 总表：名称 / 源 URL 或 did / 原文 n×d / 实测 n×d / 类数 / 每类计数 / 用途（对应 C1–C4）/ 许可或引用；
2. 预处理：P1–P9 逐条 + **为什么**（UMAP 的均匀缩放不变性要写进去，这是 P2 的依据）；
3. 划分与产物：折数、seed、子采样规则、文件路径、sha256；
4. EDA 图清单（§B6 的 **3 张必做**；另 3 张标为可选，本轮不做）；
5. 自检结果（贴 `pytest` 与哈希比对的输出摘要）；
6. 已知问题：数据集版本差异、类别极度不平衡（Shuttle ~80% 类 1）、OpenML 列名可能随版本变、子采样对结论的影响（转 `DEVIATIONS.md` D5/D13）。

**硬要求**：数据卡里每一句"我们做了 X"都要能在 `src/data_prep.py` 找到行号；写 `data_prep.py:88` 这种引用。

### B6 `figures/eda/` —— **3 张必做图**（英文标注，dpi ≥ 160，无中文）

> 范围 v2（D18）：本轮只要 `eda_01`、`eda_02`、`eda_03`。后三张保留说明，**不做**，别花时间。

| 文件 | 内容 | 一句结论（图注首句） |
|---|---|---|
| `eda_01_class_counts.png` | **2 个数据集**的类分布（PenDigits 10 类×179/180；COIL-20 20 类×72） | 哪些集不平衡（答案：都不平衡） |
| `eda_02_sample_grid.png` | **COIL-20** 每个子集 5×5 样本网格（含标签） | 同一类长什么样 |
| `eda_03_pixel_hist.png` | 像素值直方图（/255 前后各一条） | 预处理前后分布 |
| ~~`eda_04_class_means.png`~~ | COIL-20 每类均值图（20 张拼 4×5） | 本轮不做（D18） |
| ~~`eda_05_pca_scatter.png`~~ | 每集 PCA 前两维散点 | 本轮不做（D18，PCA 结果由 P6 主表覆盖） |
| ~~`eda_06_data_quality.png`~~ | 重复行/NaN/近零方差计数 | 本轮不做（V5 的数值自检已覆盖） |

### B7 结果图（P7c）—— 报告的 Fig.2 / Fig.3，由你出

> 为什么是你：这两张图是「读 csv → 画图」的机械活，A 的时间要留给算法；而且图要反复调字号/边距，交互式工作不适合塞进 A 的收尾。

**输入（A 在 S3 交付，你只读不改）**

| 文件 | 内容 |
|---|---|
| `results/embeddings/coil20_umapours.npz` | 键 `E`（1440×2 float32）、`y`（1440 int64） |
| `results/embeddings/coil20_tsne.npz` | 同上，t-SNE 的 2 维坐标 |
| `results/paper_vs_ours.csv` | 列：`dataset,k,method,ours_mean,paper_value,verdict` |
| `results/grid_knn.csv` | 逐折明细（要点核对时用） |

**Fig.2 定性嵌入**（`figures/results/fig2_qualitative_coil20.png`）
- 1×2 两联：左 UMAP（自研）、右 t-SNE；点按类别着色（`plt.cm.tab20`，20 类足够区分）；**不画标题以外的装饰**；
- 同一数据、同一坐标尺度（两图各自等比例，不要强行同 scale）；图例放在图下方一行（20 项，2 列）；
- 图注首句必须是结论，例如「COIL-20 上自研 UMAP 与 t-SNE 呈现同类的簇结构」（终稿措辞由 C 定）。

**Fig.3 原文 vs 我们**（`figures/results/fig3_paper_vs_ours.png`）
- 散点：x = 原文值、y = 我们值，画 y=x 参考虚线；只画 C2 的 2 个数据集 × 5 个 k × 4 种方法中**有原文数值的方法**（t-SNE / UMAP / PCA）；
- COIL-20 的 k=80/160 用空心标记 + 标注「未复现（D9）」；PenDigits 用实心；
- 轴标注英文 `Paper kNN accuracy` / `Our kNN accuracy`，范围锁 0.4–1.0 便于跨图比较。

**硬要求**：300 dpi、图内无中文（本机无中文字体）、脚本 `scripts/make_figures.py` 可一键重跑、图内数字与 csv 一致（A 抽查 3 点）。**不阻塞任何人**——A 的 P8 与 C 的 §4 文字都不依赖这两张图，最坏情况 A 用同一脚本 30 min 出简版。

### B8 交接（不写代码，但必须做）

- 按 `docs/HANDOFF_B2A.md` 的自查表逐条跑命令、留输出；
- 在 `docs/HANDOFF_LOG.md` 填一行（时间、分支、tag、自查结论、未解决项）；
- 打 tag：`git tag handoff-h1`（11-12 12:00）/ `handoff-h2`（11-12 22:00）/ `handoff-h3`（11-13 22:00，数据卡终版）/ `handoff-h3b`（S3 后 3 h，结果图）。

## 2. 三个时点（迟到的后果写在这里）

| 时点 | 交付 | 迟到后果 |
|---|---|---|
| **H1 · 11-12 12:00** | B1 完成 + 每个数据集的 `(n, d)` 实测值 + 下载耗时 | 到 11-12 18:00 仍未过 → A 用自建 loader 顶上并标注「B 未交付」，B 改为只交 EDA |
| **H2 · 11-12 22:00** | B2/B3/B4 全量 + 自查通过（= P1） | 到 11-13 02:00 仍未过 → A 用自建 processed 继续；数据卡由 A 代笔，Team 维度在报告里如实写分工 |
| **H3 · 11-13 22:00** | B5/B6 终版 + 哈希复核（= P7） | 报告的 Data 一节降级为 A 的简版，EDA 图从报告里删掉 |
| **S3+3h · 11-14 01:00** | B7 两张结果图（= P7c） | C 先用临时版式，A 用同一脚本出简版；报告 v1 在 11-18，有 4 天余量 |

**S2 迟到不传染**：A 的 P5/P6 用自己的 canonical 数组继续跑，报告也照常写；你晚一天只让 P1/P7/P7b 三格变红，不影响别人。反过来说——**你没有「等 A 先跑通」这个借口了**：开工只等 S1 的签名。

**提前交付**优先于完美：H2 时 manifest 里 `notes` 可以粗糙，但 `array_sha256` 必须对。

## 3. 自检清单（交接前自己先跑一遍）

```bash
cd /home/pklgames/coding/dsai5102MiniProject
source .venv/bin/activate

python scripts/fetch_data.py --datasets all           # 幂等，第二次应 0 下载
python src/data_prep.py --datasets all --force
python scripts/make_splits.py                         # 你维护（P2b）
python -m pytest -q tests/test_data_contract.py       # 由 A 提供，你只跑
python scripts/check_manifest.py                      # A 提供，逐键核对 manifest 与数组
git status --short                                    # 只应有 §0 允许的路径
```

- [ ] 2 个 npz 齐全（`pendigits.npz`、`coil20.npz`），`X.dtype=float32`、`y.dtype=int64`、`X.shape[0]==y.shape[0]`
- [ ] `n` 与 `PAPER_COUNTS` 一致：**1797 / 1440，精确相等**（子采样项本轮不涉及）
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
5. **样本数核对**（本轮）：`pendigits` 必须是 sklearn `load_digits()` 的 **1797**（若拿到 10992 说明误用了 OpenML did=32，与原文不符）；`coil20` 必须是 **1440**（20 类 × 72）。MNIST/FMNIST 的子采样口径（每类 2000 → 20000）本轮不涉及，保留在 `PROTOCOL.md` P9 备用。
6. **子采样必须在折划分之前**（P9），否则同一类在折内分布会变；且子采样要按类内 `default_rng(42+c)`，不要用全局 rng（顺序依赖）。
7. 别把 `data/processed/*.npz` 提交进 git（`.gitignore` 已忽略）；只提交 manifest 与脚本。
8. 内存：MNIST 70000×784 float32 = 220 MB，子采样前不要同时保留 int64 副本（会 440 MB）；用 `np.empty(..., dtype=np.float32)` 逐块填。

## 5. 分支与协作

- 分支：`git checkout -b data-prep`；只提交 §0 允许的路径；push 后由 A 合并并打 tag。
- 卡住：先查 `docs/PROTOCOL.md` §3 与 `docs/HANDOFF_B2A.md`；仍不清楚再问 A，**不要**自行改协议。
- 与 C 的接口：C 只读 `docs/DATA_CARD.md` 与 `figures/eda/*`，不读你的脚本。
