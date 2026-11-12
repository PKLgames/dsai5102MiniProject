# A 交付标准（自己验自己，发出前必过）

> 两条门：**S1**（Day1 10:00，契约+模板）与 **S3**（Day2 22:00，数字）。每条都能用命令验，验不过不发。

## S1 · 契约与模板

```bash
cd /home/pklgames/coding/dsai5102MiniProject && source .venv/bin/activate
python -m pytest -q tests/                                   # 期望：全绿，≥6 用例
python -c "from src.data import load; X,y=load('coil20'); X2,y2=load('coil20'); import numpy as np,hashlib; \
h=lambda A,b: hashlib.sha256(np.ascontiguousarray(A,np.float32).tobytes()+np.ascontiguousarray(b,np.int64).tobytes()).hexdigest(); \
print(X.shape, X.dtype, y.dtype, h(X,y)==h(X2,y2))"          # 期望：(1440, 16384) float32 int64 True
```

- [ ] `load()` 签名与返回 dtype/形状符合 SPEC §3；PenDigits `(1797,64)`、COIL-20 `(1440,16384)`
- [ ] 两次调用 `array_sha256` 相同（确定性）
- [ ] 不读 `data/processed/*`、不 import B 的 `data_prep`
- [ ] `results/README_numbers.md` 模板已就位：8 行（2 数据集 × 4 方法）× 5 个 k 全为 `{{...}}` 占位符，并附键名清单
- [ ] `git tag s1`，并在 `docs/log/HANDOFF_LOG.md` 记一行（时间、commit、产物）

## S3 · 数字

```bash
python scripts/run_grid.py --datasets pendigits coil20 --methods pca tsne umap_ref umap_ours
python scripts/run_grid.py --datasets pendigits coil20 --methods pca tsne umap_ref umap_ours --resume  # 第二次应 0 重算
python -c "import pandas as pd; d=pd.read_csv('results/grid_knn.csv'); print('rows',len(d)); print(d.groupby(['dataset','method']).size().to_string()); print('nan',d.acc.isna().sum(),'range',round(d.acc.min(),3),round(d.acc.max(),3))"
python scripts/run_runtime.py --datasets pendigits coil20 --repeats 3
```

- [ ] `grid_knn.csv` = **400 行**且无重复键（dataset,fold,method,k）
- [ ] **重跑逐折差 = 0**（或 `max|diff| ≤ 1e-9`；超出必须在 DEVIATIONS 开条目）
- [ ] `runtime.csv` 4 行、含 `median/min/max/timeout` 列；无 30 min 超时（有则记录）
- [ ] `paper_vs_ours.csv` 的 `paper_acc` 与 `docs/goal/PAPER_DATA.md` 逐格一致（抽查 5 格）
- [ ] `README_numbers.md` 里的 `{{...}}` 键全部能在 `results/numbers.json` 找到（机读替换表）、每个数字带 csv 行号、判定词齐全；被 C 拿走后能独立写出 §4
- [ ] `results/embeddings/coil20_{umapours,tsne}.npz` 键为 `E`(float32)/`y`(int64)，形状 `(1440,2)`/`(1440,)`
- [ ] `git tag s3` + `HANDOFF_LOG.md` 一行

## 判定自检（发出前 5 分钟）

| 问题 | 答案必须能从文件里指出来 |
|---|---|
| C2 是复现/部分复现/未复现？ | `README_numbers.md` 的判定行 + `paper_vs_ours.csv` |
| 差多少？ | `delta` 列；COIL-20 大 k 是否 `verifiable=false` |
| 为什么 COIL-20 偏低？ | `docs/log/DEVIATIONS.md` D9 的归因段落 |
| 自研是否可信？ | P3/P4 的对拍输出（ρ/σ 误差、余弦、kNN 差） |
