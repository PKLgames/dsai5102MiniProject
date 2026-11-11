# B 交付标准（A 的核验口径）

> 三条原则：① **命令即证据**（只认命令输出，不认文字描述）；② **核验独立于 B 的脚本**（A 用自己的 `src/data.py` 读同一批 raw）；③ **宁可退回**（数据错一格，主表全废；退回 2 小时，返工 2 天）。
> 交接只走 git：push 分支 → `git tag s2` / `s4` → 在 `docs/log/HANDOFF_LOG.md` 记一行。**不允许聊天发文件。**

## 1. 交接包（S2）

| # | 路径 | 必备内容 | 检查 |
|---|---|---|---|
| 1 | `scripts/fetch_data.py` | `--datasets`、幂等、`data/raw/_fetch_log.json`（url/sha256/bytes/UTC） | 源可追溯 |
| 2 | `src/data_prep.py` | `DATASETS`、`PAPER_COUNTS`、`load_raw()`、`build()`、CLI（`--out`、`--force`、`--emit-card-table`） | 路径边界 / 哈希重放 |
| 3 | `data/processed/{pendigits,coil20}.npz` | 键 `X` float32、`y` int64；**不入 git**，由脚本重放 | 哈希重放 |
| 4 | `data/manifests/{pendigits,coil20}.json` | §1 的全部键 | 哈希重放 / 完整性 |
| 5 | `data/manifests/splits.json` + `scripts/make_splits.py` | 10 折、行号、`sort_keys+indent=1` | 划分不变量 |
| 6 | `docs/goal/DATA_CARD.md` | 六节；数字来自 manifest；步骤带 `data_prep.py:行号` | 数据卡可追溯 |
| 7 | `figures/eda/eda_01..03.png` | 3 张、英文、dpi ≥160 | EDA 图 |
| 8 | `docs/log/HANDOFF_LOG.md` 一行 | 时间、tag、自证清单、未解决项 | 人工 |
| 9 | `figures/results/fig2_*.png`、`fig3_*.png`（**S4**） | 2 张、300 dpi；点数与 csv 一致 | 结果图 |

## 2. 检查项（每项：命令 → 期望 → 不过怎么办）

### 源可追溯
```bash
python -c "import json;log=json.load(open('data/raw/_fetch_log.json'));[print(k,v['bytes'],v['sha256'][:12],v['url']) for k,v in log.items()]"
```
期望 2 个 key（`pendigits`、`coil20`），sha 非空、bytes>0。缺 key 或 sha 空 → **退**（无法证明用的是哪个版本）。

### 路径边界
```bash
git fetch origin data-prep --tags && git diff --name-only main...data-prep
```
期望只出现：`scripts/fetch_data.py`、`src/data_prep.py`、`scripts/make_splits.py`、`scripts/make_figures.py`、`data/manifests/**`、`docs/goal/DATA_CARD.md`、`figures/**`。
出现 `src/data.py`、`src/umap_impl/**`、`results/**`、`configs/**`、`docs/goal/SPEC.md` → **退**（越界）。

### 哈希重放（最关键）
```bash
rm -rf /tmp/replay && python src/data_prep.py --datasets all --out /tmp/replay
python -c "
import json,hashlib,numpy as np,pathlib
for mf in sorted(pathlib.Path('/tmp/replay').glob('*.json')):
    m=json.load(open(mf)); z=np.load(f'/tmp/replay/{m[\"dataset\"]}.npz')
    h=hashlib.sha256(np.ascontiguousarray(z['X'],np.float32).tobytes()+np.ascontiguousarray(z['y'],np.int64).tobytes()).hexdigest()
    ref=json.load(open(f'data/manifests/{m[\"dataset\"]}.json'))['array_sha256']
    print(m['dataset'], m['n'], m['n_features'], 'OK' if h==ref else 'MISMATCH')
"
```
期望两行 `OK`。任一 MISMATCH → **退**（说明产物依赖随机性/路径顺序/网络）。
比的是**数组哈希**，不是 npz 文件哈希（zip 头含时间戳，文件哈希必变）。

### 契约与划分不变量
```bash
python -m pytest -q tests/
python -c "
import json,numpy as np
sp=json.load(open('data/manifests/splits.json'))
for name,d in sp['datasets'].items():
    n=d['n']; seen=np.zeros(n,int)
    for f in d['folds']:
        tr,te=np.array(f['train']),np.array(f['test'])
        assert len(np.intersect1d(tr,te))==0 and len(np.union1d(tr,te))==n
        seen[te]+=1
    assert seen.max()-seen.min()<=1
    print(name,d['n'],len(d['folds']),'ok')
"
```
期望 pytest 全绿（≥6 用例）、折数 10/10。有 fail 或靠 skip 掩盖缺文件 → **退**；train/test 有交集 → **退**。

