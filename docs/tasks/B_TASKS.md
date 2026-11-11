# B 任务书（数据 · 折划分 · 数据卡 · 结果图）

> 你负责 **P7–P11**，发 **S2**（Day1 22:00，数据包）与 **S4**（S3 后 3 h，结果图）。口径见 `docs/goal/SPEC.md` §2–§3；验收见 `docs/tasks/B_ACCEPTANCE.md`。
> §0.1 一句话：**你是审计者，不是上游**。A 的主表只吃他自己从 `data/raw` 算的数组，你的 npz 只用于对拍——所以你晚交不会卡住别人，但也没有「等 A 先跑通」的借口。

## 0. 边界

- ✅ 可改：`scripts/fetch_data.py`、`src/data_prep.py`、`scripts/make_splits.py`、`scripts/make_figures.py`、`data/**`、`figures/**`、`docs/goal/DATA_CARD.md`、`docs/log/HANDOFF_LOG.md`
- ❌ 不改：`src/data.py`、`src/umap_impl/**`、`src/*_eval.py`、`tests/**`、`configs/**`、`results/**`、`docs/goal/SPEC.md`、`docs/log/DEVIATIONS.md`、`report/`、`slides/`
- 唯一前置：**S1**（A 的 `src/data.py` 签名 + `tests/`）。S1 晚了就照本文件字段表自己定签名，A 事后对齐。

## 1. P7 数据包（→ S2）

### fetch_data.py
- 幂等：已存在且 sha256 匹配就跳过；写 `data/raw/_fetch_log.json`，每个数据集一条 `{url, sha256, bytes, retrieved_utc}`。
- 本轮只需两个源：`sklearn.datasets.load_digits()`（无需下载）与已在盘上的 `data/raw/coil20/coil-20-proc/`（1440 张 PNG）；写日志时记录 zip 或目录的 sha256。

### src/data_prep.py
```python
DATASETS = ["pendigits", "coil20"]
PAPER_COUNTS = {"pendigits": 1797, "coil20": 1440}
def load_raw(name) -> tuple[np.ndarray, np.ndarray]: ...   # 未归一化，供 A 对拍
def build(name) -> tuple[np.ndarray, np.ndarray]: ...      # 规范数组：float32 / int64 / [0,1]
```
- CLI 必须支持：`--datasets {all,名称}`、`--force`、`--out DIR`（A 重放核验用）、`--emit-card-table`（打印数据卡 §1 的表，A 核验用）。
- 规范细节照抄 `docs/goal/SPEC.md` §3 R1–R8：float32 C 序、int64、类别按首次出现编码、**不标准化**（仅 `/255`）、行优先展平、不去重、fail-on-NaN、npz 键 `X`/`y`、UTC 时间。

### manifest 字段（固定，A 逐键读）
```json
{"dataset":"coil20","n":1440,"n_features":16384,"n_classes":20,
 "class_counts":{"0":72},"label_map":{"0":"obj1"},
 "nan":0,"inf":0,"duplicate_rows":0,"min":0.0,"max":1.0,
 "array_sha256":"<sha256(X.float32 C 序字节 + y.int64 字节)>",
 "source":"coil-20-proc.zip","source_sha256":"<...>",
 "retrieved_utc":"2026-11-12T14:03:00Z","prep_seconds":42.1,
 "notes":"objK__NN.png 正则解析；PIL；行优先"}
```
`array_sha256` 必须与 A 同算法：`hashlib.sha256(np.ascontiguousarray(X, np.float32).tobytes() + np.ascontiguousarray(y, np.int64).tobytes()).hexdigest()`。**不要用 npz 文件哈希**（zip 时间戳不稳定）。

## 2. P8 折划分（→ 随 S2）

`scripts/make_splits.py` 由**你维护**（A 只跑 pytest 验不变量）：

```python
from sklearn.model_selection import StratifiedKFold
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
for name in DATASETS:
    X, y = build(name)
    folds = [{"train": tr.tolist(), "test": te.tolist()} for tr, te in skf.split(X, y)]
    # 校验：train∩test=∅、并集=全量、折大小差≤1
```
- 落盘 `data/manifests/splits.json`：`json.dumps({"seed":42,"datasets":{...}}, sort_keys=True, indent=1)`，**重跑字节相同**。
- 存行号不存数据；行号对应 `npz` 的行序。

