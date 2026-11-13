#!/usr/bin/env bash
# 端到端复现：数据校验 → 主表(400 行) → 运行时间 → 数字终版 → 查重 → 结果图（若有）
# 用法：  bash scripts/repro.sh            # 从仓库根目录
#        NUMBA_NUM_THREADS=1 bash scripts/repro.sh
set -euo pipefail
cd "$(dirname "$0")/.."
export NUMBA_NUM_THREADS="${NUMBA_NUM_THREADS:-1}"
PY="${PY:-.venv/bin/python}"

echo "== 0. 一次性数据准备（幂等） =="
bash scripts/fetch_data.sh

echo "== 1. 数据契约自检（array_sha256 两次一致） =="
$PY - <<'PY'
from src.data import load_fresh, array_sha256
for name in ("pendigits", "coil20"):
    h1 = array_sha256(*load_fresh(name)); h2 = array_sha256(*load_fresh(name))
    assert h1 == h2, f"{name}: 两次读取哈希不一致"
    print(f"   {name}: {h1[:16]}…  ok")
PY

echo "== 2. 主表：2 数据集 × 10 折 × 4 方法 × 5 个 k = 400 行 =="
$PY scripts/run_grid.py --recompute

echo "== 3. 运行时间基准（3 次中位数） =="
$PY scripts/run_runtime.py

echo "== 4. 数字终版（results/README_numbers.md + numbers.json） =="
$PY scripts/fill_numbers.py

echo "== 5. 原创性自查（8-gram 重合率 <5%） =="
if ls report/*.md >/dev/null 2>&1; then
  $PY scripts/similarity_check.py report/*.md || true
else
  echo "   （report/ 下暂无 md，跳过）"
fi

echo "== 6. 结果图（成员 B 交付；脚本存在才跑） =="
if [ -f scripts/make_figures.py ]; then
  $PY scripts/make_figures.py
else
  echo "   （scripts/make_figures.py 尚未提交，跳过 Fig.2/Fig.3）"
fi

echo "== done =="
