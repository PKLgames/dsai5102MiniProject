# B → A 交接与核验标准（Handoff Contract）

> 版本 v1 · 2026-11-11 · 甲方（接收/核验）：A（本机）· 乙方（交付）：B
> 目的：让 A **不问 B 一句话**就能判定"这批数据能不能进主实验"。凡是不能由命令复现的交付，一律不算交付。
> 关联：`docs/TASKS_B.md`（做什么）、`docs/PROTOCOL.md` §3（规范口径）、`docs/DEVIATIONS.md`（偏离）、`docs/HANDOFF_LOG.md`（记录）

---

## 0. 四条原则

1. **命令即证据**。B 的每条「已完成」都要附一条可重跑的命令 + 它的输出；A 只认命令输出，不认文字描述。
2. **A 的核验必须独立于 B 的脚本**。A 用自己的 `src/data.py` 读同一批原始数据，逐个数组比；B 的 loader 写得对不对，不看代码看数组。
3. **宁可退回，不将就**。数据错一格，主表全废；退回一次的成本是 2 小时，返工一次的成本是 2 天。
4. **交接是审计，不是上游（`PLAN.md` §2）**。A 的主表只吃自己从 `data/raw` 算出的 canonical 数组，**不等** B 的 npz；B 的 npz 用于对拍。所以 H2 被退回**不会**让主表停摆——只让 P1/P7/P7b 变红。这条同时决定了两件事：B 晚交不连累别人；A 也没有「等数据到了再写」的余地。

## 1. 三个交接时点与形式

| 时点 | 内容 | 形式 | 核验预算 |
|---|---|---|---|
| **H1 · 2026-11-12 12:00** | **2 个**数据源（`pendigits`、`coil20`）可达性 + 每个 `(n, d)` 实测 + 下载耗时 | `data-prep` 分支 push + tag `handoff-h1` + `HANDOFF_LOG.md` 一行 | 20 min（只跑 V0/V1） |
| **H2 · 2026-11-12 22:00** | `npz` + `manifest` + `splits.json` 全量（= `PLAN.md` **P1**，审计产物） | push + tag `handoff-h2` | 60 min（V1–V6） |
| **H3 · 2026-11-13 22:00** | 数据卡终版 + **3 张** EDA 图 + 哈希复核（= `PLAN.md` **P7**） | push + tag `handoff-h3` | 30 min（V7–V8） |

> ⏱ 时点按**两日核心计划**（`PLAN.md` v2）压缩：H1 12:00 / H2 22:00 / H3 次日 22:00。**核验项一个不删**，只是窗口更短——所以 B 的自检必须一次过。

- **同机交接**（B 也在这台机器上）：文件直接在工作区，仍必须走同一个分支 + tag 流程，保证 A 看到的是"B 提交过的版本"而不是 B 工作区里的半成品。
- **远程交接**：`git push origin data-prep --tags`；A 先 `git fetch --tags` 再核验。**不允许**用聊天窗口发文件。
- tag 只打一次；若交接后要改，打 `handoff-h2b`，并说明上一版为何不合格（记录在 `HANDOFF_LOG.md`）。

## 2. 交接包清单（缺一项即不完整）

