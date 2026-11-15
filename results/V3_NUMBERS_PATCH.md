# V3 报告数值替换补丁（A 生成，2026-11-15）

来源：`results/grid_knn_summary.csv`（按 `data/manifests/splits.json` 的验证分层划分重算，2026-11-15）。

用法：把下面各表整表替换 V3 的对应表；句子级替换见每节末尾。

### 表 2a（PenDigits）
| Method | k=10 | k=20 | k=40 | k=80 | k=160 |
| --- | --- | --- | --- | --- | --- |
| PCA | 0.649 ± 0.030 | 0.641 ± 0.037 | 0.646 ± 0.036 | 0.652 ± 0.031 | 0.640 ± 0.032 |
| t-SNE | 0.987 ± 0.010 | 0.977 ± 0.011 | 0.965 ± 0.016 | 0.950 ± 0.013 | 0.951 ± 0.014 |
| UMAP (reference) | 0.988 ± 0.009 | 0.977 ± 0.012 | 0.968 ± 0.012 | 0.951 ± 0.014 | 0.921 ± 0.015 |
| UMAP (ours) | 0.988 ± 0.010 | 0.984 ± 0.013 | 0.971 ± 0.015 | 0.956 ± 0.014 | 0.954 ± 0.014 |
### 表 2b（COIL-20）
| Method | k=10 | k=20 | k=40 | k=80 | k=160 |
| --- | --- | --- | --- | --- | --- |
| PCA | 0.723 ± 0.042 | 0.705 ± 0.042 | 0.647 ± 0.038 | 0.549 ± 0.033 | 0.394 ± 0.040 |
| t-SNE | 0.965 ± 0.016 | 0.912 ± 0.022 | 0.869 ± 0.016 | 0.783 ± 0.016 | 0.653 ± 0.021 |
| UMAP (reference) | 0.858 ± 0.010 | 0.858 ± 0.010 | 0.856 ± 0.018 | 0.815 ± 0.011 | 0.570 ± 0.033 |
| UMAP (ours) | 0.857 ± 0.014 | 0.849 ± 0.022 | 0.849 ± 0.014 | 0.817 ± 0.012 | 0.578 ± 0.037 |

### 表 3（实际值、Δ 与容差判定，UMAP-ours vs 原文）

| Dataset | k | Paper | Ours | Δ | 幅度容差 | 方向（vs t-SNE）| 单元判定 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pendigits | 10 | 0.973 ± 0.044 | 0.988 ± 0.010 | +0.015 | ✓ | 0.988 ≥ 0.987 −0.03 → 过 | 复现 |
| pendigits | 20 | 0.976 ± 0.035 | 0.984 ± 0.013 | +0.008 | ✓ | 0.984 ≥ 0.977 −0.03 → 过 | 复现 |
| pendigits | 40 | 0.954 ± 0.060 | 0.971 ± 0.015 | +0.017 | ✓ | 0.971 ≥ 0.965 −0.03 → 过 | 复现 |
| pendigits | 80 | 0.951 ± 0.072 | 0.956 ± 0.014 | +0.005 | ✓ | 0.956 ≥ 0.950 → 过 | 复现 |
| pendigits | 160 | 0.951 ± 0.085 | 0.954 ± 0.014 | +0.003 | ✓ | 0.954 ≥ 0.951 → 过 | 复现 |
| coil20 | 10 | 0.921 ± 0.075 | 0.857 ± 0.014 | -0.064 | ✓ | 0.857 < 0.965 −0.03 → 不过 | 未复现 |
| coil20 | 20 | 0.907 ± 0.064 | 0.849 ± 0.022 | -0.058 | ✓ | 0.849 < 0.912 −0.03 → 不过 | 未复现 |
| coil20 | 40 | 0.904 ± 0.056 | 0.849 ± 0.014 | -0.055 | ✓ | 0.849 ≥ 0.869 −0.03 → 过 | 复现 |
| coil20 | 80 | 0.899 ± 0.058 | 0.817 ± 0.012 | -0.082 | ✓ | 0.817 ≥ 0.783 → 过 | 复现 |
| coil20 | 160 | 0.803 ± 0.138 | 0.578 ± 0.037 | -0.225 | ✗ | 0.578 < 0.653 → 不过 | 未复现 |

数据集级判定：PenDigits = **复现**（5/5 单元过；方向 5/5；排序 73%）；COIL-20 = **未复现**（k=10/20/160 方向不过；排序 60%）。

### 句子级替换

1. 首页 Version 行 → `Version: V3. Numerical tables and figures use the validated stratified 10-fold splits recomputed on 2026-11-15.`
2. Abstract 末两句 → 删掉 "A code audit identified a fold-file loading defect, so these numerical findings remain provisional until evaluation is rerun using the validated stratified partitions."，改为 `The evaluation was rerun after the fold-file defect was repaired; all numbers below come from the validated stratified partitions.`
3. §4 开头 "Evaluation status." 整段 → `All numbers below were recomputed after the fold-file defect was repaired: scripts/run_grid.py now reads data/manifests/splits.json, checks the array hash and per-fold index validity, and verifies the folds equal the agreed true-label stratified 10-fold partition. results/evaluation_protocol.json records the protocol hash used for the run.`
4. §4 COIL-20 段数值 → `At k = 10, UMAP-ours gives 0.857 ± 0.014, below t-SNE's 0.965 ± 0.016; the gap persists at k = 20 (0.849 ± 0.022 vs 0.912 ± 0.022). At k = 40 and k = 80 UMAP-ours is within 0.03 of t-SNE (0.849 ± 0.014 vs 0.869 ± 0.016; 0.817 ± 0.012 vs 0.783 ± 0.016) and at k = 160 it drops to 0.578 ± 0.037 against t-SNE's 0.653 ± 0.021.`
5. §4 "All comparative conclusions remain provisional..." → `All numbers above come from the validated stratified partitions; the dataset-level verdict is reproduced for PenDigits and not reproduced for COIL-20.`
6. Figure 4 caption 末句 `... remain provisional pending evaluation with the corrected fold reader.` → 删除。
7. Table 3 注 `... because the existing verifiable flags are hard-coded rather than computed from the full protocol.` → `... because the flags now record numerical comparability only, not a success verdict.`

