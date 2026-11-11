"""1-hour smoke test for the UMAP reproduction (UMAP paper, arXiv:1802.03426).

Purpose (see for_next_round.md step 3): on ONE small dataset, check that the
published protocol (embed -> kNN classifier in embedding space, stratified
10-fold CV) reproduces the published direction (UMAP ~ t-SNE > PCA), and
measure the wall-clock cost of one configuration.

This smoke uses the *reference* implementation (umap-learn) on purpose: it
validates data access + protocol + runtime, not our reimplementation.

Run:  .venv/bin/python -u scripts/smoke_umap.py digits
      .venv/bin/python -u scripts/smoke_umap.py coil20
"""
import sys
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
import umap

ROOT = Path(__file__).resolve().parents[1]
K_SMALL = [10, 20, 40, 80, 160]
SEED = 42


def load_coil20():
    d = ROOT / "data" / "raw" / "coil20" / "coil-20-proc"
    files = sorted(d.glob("obj*__*.png"))
    if len(files) != 1440:
        raise RuntimeError(f"expected 1440 COIL-20 images, found {len(files)}")
    X = np.stack([np.asarray(Image.open(f), dtype=np.float64).ravel() for f in files])
    y = np.array([int(f.name.split("__")[0][3:]) for f in files])
    return X, y, [f.name for f in files]


def load_dataset(name):
    if name == "digits":
        d = load_digits()
        return d.data.astype(np.float64), d.target, "PenDigits (sklearn load_digits)"
    if name == "coil20":
        X, y, _ = load_coil20()
        return X, y, "COIL-20 (Columbia SLAM, 1440x16384)"
    raise SystemExit(f"unknown dataset {name}")


def embed(name, X):
    out = {}
    t0 = time.time()
    out["PCA"] = PCA(n_components=2, random_state=SEED).fit_transform(X)
    out["_time_PCA"] = time.time() - t0

    t0 = time.time()
    out["t-SNE"] = TSNE(
        n_components=2, perplexity=30, init="pca", learning_rate="auto",
        max_iter=1000, random_state=SEED, n_jobs=1,
    ).fit_transform(X)
    out["_time_t-SNE"] = time.time() - t0

    t0 = time.time()
    out["UMAP"] = umap.UMAP(
        n_components=2, n_neighbors=15, min_dist=0.1, random_state=SEED,
        n_jobs=1, verbose=False,
    ).fit_transform(X)
    out["_time_UMAP"] = time.time() - t0
    return out


def knn_accuracy(E, y):
    skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=SEED)
    res = {}
    for k in K_SMALL:
        accs = []
        for tr, te in skf.split(E, y):
            clf = KNeighborsClassifier(n_neighbors=k, n_jobs=1)
            clf.fit(E[tr], y[tr])
            accs.append(clf.score(E[te], y[te]))
        res[k] = (float(np.mean(accs)), float(np.std(accs)))
    return res


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "digits"
    X, y, desc = load_dataset(name)
    print(f"[data] {desc}  X={X.shape}  classes={len(np.unique(y))}", flush=True)

    embs = embed(name, X)
    print("[time] " + "  ".join(
        f"{m}={embs[f'_time_{m}']:.1f}s" for m in ("PCA", "t-SNE", "UMAP")), flush=True)

    results = {"dataset": name, "desc": desc, "shape": list(X.shape), "k": K_SMALL,
               "times": {m: embs[f"_time_{m}"] for m in ("PCA", "t-SNE", "UMAP")}}
    for m in ("PCA", "t-SNE", "UMAP"):
        results[m] = {str(k): v for k, v in knn_accuracy(embs[m], y).items()}

    print(f"{'k':>4} " + " ".join(f"{m:>16}" for m in ("PCA", "t-SNE", "UMAP")))
    for k in K_SMALL:
        row = " ".join(f"{results[m][str(k)][0]:.3f}±{results[m][str(k)][1]:.3f}" for m in ("PCA", "t-SNE", "UMAP"))
        print(f"{k:>4} {row}")

    out = ROOT / "results" / "smoke_umap"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.json").write_text(json.dumps(results, indent=2))
    print(f"[saved] {out / f'{name}.json'}")


if __name__ == "__main__":
    main()
