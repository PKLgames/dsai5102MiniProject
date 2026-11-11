# A 任务书（本机计算 · 自研 UMAP 与主表）

> 你负责 **P2–P6**（P1 环境冒烟已完成），发 **S1**（Day1 10:00）与 **S3**（Day2 22:00）。口径见 `docs/goal/SPEC.md`；验收见 `docs/tasks/A_ACCEPTANCE.md`。
> 原则：**A 不等人**。数据自己从 `data/raw` 读，B 的 npz 只用于对拍（P9），不进你的计算路径。

## 0. 边界

- ✅ 可改：`src/data.py`、`src/umap_impl/**`、`src/*_eval.py`、`scripts/run_grid.py`、`scripts/run_runtime.py`、`tests/**`、`configs/**`、`results/*.csv`、`results/embeddings/**`、`results/README_numbers.md`、`docs/goal/SPEC.md`、`docs/log/**`
- ❌ 不改：`src/data_prep.py`、`scripts/fetch_data.py`、`scripts/make_splits.py`、`scripts/make_figures.py`、`data/`、`figures/**`、`docs/goal/DATA_CARD.md`、`report/`、`slides/`（这些是 B/C 的）

## 1. 环境事实（已实测，不要重新发现）

| 项 | 事实 |
|---|---|
| Python | 3.14.7（`.venv`）；numpy 2.5.4 / scipy 1.18.1 / sklearn 1.9.1 / umap-learn 0.6.0 / numba 0.68.1 / matplotlib 3.11.2 |
| 机器 | 16 vCPU / **7.5 GB RAM** / 无 GPU；当前 available ≈4 GB |
| 线程 | joblib 每次 import 都警告 `[Errno 13] Permission denied. joblib will operate in serial mode` → **按单核算**；`export NUMBA_NUM_THREADS=1` |
| 字体 | matplotlib 无中文字体 → 图内英文（你不出图，但 debug 时注意） |
| 包管理 | `~/.cache` 不可写；装包用 `UV_CACHE_DIR=$PWD/.uvcache UV_PYTHON_INSTALL_DIR=$PWD/.uvpython`；pyarrow 装不上，一律 CSV/npz |

## 2. 节点

### P2 数据契约（→ S1 的一部分）

- `src/data.py`：`load(name) -> (X: np.ndarray float32 (n,d), y: ndarray int64 (n,))`，只读 `data/raw/`，实现 `docs/goal/SPEC.md` §3 P1–P8。
  - PenDigits：`sklearn.datasets.load_digits()`，`X = d.data.astype(np.float32)/16.0`（原值 0–16 → /16 落 [0,1]），`y` 按首次出现编码。
  - COIL-20：读 `data/raw/coil20/coil-20-proc/` 下 1440 个 PNG，**正则** `obj(\d+)__(\d+)\.png`（不能用 `split("__")` 就完事，类号在 `objK` 里），`plt.imread`/`PIL` → float32 `/255`，按 (类号, 序号) 排序后行优先展平 16384 维。标签 = 类号 1..20 → 0..19（首次出现序）。
  - `array_sha256` 严格按 SPEC P7。
- `tests/test_data_contract.py`：≥6 用例——形状/dtype、n 精确（1797/1440）、`isfinite`、标签覆盖、值域、**两次调用 sha 相同**、标签与类别计数一致。
- **S1 发布**：`src/data.py` 的签名 + `tests/` + `results/README_numbers.md` 占位模板（键名见 C 任务书 C1b）+ 一页占位符清单。发到 main，`git tag s1`。

### P3 自研前两件