## 3. P9 审计对拍（P7 完成后立刻做，不用等 A 叫）

```bash
python -c "
import numpy as np
from src.data import load as load_a          # A 的 canonical
import src.data_prep as B
for n in ('pendigits','coil20'):
    Xa, ya = load_a(n); Xb, yb = B.build(n)
    print(n, 'max|dX| =', float(np.abs(Xa.astype(np.float64)-Xb.astype(np.float64)).max()), 'y_equal =', bool((ya==yb).all()))
"
```
- 期望：`max|dX| = 0.0`、`y_equal = True`。不为 0 → 按「值域/展平顺序/标签编码/PNG dtype」逐步二分，把结论写进 `docs/log/HANDOFF_LOG.md`；若定位到协议本身歧义，报 A 开 D 条目。

## 4. P10 数据卡 + EDA

- `docs/goal/DATA_CARD.md` 六节按 UMAP 口径写（**没有 IR、没有正类、没有重采样**）：数据来源与版本、预处理决策（每条带 `data_prep.py:行号`）、划分与产物、EDA 图说明、自检结果、已知问题。
- `figures/eda/` 三张，英文标注、dpi ≥160、无中文方框：
  - `eda_01_class_counts.png`：两数据集类分布（PenDigits 10 类 ×179/180；COIL-20 20 类 ×72）
  - `eda_02_sample_grid.png`：COIL-20 每类 5×5 样本网格（含标签）
  - `eda_03_pixel_hist.png`：像素值直方图（`/255` 前 vs 后）

## 5. P11 结果图（→ S4，只读 A 的 S3）

| 输入（只读） | 内容 |
|---|---|
| `results/embeddings/coil20_umapours.npz` | 键 `E`（1440×2 float32）、`y`（1440 int64） |
| `results/embeddings/coil20_tsne.npz` | 同上 |
| `results/paper_vs_ours.csv` | `dataset,method,k,paper_acc,paper_std,our_acc,our_std,delta,n_folds,verifiable` |

- **Fig.2** `figures/results/fig2_qualitative_coil20.png`：1×2 两联（左 UMAP-ours、右 t-SNE），点按类别 `tab20` 着色，图例 2 列置底，300 dpi。
- **Fig.3** `figures/results/fig3_paper_vs_ours.png`：散点 x=原文、y=我们，y=x 虚线；`verifiable=false` 的点用空心并注「未复现（D9）」；轴范围 0.4–1.0，英文轴标。
- `scripts/make_figures.py` 一键重跑；图内数字必须与 csv 一致（A 抽查 3 点）。

## 6. 坑（都踩过一次的）

1. COIL-20 命名 `obj{K}__{NN}.png`（双下划线），**用正则** `obj(\d+)__(\d+)\.png`，不要 `split('__')` 后乱取。
2. PNG dtype：`PIL` 给 `uint8`、`plt.imread` 给 float 0–1。统一 `np.asarray(Image.open(p), dtype=np.float32)/255.0`，数据卡写明用了哪个库。
3. `load_digits()` 是 **1797** 条、像素 0–16；拿到 10992 说明误用 OpenML did=32（口径不同）。
4. `StratifiedKFold` 分层后每折 179/180；k 网格最大 160 时，**train 侧每类**只有 ~145，跑 kNN 要按每类检查 `k < 每类 train 数`。
5. `splits.json` 必须字节稳定：`sort_keys=True, indent=1`，不要 `ensure_ascii=False` 之外的随机键序。
6. 不把 `data/processed/*.npz` 提交进 git（已 ignore）；只提交脚本 + manifest + splits。

## 7. 发布（S2 / S4）

```bash
git checkout -b data-prep          # 只提交 §0 允许的路径
python scripts/fetch_data.py --datasets all && python src/data_prep.py --datasets all --force && python scripts/make_splits.py
python -m pytest -q tests/         # A 的契约测试，你只跑
git add -A && git commit -m "data: S2 数据包（npz+manifest+splits）" && git push -u origin data-prep
git tag s2 && git push origin s2
```
- S2 → `docs/log/HANDOFF_LOG.md` 记一行（时间、tag、自查输出、未解决项）。
- S4 → tag `s4`，同样记一行。迟到后果见 `PLAN.md` §4（只影响自己那几格）。
