"""采样器工厂：把配置字符串解析成 imbalanced-learn 的采样器对象。

约定（与论文 Table 3 的列对齐）：
- `none`           不做任何处理
- `ros`            随机过采样到 1:1
- `rus`            随机降采样到 1:1
- `smote100`       SMOTE，把少数类合成到原数量的 100%（即 200%，与论文 N% 的记法一致：合成 N% 的额外样本）
- `smote{k}`       同上并指定 k 近邻，如 `smote200_k5`
- `borderline`/`adasyn`/`smoteenn`/`smotetomek`  论文后续变体（属于我们的扩展）
"""

from __future__ import annotations

import re

from imblearn.combine import SMOTEENN, SMOTETomek
from imblearn.over_sampling import ADASYN, SMOTE, BorderlineSMOTE, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler

SAMPLER_NAMES = ["none", "ros", "rus", "smote", "borderline", "adasyn", "smoteenn", "smotetomek"]


def _strategy_for_percent(y, percent: float) -> dict:
    """论文的 “N% over-sampling” → imblearn 的 sampling_strategy。

    N% 表示额外合成 N% 的少数类样本，即少数类最终数量 = 原数量 × (1 + N/100)。
    这里用 {少数类标签: 目标数量} 的绝对计数写法，而不是浮点比例：
    浮点比例 >1.0 会被 imblearn 拒绝，而论文确实会在低不平衡比的数据集上
    过采样到超过多数类（如 Pima 的 200%–500% 列），用计数才能忠实复现。
    """
    counts = {v: int((y == v).sum()) for v in set(y)}
    if len(counts) != 2:
        raise ValueError(f"expect binary y, got classes {sorted(counts)}")
    minority = min(counts, key=counts.get)
    target = int(round(counts[minority] * (1.0 + percent / 100.0)))
    return {minority: target}


def build(spec: str, y=None, seed: int = 0):
    """返回 (sampler | None, canonical_spec)。"""
    spec = spec.strip().lower()
    if spec in ("none", "baseline", ""):
        return None, "none"

    m = re.fullmatch(r"(smote|borderline|adasyn)(?:(\d+))?(?:_k(\d+))?", spec)
    if m:
        kind, pct, k = m.group(1), m.group(2), m.group(3)
        pct = float(pct) if pct else 100.0
        k = int(k) if k else 5
        strategy = _strategy_for_percent(y, pct) if y is not None else "auto"
        if kind == "smote":
            return SMOTE(sampling_strategy=strategy, k_neighbors=k, random_state=seed), spec
        if kind == "borderline":
            return BorderlineSMOTE(sampling_strategy=strategy, k_neighbors=k, random_state=seed), spec
        return ADASYN(sampling_strategy=strategy, n_neighbors=k, random_state=seed), spec

    if spec == "smoteenn":
        return SMOTEENN(random_state=seed), spec
    if spec == "smotetomek":
        return SMOTETomek(random_state=seed), spec
    if spec == "ros":
        return RandomOverSampler(random_state=seed), spec
    if m := re.fullmatch(r"rus(\d+)?", spec):
        pct = float(m.group(1)) if m.group(1) else None
        if pct is None or y is None:
            return RandomUnderSampler(random_state=seed), "rus"
        # rus{N}：保留多数类原数量的 N%（不低于少数类数量），对应论文的降采样率扫描
        counts = {v: int((y == v).sum()) for v in set(y)}
        minority = min(counts, key=counts.get)
        majority = max(counts, key=counts.get)
        keep = max(int(round(counts[majority] * pct / 100.0)), counts[minority])
        return RandomUnderSampler(sampling_strategy={majority: keep}, random_state=seed), spec
    raise ValueError(f"unknown sampler spec {spec!r}; examples: none, rus, smote100, smote200_k5, adasyn")
