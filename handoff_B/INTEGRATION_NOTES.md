# Integration notes for A and C

## A — required before final numeric submission
1. Apply/review A_REVIEW_split_reader.patch from the repository root (`git apply --check handoff_B/A_REVIEW_split_reader.patch`, then `git apply ...`). This patch is NOT applied to your scripts in this delivery. It reads the nested datasets schema, validates array hashes and fails rather than silently making non-stratified partitions.
2. Keep the old result snapshot for traceability. Recompute classification results after fixing the reader; the new partitions differ from the fallback. Rebuild summaries, paper comparisons and report numbers, then run B's make_figures.py again. B has not refitted UMAP or changed your CSVs.
3. Do not use `verifiable` as an automatic reproduced/not-reproduced flag: current code hard-codes all COIL k>=80 false, including baselines. Compute numerical gaps, direction and ranking separately under the declared protocol. k=80 ours 0.808333 vs paper 0.899 differs by 0.090667 (<0.10), and exceeds current t-SNE 0.774305. k=10 COIL UMAP is below t-SNE despite the true flag.
4. Keep UMAP n_neighbors distinct from classifier k. kNN k is constrained by total training sample count, not class-specific count.
5. Review partial-resume logic in run_grid.py: the todo_k check may skip an incompletely populated method when early folds exist. Use an explicit full --recompute after backing up results.

## C — writing corrections
- Dataset table: only the two delivered datasets in the main table; digits class range 174–183. Unexecuted datasets may be mentioned as limitations.
- Figure 2 compares UMAP-ours with t-SNE, not two UMAP variants. Use supplied neutral captions rather than asserting untested conclusions.
- Do not say both UMAP codes beat t-SNE at digits k=160: supplied ref 0.920984 < t-SNE 0.951031.
- COIL k=80 absolute gap does not exceed 0.10. Differentiate numeric agreement from preservation of a comparative claim.
- The supplied deviation appendix renumbers D1–D18 relative to the deviation log; reconcile IDs.
- Treat initialization/repulsion/high dimensionality as candidate explanations unless supported by controlled experiments. Similar classifier scores do not prove equal embeddings.
- Correct 2024 DOI to 10.1038/s43586-024-00363-x; identify the actual 2020 v3 version used for the original arXiv work first posted in 2018.
- Internal 8-gram threshold is not a course requirement or proof of integrity; no preregistration claim beyond available dated evidence.
- Final AI disclosure must include actual code/figure/document assistance, not only language polishing if broader assistance was used.

## Delivery boundary
B files are completed and independently checked. Model CSVs and embeddings are unchanged from the supplied ZIP; main-result scientific conclusions remain provisional until A's review. No upload, Git commit, push, acceptance tag or submission has been performed on anyone's behalf.