- `src/umap_impl/fuzzy.py`：kNN 图 → 局部模糊单纯集（原文 Algorithm 1/2），`n_neighbors=15`；ρ = 最近邻距离，σ 由二分求得使 `Σexp(−(d_ij−ρ_i)/σ_i)=log2(n)`（Algorithm 3）。
- `src/umap_impl/spectral.py`：对称归一化 Laplacian 的前 2 个非平凡特征向量，Arpack（`eigsh`），符号对齐。
- 判据：与 umap-learn 的 `smooth_knn_dist`/`spectral_layout` 对比，ρ/σ 相对误差 <1e-6，初始化符号对齐后余弦 >0.99。**对拍脚本留在 `tests/test_umap_parts.py`**（用 umap-learn 的私有函数，版本固定 0.6.0，别升级）。

### P4 自研闭环

- `src/umap_impl/optimize.py`：负采样 SGD，`Φ(x,y)=(1+a‖x−y‖²ᵇ)⁻¹`；a/b 由 `min_dist=0.1` 曲线非线性最小二乘拟合（`scipy.optimize.curve_fit`）；负样本按 `deg^0.75` 采样。
- `src/umap_impl/umap.py`：`fit(X) -> E (n,2) float32`，串起 P3+P4；`n_epochs=500`，`random_state=42`。
- 判据：PenDigits 上 `kNN@10` 与 umap-learn 差 ≤0.02、无 NaN、`silhouette_score(E,y)>0.1`。若差 >0.02，先查（a）kNN 图是否对称化、（b）负采样分布、（c）`a/b` 拟合，再考虑降级（PLAN §4 第 1 条）。

### P5 主表（→ S3）

- `scripts/run_grid.py`：2 数据集 × 10 折 × 4 方法 × 5 k = 400 行 → `results/grid_knn.csv`（列：`dataset,fold,method,k,acc`），聚合 `grid_knn_summary.csv`。
- 折从 `data/manifests/splits.json` 读（B 在 P8 产出；若未到，用 `sklearn StratifiedKFold(10, shuffle=True, random_state=42)` 现算，事后核对一致）。
- 降维在每个 fold 的 train 行上 fit，得到全体点坐标（transductive），kNN 只在 train 坐标+标签上训，test 坐标上评（SPEC §4 E2）。
- 每折结果**落盘一行一写**，中断可续跑（`--resume`）。
- `scripts/run_runtime.py`：4 行 fit 秒数（3 次中位数）→ `results/runtime.csv`。
- `results/paper_vs_ours.csv`：`dataset,method,k,paper_acc,paper_std,our_acc,our_std,delta,n_folds,verifiable`（原文值查 `docs/goal/PAPER_DATA.md`；COIL-20 大 k `verifiable=false`）。
- 导出 `results/embeddings/coil20_{umapours,tsne}.npz`（键 `E` float32、`y` int64）给 B 出图。
- 判据：行数 400；**重跑一次逐折差 = 0**（同 seed 同机器应字节级一致；若 float 抖动，记录 `max|diff|` 并说明）。

### P6 数字终版（→ S3 的一部分）

- `results/README_numbers.md`：填满 S1 的模板（结构逐键一致，C 要机械替换）；每个数字后面括号注 `grid_knn.csv:行号`；给出每条判定（复现/部分复现/未复现）。
- 判据：C 能只读这一个文件写出 §4；抽查任意 3 个数字能对上 csv。

## 3. 常见坑

1. `load_digits()` 是 1797 条、像素 0–16；**不要**去 OpenML 拉 did=32（10992 条，口径不同）。
2. COIL-20 的 PNG 是灰度 `uint8`；`plt.imread` 若返回 float 已除 255，先看 dtype 再决定除不除。
3. `StratifiedKFold` 在 1797 条 10 折下每折 179/180，k=160 时 train 侧每类仅 ~145 → `k < train 规模` 断言要按**每类**检查，不能只看总数。
4. numba 首次 JIT 有 10–30 s 启动开销，计时实验要 warm-up 一次再计。
5. umap-learn 的 `random_state` 只固定初始化与负采样，SGD 中途顺序仍受内部 RNG 影响 → 重跑一致性优先在同一进程内验证。
