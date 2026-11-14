# Report-ready text and captions (B delivery)

## Data and preprocessing
We used the 1,797-sample, 64-feature digits dataset distributed with scikit-learn and the official COIL-20 processed archive containing 1,440 grayscale images of 20 objects. COIL images were sorted numerically by object and view index and flattened in row-major order. Pixel arrays were converted to float32 and divided by 16 for digits or 255 for COIL-20; labels were encoded as contiguous int64 values with the original label mapping retained. No per-feature standardization, deduplication, imputation or augmentation was applied. Both processed datasets matched the independent canonical loader exactly, with zero maximum absolute difference and identical labels. Digits contained 174–183 samples per class; COIL-20 contained 72 per class. Neither processed array contained nonfinite values or duplicate feature rows.

## Split statement — only after A integrates and reruns
We generated one set of ten-fold stratified partitions using the true class labels, shuffle=True and random_state=42. All methods used these identical partitions. Each observation appeared in exactly one test fold, and no fold had overlapping training and test indices. Embedding was transductive: labels were used for downstream classifier training and evaluation, not embedding fitting.

Do NOT insert that paragraph as a description of existing CSVs until A confirms the rerun. The current split-file reader fails to consume the nested schema.

## Captions

EDA 1. Digits are approximately balanced (174–183 images per class), whereas COIL-20 is exactly balanced at 72 images per object. Bars show complete dataset counts using original digit/object labels.

EDA 2. Viewpoint changes alter each object's appearance. Rows correspond to the 20 COIL objects; columns show five evenly selected views from each object's ordered sequence. Images are illustrative and are not an evaluation partition.

EDA 3. Global scaling maps both datasets into [0,1] without changing the pixel-frequency pattern shown. Columns display raw and scaled intensities, with pixel fractions on a logarithmic vertical axis; all pixels are included.

Figure 2. The supplied COIL-20 embeddings show object-specific trajectories and some overlapping regions. Left: UMAP (ours); right: t-SNE. Colours consistently identify the same 20 objects in both panels. Coordinates were read from the supplied A snapshot; axes have no direct feature interpretation, and between-panel distances and orientation are not comparable. This is a qualitative display, not a formal cluster-quality test.

Figure 3. Measured accuracies differ from published values by dataset, method and classifier neighbourhood size. Each of the 40 points compares one supplied result with its corresponding published value; the dashed line indicates equality. Marker shape identifies the dataset and colour identifies the method. Coincident points may overlap. No reproduction verdict is encoded because the supplied flags are hard-coded rather than calculated from the protocol. This figure is descriptive pending evaluation/protocol review.

Supplementary Figure 4. kNN accuracy varies with classifier neighbourhood size, particularly on COIL-20. Curves use the supplied mean accuracy; error bars show fold standard deviation, not confidence intervals or variability across independently refitted embeddings. These are supplied-snapshot results and require regeneration after the fold-reader repair.

## Individual contribution — suggested factual wording
LU Yuqing: prepared independent data-processing and provenance scripts; verified processed arrays against the canonical loader; generated and validated label-stratified fold indices; completed the data card; produced three exploratory figures and two required result figures, plus a supplementary accuracy curve; documented integration issues and reproducible verification outputs. AI assistance was used to draft code, documentation and figure-generation workflows; the team should review the outputs and describe actual assistance accurately in its final disclosure.

Do not state that LU ran the original UMAP training or that A has accepted this package until verified. No equal workload percentage is inferred here.