| # | 路径 | 必备内容 | 检查者 |
|---|---|---|---|
| 1 | `scripts/fetch_data.py` | `--datasets` 参数、幂等、`_fetch_log.json`（源 URL + sha256 + 字节数 + UTC 时间） | V0 |
| 2 | `src/data_prep.py` | `DATASETS`、`PAPER_COUNTS`、`load_raw()`、`build()`、CLI（`--out`、`--force`、`--emit-card-table`） | V3 |
| 3 | `data/processed/{name}.npz` ×2（pendigits、coil20） | 键 `X`(float32)、`y`(int64)；**不入 git**，由脚本重放生成 | V2 |
| 4 | `data/manifests/{name}.json` ×2 | §B3 的 **全部**键（n/n_features/n_classes/class_counts/label_map/nan/inf/duplicate_rows/min/max/array_sha256/source/source_sha256/retrieved_utc/prep_seconds/notes） | V2/V5 |
| 5 | `data/manifests/splits.json` + `scripts/make_splits.py` | `seed`、每数据集 `n/n_folds/folds[train,test]`、`config_sha256`；脚本可一键重跑（**B 负责写（P2b），A 只验**） | V3 |
| 6 | `docs/DATA_CARD.md` | 六节齐全（§B5），每个数字来自 manifest，处理步骤带 `data_prep.py:行号` | V7 |
| 7 | `figures/eda/eda_0{1..3}_*.png` | **3 张**，英文标注，dpi ≥ 160 | V8 |
| 8 | `docs/HANDOFF_LOG.md` 一行 | 时间、tag、B 的自证清单勾选、未解决项 | 人工 |
| 9 | `figures/results/fig2_*.png`、`fig3_*.png`（**P7c，S3 后 3 h**） | 2 张，300 dpi，英文标注；数值与 `results/*.csv` 一致 | V9 |

## 3. A 的核验流程（V0–V9）

所有命令在 `/home/pklgames/coding/dsai5102MiniProject` 下、`.venv` 激活状态下执行。**每条都要记录实际输出**到 `HANDOFF_LOG.md`。

### V0 · 源可追溯（H1 只跑这条）

```bash
python - <<'EOF'
import json, pathlib
log = json.load(open("data/raw/_fetch_log.json"))
for k, v in log.items():
    print(k, v["bytes"], v["sha256"][:12], v["url"])
EOF
```

- 期望：**2 个 key**（`pendigits`、`coil20`；前者可标 `sklearn`）；每个 `sha256` 非空；`bytes > 0`。
- 范围提醒（D18）：`shuttle`/`mnist`/`fmnist` 本轮不交付，`_fetch_log.json` 里**没有**这 3 个 key 属正常，不算缺项。
- 判定：缺 key / sha 为空 → **退**（无法证明用的是哪个版本的数据）。

### V1 · 路径边界

```bash
git fetch origin data-prep --tags
git diff --name-only main...data-prep
```

- 期望：只有 `scripts/fetch_data.py`、`src/data_prep.py`、`data/manifests/**`、`docs/DATA_CARD.md`、`figures/eda/**`、`notebooks/**`。
- 出现 `src/umap_impl/**`、`src/data.py`、`results/**`、`configs/**`、`docs/PROTOCOL.md` → **退**（越界修改，说明 B 在改不该改的东西）。
- 附：`git diff --numstat main...data-prep -- data/processed` 应为空（npz 不入库）。

### V2 · 内容哈希重放（**最关键的一条**）

```bash
rm -rf /tmp/replay_h2
python src/data_prep.py --datasets all --out /tmp/replay_h2
python - <<'EOF'
import json, hashlib, numpy as np, pathlib
ok = True
for mf in sorted(pathlib.Path("/tmp/replay_h2").glob("*.json")):
    m = json.load(open(mf))
    z = np.load(f"/tmp/replay_h2/{m['dataset']}.npz")
    h = hashlib.sha256(np.ascontiguousarray(z["X"], np.float32).tobytes()
                       + np.ascontiguousarray(z["y"], np.int64).tobytes()).hexdigest()
    ref = json.load(open(f"data/manifests/{m['dataset']}.json"))["array_sha256"]
    same = (h == ref)
    ok &= same
    print(f"{m['dataset']:10s} n={m['n']:6d} d={m['n_features']:6d} sha={h[:12]} {'OK' if same else 'MISMATCH'}")
print("V2:", "PASS" if ok else "FAIL")
EOF
```

- 期望：5 行全 `OK`，末行 `V2: PASS`。
- 判定：任何一个 MISMATCH → **退**。这说明 B 的产物依赖了随机性/未固定顺序/网络变化，不可复现。
- 注意：比的是**数组哈希**，不是 npz 文件哈希（zip 时间戳会让文件哈希每次都变，这条是故意的）。

### V3 · 契约测试 + 划分不变量