### 双实现对拍
```bash
python -c "
import numpy as np
from src.data import load
for n in ('pendigits','coil20'):
    Xa,ya=load(n); z=np.load(f'data/processed/{n}.npz')
    Xb,yb=z['X'],z['y']
    print(n, Xa.shape==Xb.shape, 'max|dX|=%.1e'%float(np.abs(Xa-Xb).max()), 'y_equal=',bool(np.array_equal(ya,yb)))
"
```
期望 `max|dX|=0.0e+00`、`y_equal=True`。`0<d≤1e-6` 允许但必须查清（常见：`/255` 与 `astype` 顺序）并开 D 条目；`d>1e-6` 或标签不等 → **退**。

### 完整性
```bash
python -c "
import json,numpy as np
for n in ('pendigits','coil20'):
    z=np.load(f'data/processed/{n}.npz'); X,y=z['X'],z['y']; m=json.load(open(f'data/manifests/{n}.json'))
    cc={int(k):int(v) for k,v in m['class_counts'].items()}
    assert int(np.isnan(X).sum()+np.isinf(X).sum())==m['nan']+m['inf']==0
    assert np.array_equal(np.bincount(y),[cc[i] for i in range(len(cc))])
    assert 0<=X.min() and X.max()<=1+1e-6 and len(m['label_map'])==m['n_classes']
    print(n,len(y),m['n_classes'],min(cc.values()),round(float(X.max()),3))
"
```
期望两行都过、`min_class` 与数据卡一致、`max≤1+1e-6`。NaN/inf → **退**。

### 资源上限
```bash
/usr/bin/time -v python src/data_prep.py --datasets all --out /tmp/replay_time 2>&1 | grep -E "Elapsed|Maximum resident"
```
期望 ≤30 min、峰值 ≤3 GB（本机 7.5 GB，留 4 GB 给训练）。超限 → 退，改分块/拆段。

### 数据卡可追溯
```bash
python src/data_prep.py --emit-card-table > /tmp/card.md
diff <(sed -n '/^| 名称/,/^$/p' docs/goal/DATA_CARD.md) /tmp/card.md || echo DRIFT
grep -o "data_prep\.py:[0-9]*" docs/goal/DATA_CARD.md | sort -u
```
期望无 `DRIFT`；每个行号 ≤ `wc -l src/data_prep.py`。数字不一致 → **退**（报告 §3 直接抄这表）。

### EDA 图 / 结果图
```bash
python -c "
from PIL import Image; import pathlib
for p in sorted(pathlib.Path('figures').rglob('fig*.png')):
    im=Image.open(p); print(p, im.size, round(im.info.get('dpi',(0,0))[0]), round(p.stat().st_size/1024),'KB')
"
```
期望 EDA 3 张（dpi≥160）、结果图 2 张（dpi≥300、单张≥80 KB）。缺图 → 退；人工看一眼**无中文方框**、每图注首句给结论。
结果图另需：点数 = `paper_vs_ours.csv` 中 `paper_acc` 非空行数；COIL-20 大 k 标「未复现（D9）」。

## 3. 硬阈值总表

| 项 | 阈值 |
|---|---|
| `n` | PenDigits **1797**、COIL-20 **1440**，精确相等 |
| `d` | 64 / 16384，精确相等 |
| dtype | `float32` / `int64` |
| `array_sha256` | 重放后完全一致 |
| splits | 10 折、无交集、全覆盖、折大小差 ≤1、重跑 md5 相同 |
| NaN / inf | 0 / 0 |
| `X` 范围 | [0, 1]（容差 1e-6） |
| 预处理 | ≤30 min、峰值 ≤3 GB |
| EDA / 结果图 | 3 张 dpi≥160 / 2 张 dpi≥300 |

## 4. 拒收条件（任一命中即退，不商量）

1. 路径越界；2. `array_sha256` 重放不一致；3. `n/d/类计数` 不符且无 D 条目；4. NaN/inf；5. pytest 非全绿或 skip 掩盖；6. 折有交集/覆盖不全；7. 数据卡与 manifest 不一致或无行号；8. 图缺失/含中文；9. 用 A 的 loader「对拍」（自证）。

**退回话术模板**：
> S2 退回：哈希重放在 `coil20` 上 MISMATCH（你的 sha 与我重放不同，`max|dX|=0.0039`）。大概率是 PNG 读入后先 `astype(float32)` 再 `/255`，协议 P2 要求先 `/255` 再转 float32（顺序反了会在 float32 末位产生差异）。改完重跑、重新打 `s2` 并把输出贴进 `HANDOFF_LOG.md`。`pendigits` 已通过，不用重跑。

## 5. 记录与兜底

- `docs/log/HANDOFF_LOG.md` 每条：`时间 | tag | 核验人 | 跑了哪些检查 | 结论 | 未解决项`。
- B 迟到：A 用 `src/data.py` 自建 processed 顶上，B 补交后只做一致性抽检；报告如实写分工。
- B 与 A 不一致且查不清：以 **A 的 canonical** 为主，B 的差异写成敏感性分析（这反而是方法学加分项）。
