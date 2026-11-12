"""数据契约（A 侧，唯一权威 loader）。

契约（docs/goal/SPEC.md §3 R1–R8）：
    load(name) -> (X: np.ndarray float32 (n, d) C 序, y: np.ndarray int64 (n,))

只读 data/raw/**，不读 data/processed/**（那是 B 的产物，仅用于对拍）。
- pendigits: sklearn.datasets.load_digits()，像素 0..16 → /16.0
- coil20   : data/raw/coil20/coil-20-proc/obj{K}__{NN}.png，uint8 → /255.0，行优先展平
两种都把类别按「首次出现」顺序重编码为 0..K-1。

命令行自检：
    .venv/bin/python -m src.data --sha          # 打印形状 + array_sha256
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
COIL20_DIR = RAW / "coil20" / "coil-20-proc"

DATASETS = ("pendigits", "coil20")
EXPECTED = {"pendigits": (1797, 64), "coil20": (1440, 16384)}

_COIL_RE = re.compile(r"^obj(\d+)__(\d+)\.png$")


# ---------------------------------------------------------------- 工具函数
def encode_by_first_appearance(y: np.ndarray) -> tuple[np.ndarray, dict[int, int]]:
    """把原始标签按「首次出现」的顺序重编码为 0..K-1（SPEC R1）。"""
    y = np.asarray(y)
    classes, first_idx = np.unique(y, return_index=True)
    order = classes[np.argsort(first_idx, kind="stable")]
    mapping = {int(c): i for i, c in enumerate(order)}
    return np.array([mapping[int(v)] for v in y], dtype=np.int64), mapping


def array_sha256(X: np.ndarray, y: np.ndarray) -> str:
    """数组内容哈希（SPEC R7）：float32 C 序字节 + int64 字节。"""
    xb = np.ascontiguousarray(X, dtype=np.float32).tobytes()
    yb = np.ascontiguousarray(y, dtype=np.int64).tobytes()
    return hashlib.sha256(xb + yb).hexdigest()


def _finalize(X: np.ndarray, y_raw: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    X = np.ascontiguousarray(X, dtype=np.float32)  # R1: float32, C 序
    if not np.isfinite(X).all():
        raise ValueError("X 含 NaN/inf（SPEC R5 要求立即失败）")
    y, _ = encode_by_first_appearance(y_raw)
    if X.shape[0] != y.shape[0]:
        raise ValueError(f"X/y 行数不一致: {X.shape[0]} vs {y.shape[0]}")
    return X, y


# ---------------------------------------------------------------- 数据集
def _load_pendigits() -> tuple[np.ndarray, np.ndarray]:
    from sklearn.datasets import load_digits

    d = load_digits()
    X = d.data.astype(np.float32) / 16.0  # R2: 0..16 → [0,1]，不做标准化
    return _finalize(X, d.target)


def _load_coil20() -> tuple[np.ndarray, np.ndarray]:
    from PIL import Image

    if not COIL20_DIR.is_dir():
        raise FileNotFoundError(f"缺少 COIL-20 目录: {COIL20_DIR}")
    files = []
    for p in COIL20_DIR.iterdir():
        m = _COIL_RE.match(p.name)
        if m:
            files.append((int(m.group(1)), int(m.group(2)), p))
    files.sort(key=lambda t: (t[0], t[1]))  # 按 (类号, 序号) 排序 → 行序可复现
    if len(files) != 1440:
        raise ValueError(f"COIL-20 文件数 {len(files)} != 1440")

    n, d = 1440, 16384
    X = np.empty((n, d), dtype=np.float32)
    y_raw = np.empty(n, dtype=np.int64)
    for i, (cls, _, path) in enumerate(files):
        arr = np.asarray(Image.open(path))  # uint8 (128,128)
        if arr.dtype != np.uint8:
            raise ValueError(f"{path.name}: 期望 uint8，得到 {arr.dtype}")
        X[i] = (arr.astype(np.float32) / 255.0).reshape(-1)  # R2/R3
        y_raw[i] = cls
    return _finalize(X, y_raw)


_LOADERS = {"pendigits": _load_pendigits, "coil20": _load_coil20}
_CACHE: dict[str, tuple[np.ndarray, np.ndarray]] = {}


def load(name: str) -> tuple[np.ndarray, np.ndarray]:
    """读原始数据并返回规范数组；同一进程内缓存，调用方不得原地修改返回值。"""
    if name not in _LOADERS:
        raise KeyError(f"未知数据集 {name!r}，可选 {list(_LOADERS)}")
    if name not in _CACHE:
        _CACHE[name] = _LOADERS[name]()
    X, y = _CACHE[name]
    return X, y


def load_fresh(name: str) -> tuple[np.ndarray, np.ndarray]:
    """不走缓存，用于确定性检查。"""
    return _LOADERS[name]()


def label_names(name: str) -> dict[int, str]:
    """编码后的标签 → 原始标签名（写数据卡/图例用）。"""
    if name == "coil20":
        return {i: f"obj{i + 1}" for i in range(20)}
    return {i: str(i) for i in range(10)}


def main() -> None:
    import argparse
    import time

    ap = argparse.ArgumentParser(description="数据契约自检")
    ap.add_argument("--datasets", nargs="+", default=list(DATASETS))
    ap.add_argument("--sha", action="store_true", help="打印 array_sha256（对拍用）")
    args = ap.parse_args()

    for name in args.datasets:
        t0 = time.perf_counter()
        X, y = load_fresh(name)
        dt = time.perf_counter() - t0
        n_exp, d_exp = EXPECTED[name]
        counts = np.bincount(y)
        print(
            f"{name:9s} shape={X.shape} dtype={X.dtype} y={y.dtype} "
            f"classes={len(counts)} counts[{counts.min()},{counts.max()}] "
            f"range=[{X.min():.3f},{X.max():.3f}] load={dt:.2f}s"
        )
        if (X.shape != (n_exp, d_exp)):
            raise SystemExit(f"{name}: 形状 {X.shape} != {(n_exp, d_exp)}")
        if args.sha:
            print(f"{name:9s} array_sha256={array_sha256(X, y)}")


if __name__ == "__main__":
    main()
