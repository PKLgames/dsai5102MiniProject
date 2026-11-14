# DATA CARD — LU Yuqing (B)

Status: measured on the supplied project snapshot; preparation and audit completed locally.
The processed arrays match A's canonical loader exactly. Existing A result tables have NOT been recomputed with these newly generated stratified folds.

## 1. Dataset identity and sources

| Dataset | Shape | Classes | Class counts | Scaling |
|---|---|---:|---|---|
| pendigits | 1797 × 64 | 10 | 174–183 | /16 |
| coil20 | 1440 × 16384 | 20 | 72–72 | /255 |

PenDigits is the project's name for scikit-learn load_digits(), the 1,797-image, 8×8 representation described in the reproduction target. It must not be substituted with the 10,992-row, 16-feature dataset. COIL-20 uses the official Columbia CAVE processed archive (20 objects; 72 views each; 128×128 grayscale PNGs).

Sources:
- https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html
- https://www.cs.columbia.edu/CAVE/databases/SLAM_coil-20_coil-100/coil-20/coil-20-proc.zip

All counts, ranges, duplicates and labels below were measured. Full numeric details and hashes are in data/manifests/{pendigits,coil20}.json. Source-byte provenance is copied to docs/validation/B/FETCH_PROVENANCE.json; raw files remain outside Git.

## 2. Preprocessing decisions and code trace

| Decision | Rationale | Code location (function start) |
|---|---|---|
| Read bundled digits and numerically sorted COIL PNGs | Stable row order; verify 1440 images of shape 128×128 | src/data_prep.py:12 |
| Cast pixels to float32, then divide digits by 16 and COIL by 255 | Matches A exactly; maps values into [0,1]; no per-feature standardization | src/data_prep.py:33 |
| Encode labels by first appearance and retain original mapping | Preserves explicit relationship between numeric labels and object/digit identities | src/data_prep.py:29 |
| Reject NaN/inf or wrong shapes/ranges | Do not silently impute unexpected data corruption | src/data_prep.py:33 |
| Record duplicate rows, content hashes, provenance and timestamps | No row removal; reproducible content checks | src/data_prep.py:41 |
| Write X/y compressed NPZ and JSON manifests | Convenient replay; compressed NPZ is not memory-mapped | src/data_prep.py:61 |

COIL images are flattened in C (row-major) order. No transpose, feature selection, deduplication, outlier exclusion, augmentation or PCA pre-reduction is applied. Global scaling is recorded as a reproducibility choice; no claim of exact numerical scale invariance is required for this audit.

## 3. Splits and outputs

scripts/make_splits.py uses StratifiedKFold(n_splits=10, shuffle=True, random_state=42) with real labels. The agreed nested schema is {seed, datasets: {name: {n, n_folds, array_sha256, folds}}}. Indices refer to canonical row order. Each test row appears exactly once; train/test are disjoint; every fold covers all observations; fold sizes differ by at most one. The hash binds fold indices to input array order.

- data/processed/{name}.npz: X float32, y int64; generated locally and excluded from Git.
- data/manifests/{name}.json: measured statistics and content hash.
- data/manifests/splits.json: deterministic canonical folds; committed.
- docs/validation/B/VALIDATION.json: independent comparison and fold/figure checks.

## 4. Exploratory figures

| File in figures/eda/ | Measured observation / caption |
|---|---|
| eda_01_class_counts.png | Digits are approximately balanced (174–183 images per digit); COIL-20 has exactly 72 images per object. |
| eda_02_sample_grid.png | Five evenly selected view indices per object illustrate viewpoint variation; one row per object, 20 rows × 5 columns. These are illustrative views, not an independent random sample. |
| eda_03_pixel_hist.png | Global rescaling changes the intensity scale while preserving the displayed pixel-frequency pattern. Both datasets contain many zero-valued pixels. A log y-axis exposes less common intensities. |

All PNGs use English labels and nominal 300 dpi. Pixel histograms include every pixel; no sampling is used. Result figures read supplied A outputs without modifying them. Their captions and status are in report/DSAI5102_07_Report_V3.md.

## 5. Verification

Both datasets: exact equality to A's src.data.load output (max absolute difference = 0; all labels equal). No NaN/inf; no duplicate feature rows; float32/int64; expected shapes and [0,1] range. NPZ arrays match freshly built arrays. Canonical fold JSON is byte-identical on regeneration and equals sklearn's true-label stratified splits. See VALIDATION.json and validation_stdout.txt for environment and measured output. See PYTEST.txt for A's data-contract tests. Full UMAP component tests/model training are not claimed by this data delivery.

## 6. Known issues and interpretation limits

The historical scripts/run_grid.py did not read this nested split schema and fell back to stratification over all-zero labels. Therefore old CSVs cannot be asserted to use these canonical folds. V3 supplies the corrected script and scripts/run_fixed_evaluation.py to back up historical results and recompute evaluation and figures. The corrected full evaluation has not been run as part of this update.

The intended evaluation is transductive: embedding on all unlabelled points, followed by CV on embedding coordinates. It assesses class structure on that dataset, not unseen-sample generalisation. Multiple views of each COIL object are related observations; fold SD is not an independent-run confidence interval. kNN k is bounded by the full training-set size, not per-class counts. UMAP n_neighbors and classifier k are different parameters.