```bash
python -m pytest -q tests/test_data_contract.py     # A 提供
python - <<'EOF'
import json, numpy as np
sp = json.load(open("data/manifests/splits.json"))
for name, d in sp["datasets"].items():
    n = d["n"]; allidx = np.arange(n); seen = np.zeros(n, int)
    for f in d["folds"]:
        tr, te = np.array(f["train"]), np.array(f["test"])
        assert len(np.intersect1d(tr, te)) == 0, f"{name}: train/test overlap"
        assert len(np.union1d(tr, te)) == n, f"{name}: coverage {len(np.union1d(tr,te))} != {n}"
        seen[te] += 1
    assert seen.max() - seen.min() <= 1, f"{name}: folds unbalanced in size"
    print(f"{name:10s} n={n:6d} folds={len(d['folds'])} sizes={seen.tolist()[:3]}...")
print("V3: PASS")
EOF
```

- 期望：`pytest` 全绿（`5 passed`，无 xfail 掩盖）；每数据集无重叠、全覆盖、折大小差 ≤1。
- 判定：pytest 有 fail → **退**；只有 skip（缺文件）→ 视为未交付，**退**。
- 折数必须 = `configs/main.yaml`（10/10/10/5/5）；不符 → 先查是脚本参数还是 B 手写，一律**退**。

### V4 · 双实现对拍（A 的 `src/data.py` vs B 的 npz）

```bash
python - <<'EOF'
import numpy as np, json
from src.data import load            # A 的实现
for name in ["pendigits", "coil20"]:  # D18：本轮只 2 个
    Xa, ya = load(name)
    z = np.load(f"data/processed/{name}.npz"); Xb, yb = z["X"], z["y"]
    assert Xa.shape == Xb.shape and ya.shape == yb.shape, name
    assert Xa.dtype == np.float32 and Xb.dtype == np.float32 and yb.dtype == np.int64
    same_y = np.array_equal(ya, yb)
    d = float(np.abs(Xa - Xb).max())
    print(f"{name:10s} shape={Xa.shape} max|dX|={d:.3e} y_equal={same_y}")
    assert same_y and d == 0.0, f"{name}: A 与 B 不一致"
print("V4: PASS")
EOF
```

- 期望：`max|dX| = 0.000e+00`、`y_equal=True`（同一原始数据 + 确定性运算，必须逐位相等）。
- 若 `0 < d ≤ 1e-6`：允许，但必须查清原因（通常是 `/255` 与 `astype` 顺序不同）并记入 `DEVIATIONS.md`（D 编号），**A 决定采用哪一侧作为主**，两侧都必须重放到该侧的值。
- 若 `d > 1e-6` 或 `y_equal=False` → **退**（标签/行序不同是最危险的静默错误）。

### V5 · 完整性与分布

```bash
python - <<'EOF'
import json, numpy as np
for name in ["pendigits", "coil20"]:  # D18：本轮只 2 个
    z = np.load(f"data/processed/{name}.npz"); X, y = z["X"], z["y"]
    m = json.load(open(f"data/manifests/{name}.json"))
    nan = int(np.isnan(X).sum() + np.isnan(y).sum())
    inf = int(np.isinf(X).sum())
    dup = int(len(np.unique(X, axis=0)) != len(X))
    cc = {int(k): int(v) for k, v in m["class_counts"].items()}
    assert nan == m["nan"] == 0, (name, nan)
    assert inf == m["inf"] == 0
    assert int(dup) == m["duplicate_rows"]
    assert np.array_equal(np.bincount(y), np.array([cc[i] for i in range(len(cc))]))
    assert X.min() >= 0 and X.max() <= 1.0 + 1e-6, (name, X.min(), X.max())
    assert len(m["label_map"]) == m["n_classes"] == len(np.unique(y))
    print(f"{name:10s} n={len(y):6d} K={m['n_classes']:2d} min_class={min(cc.values()):4d} max={X.max():.3f}")
print("V5: PASS")
EOF
```

