"""数据集获取与二分类构造（A 负责的“最小加载器”）。

设计约束：
- 直接对接 OpenML REST API，按 did 取数据并缓存为 CSV 到 data/raw/；
- 不做特征工程（那是 B 的 data_prep.py 的职责），只保证“同一份数据、同一套标签编码”可复现；
- 每个数据集都按论文 Table 2 的样本数做硬校验，数据不对就直接报错。
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

# 论文 Table 2 的数据集（7 个可原样获取）+ 2 个替代 + 1 个外部验证集。
# minority 写 CSV 里的实际标签值；paper=(少数类数, 多数类数)。
DATASETS: dict[str, dict] = {
    # --- 论文原始数据集 ---
    "pima": dict(did=37, target="class", minority="tested_positive", paper=(268, 500)),
    "phoneme": dict(did=1489, target="Class", minority=2, paper=(1586, 3818)),
    "adult": dict(did=179, target="class", minority=">50K", paper=(11687, 37155)),
    # OpenML did=182 与论文版本略有出入（6430 vs 6435 行），见 DEVIATIONS.md D11
    "satimage": dict(did=182, target="class", minority=4, paper=(626, 5809),
                     expected=(625, 5805)),
    # 论文的 Forest Cover = UCI covtype 的 class 3 (35754) vs class 4 (2747)，需先取两类子集
    "covertype": dict(did=150, target="class", keep=(3, 4), minority=4, paper=(2747, 35754)),
    "mammography": dict(did=310, target="class", minority=1, paper=(260, 10923)),
    "oil": dict(did=311, target="class", minority=1, paper=(41, 896)),
    # --- 替代集（E-state / Can 无公开镜像，见 docs/DEVIATIONS.md D3/D4）---
    "qsar-biodeg": dict(did=1494, target="class", minority=None, paper=None),
    "kddcup99": dict(did=1113, target="class", minority=None, paper=None,
                     binarize="kddcup99_attack"),
    # --- 外部验证 ---
    "creditcard": dict(did=1597, target="Class", minority=1, paper=None),
}

# KDDCup99：normal. 为多数类（0），其余攻击类型合并为 1
KDDCUP99_NORMAL = "normal."


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def _openml_description(did: int) -> dict:
    url = f"https://www.openml.org/api/v1/json/data/{did}"
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)["data_set_description"]


def _has_pyarrow() -> bool:
    try:
        import pyarrow  # noqa: F401
    except Exception:
        return False
    return True


def fetch(name: str, force: bool = False) -> Path:
    """下载并缓存为 CSV，返回本地路径。"""
    if name not in DATASETS:
        raise KeyError(f"unknown dataset {name!r}; known: {sorted(DATASETS)}")
    RAW.mkdir(parents=True, exist_ok=True)
    out = RAW / f"{name}.csv"
    if out.exists() and not force:
        return out
    desc = _openml_description(DATASETS[name]["did"])
    # 默认走 ARFF（scipy 直接可读）；仅当 pyarrow 可用且 parquet 链接存在时才用 parquet
    use_parquet = bool(desc.get("parquet_url")) and _has_pyarrow()
    src = desc["parquet_url"] if use_parquet else desc["url"]
    suffix = ".parquet" if use_parquet else ".arff"
    tmp = RAW / f".{name}{suffix}"
    log(f"[{name}] downloading {src}")
    urllib.request.urlretrieve(src, tmp)
    df = pd.read_parquet(tmp) if use_parquet else _read_arff(tmp)
    df.to_csv(out, index=False)
    tmp.unlink(missing_ok=True)
    return out


def _read_arff(path: Path) -> pd.DataFrame:
    from scipy.io import arff

    data, _meta = arff.loadarff(str(path))
    df = pd.DataFrame(data)
    for c in df.columns:  # arff 的字符串列是 bytes
        if df[c].dtype == object:
            df[c] = df[c].map(lambda v: v.decode() if isinstance(v, bytes) else v)
    return df


def load(name: str) -> tuple[pd.DataFrame, np.ndarray]:
    """返回 (X, y)，y ∈ {0,1}，1 = 少数类。"""
    cfg = DATASETS[name]
    df = pd.read_csv(fetch(name))
    target = cfg["target"]
    if target not in df.columns:  # OpenML 的 target 列名偶尔大小写不同
        cand = [c for c in df.columns if c.lower() == target.lower()]
        if not cand:
            raise KeyError(f"{name}: target {target!r} not in {list(df.columns)[:8]}…")
        target = cand[0]

    keep = cfg.get("keep")
    if keep:
        mask = df[target].map(lambda v: any(_same_label(v, k) for k in keep))
        df = df[mask].reset_index(drop=True)

    if cfg.get("binarize") == "kddcup99_attack":
        y = (df[target].astype(str).str.strip() != KDDCUP99_NORMAL).astype(int).to_numpy()
    else:
        m = cfg["minority"]
        if m is None:  # 取样本数最少的类为少数类
            m = df[target].value_counts().index[-1]
        y = df[target].map(lambda v: _same_label(v, m)).astype(int).to_numpy()

    X = _encode(df.drop(columns=[target]))
    _check_counts(name, cfg, y)
    return X, y


def _same_label(a, b) -> bool:
    """同一标签在 CSV/ARFF 里可能是 '4' / '4.0' / b'4'，统一比较。"""
    a = a.decode() if isinstance(a, bytes) else a
    b = b.decode() if isinstance(b, bytes) else b
    sa, sb = str(a).strip(), str(b).strip()
    if sa == sb:
        return True
    try:
        return float(sa) == float(sb)
    except (TypeError, ValueError):
        return False


def _check_counts(name: str, cfg: dict, y: np.ndarray) -> None:
    """与论文 Table 2 的样本数对齐校验，避免“跑完才发现数据错了”。"""
    paper = cfg.get("paper")
    if not paper:
        return
    expected = tuple(cfg.get("expected") or paper)
    n1, n0 = int(y.sum()), int((1 - y).sum())
    if (n1, n0) != expected:
        raise ValueError(
            f"{name}: counts {n1}/{n0} != paper {paper[0]}/{paper[1]} "
            f"(IR {n0 / max(n1, 1):.2f} vs {expected[1] / expected[0]:.2f})")
    if (n1, n0) != tuple(paper):
        log(f"[{name}] WAIT: paper {paper[0]}/{paper[1]} vs loaded {n1}/{n0} (documented in DEVIATIONS)")
    else:
        log(f"[{name}] counts match paper: minority={n1} majority={n0}")


def _encode(X: pd.DataFrame) -> pd.DataFrame:
    """最小可复现的编码：数值列中位数填充，类别列 one-hot（B 可替换为更细的策略）。"""
    num = X.select_dtypes(include=[np.number])
    cat = X.select_dtypes(exclude=[np.number])
    parts = []
    if not num.empty:
        parts.append(num.fillna(num.median(numeric_only=True)))
    if not cat.empty:
        cat = cat.astype(str).fillna("NA")
        parts.append(pd.get_dummies(cat, dummy_na=False, dtype=float))
    out = pd.concat(parts, axis=1)
    return out.astype(float).reset_index(drop=True)


def describe(name: str) -> dict:
    X, y = load(name)
    n1, n0 = int(y.sum()), int((1 - y).sum())
    return dict(name=name, n=len(y), minority=n1, majority=n0,
                ir=round(n0 / max(n1, 1), 2), n_features=X.shape[1])