- 期望：`V5: PASS`；每数据集各类计数与数据卡一致；`min_class` ≥ 该数据集最大 k 的 1/2（10 折时每折 test 侧每类至少 1）。
- Shuttle 最小类若 < 10 → 不视为失败，但必须已在数据卡写明，且 A 确认 `StratifiedKFold` 仍可运行。

### V6 · 资源上限

```bash
/usr/bin/time -v python src/data_prep.py --datasets all --out /tmp/replay_v6 2>&1 | grep -E "Elapsed|Maximum resident"
```

- 期望：`Elapsed ≤ 30:00`、`Maximum resident ≤ 3 GB`（本机 7.5 GB，要留 4 GB 给训练）。
- 判定：超时 → 退并协商"预处理拆两段"（下载与转换分离）；超内存 → 退，改用分块写盘。

### V7 · 文档可追溯

```bash
python src/data_prep.py --emit-card-table > /tmp/card_table.md
diff <(sed -n '/^| 名称/,/^$/p' docs/DATA_CARD.md) /tmp/card_table.md || echo "CARD TABLE DRIFT"
grep -o "data_prep\.py:[0-9]*" docs/DATA_CARD.md | sort -u | head
for ref in $(grep -o "data_prep\.py:[0-9]*" docs/DATA_CARD.md | cut -d: -f2 | sort -u); do
  [ "$ref" -le "$(wc -l < src/data_prep.py)" ] || echo "STALE REF $ref"
done
```

- 期望：无 `CARD TABLE DRIFT`、无 `STALE REF`；数据卡 §2 每条决策后都有行号引用。
- 判定：数据卡数字与 manifest 不一致 → **退**（报告 §3 会直接抄这表）。

### V8 · EDA 图

```bash
python - <<'EOF'
from PIL import Image; import pathlib
for p in sorted(pathlib.Path("figures/eda").glob("eda_*.png")):
    im = Image.open(p); dpi = im.info.get("dpi", (0, 0))[0]
    print(f"{p.name:28s} {im.size} dpi={dpi:.0f} size={p.stat().st_size/1024:.0f}KB")
EOF
```

- 期望：**3 张**（`eda_01`/`02`/`03`）；`dpi ≥ 160`；单张 ≥ 50 KB（太小说明是空白/纯色）。
- 人工项（A 自己看）：**图内无中文方框**（本机无中文字体）、坐标轴有单位/类别名、每张图注首句给结论。
- 判定：缺图 → 退（H3）；出现方框 → 退（说明用了中文标签）。

### V9 · 结果图（P7c，S3 之后）

```bash
python - <<'EOF'
from PIL import Image; import pathlib, csv
for p in sorted(pathlib.Path("figures/results").glob("fig[23]_*.png")):
    im = Image.open(p)
    print(f"{p.name:36s} {im.size} dpi={im.info.get('dpi',(0,0))[0]:.0f} {p.stat().st_size/1024:.0f}KB")
# 抽查：Fig.3 的点数 = paper_vs_ours.csv 里 verdict 非空的组合数
rows = [r for r in csv.DictReader(open("results/paper_vs_ours.csv")) if r["paper_value"]]
print("expected_points:", len(rows))
EOF
```

- 期望：2 张图、`dpi ≥ 300`、单张 ≥ 80 KB；`expected_points` 与实际点数一致（人工数一眼或读脚本返回值）。
- 人工项：y=x 参考线在；COIL-20 k=80/160 标了「未复现（D9）」；无中文方框。
- 判定：图中数值与 csv 不一致 → **退**（这是唯一会让「图与数字」互相矛盾的核验）。

## 4. 硬性阈值总表（A 直接对照）

| 项 | 阈值 | 来源 |
|---|---|---|
| `n`（原始） | **pendigits 1797 / coil20 1440**，精确相等（D18：其余 3 个本轮不交付） | 原文 §5 |
| `n`（processed） | 与原始相同：1797 / 1440（本轮无子采样） | 协议 P9 |
| `d` | 64 / 16384，**精确相等**（D18：其余 3 个本轮不交付） | 原文 §5 |
| `X.dtype` / `y.dtype` | `float32` / `int64` | 协议 P1 |
| `array_sha256` | 重放后**完全一致** | V2 |
| `splits.json` md5 | 重跑后一致；train∩test=∅；覆盖全部行 | V3 |
| NaN / inf | 0 / 0 | 协议 P5 |
| `X` 范围 | `[0, 1]`（容差 1e-6） | 协议 P2 |
| 预处理总时长 | ≤ 30 min | V6 |
| 预处理峰值内存 | ≤ 3 GB | V6 |
| EDA 图 | 3 张，dpi ≥ 160，英文 | V8 |

## 5. 拒收条件（任一命中即退回，不逐条商量）

1. 路径越界（V1）；
2. 任一数据集 `array_sha256` 重放不一致（V2）；
3. 任一 `n/d/类数/类计数` 与原文或协议不符且未登记偏离（V5）；
4. 存在 NaN/inf（V5）；
5. `pytest` 非全绿，或靠 `skip` 掩盖缺文件（V3）；
6. train/test 有交集或覆盖不全（V3）；
7. 数据卡数字与 manifest 不一致 / 处理步骤无行号引用（V7）；
8. EDA 图缺失或含中文方框（V8）；
9. 用了 `import` A 的 loader 来"对拍"（违反独立性，V4 会退化为自证）。

**退回话术**（复制粘贴即可）：

> H2 退回（示例格式，本轮适用对象为 `pendigits`/`coil20`）：V2 在 `coil20` 上 MISMATCH（你的 `array_sha256` 与我重放的不同，Δmax = 0.0039）。原因大概率是 PNG 读入后先做了 `astype(float32)` 再 `/255`，而协议 P2 要求先 `/255` 再转 float32（顺序反了会在 float32 舍入上出现末位差异）。请按 `PROTOCOL.md` P2 改，重跑后重新打 `handoff-h2b`。`pendigits` 的 V2 通过，不用重跑。

## 6. 核验记录格式（`docs/HANDOFF_LOG.md`）

| 时点 | tag | 核验人 | 命令 | 结论 | 未解决项 | 日期 |
|---|---|---|---|---|---|---|
| H1 | `handoff-h1` | A | V0/V1 | PASS | shuttle 下载 6 min，可接受 | 2026-11-13 |
| H2 | `handoff-h2` | A | V1–V6 | 见下 | | |

每条记录必须能回答："如果两周后被问'数据到底对不对'，我拿什么证明？"——答案就是这条记录 + 命令输出的粘贴。

## 7. 责任划分与兜底

| 情形 | 处理 | 报告怎么写 |
|---|---|---|
| B 按时交付且全过 | A 合入 `main`，打 tag，H1/H2/H3 记账 | 分工表写 B 负责数据准备 + EDA |
| B 迟到 1 天 | A 用 `src/data.py` 自建 processed 顶上，B 补交后 A 只做"一致性抽检" | 如实写"数据处理由 A/B 共同完成，B 负责 X" |
| B 的 npz 与 A 不一致且查不清 | 以 **A 的实现**为主（主实验跑 A 侧），B 的差异作为敏感性分析（"两套预处理下结论是否变化"） | 写成方法学优点："我们做了双实现对拍，差异 <1e-6" |
| B 完全无法交付 | A 全包；H1–H3 降级为 A 自查 | Team 维度会失分，用"双实现 + 可复现脚本"部分弥补 |

**兜底不是惩罚**：数据错了不退回才是惩罚。退回一次 = 2 小时；错进主表 = 45 个数字重跑 + 报告重写。

## 8. 一页速查（贴在 B 的屏幕上）

```
交付前，我必须能回答：
1. 我的 sha256 是数组哈希，不是文件哈希  → V2 过
2. 我的 splits.json 里 train∩test=∅、覆盖全部行  → V3 过
3. 我的数据卡数字 = manifest 数字，每个处理有行号  → V7 过
4. 我的 npz 在任何机器上重跑都逐位相同  → V2 过
5. 图里没有一个中文字  → V8 过
```
