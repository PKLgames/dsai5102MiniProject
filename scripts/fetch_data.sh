#!/usr/bin/env bash
# 一次性数据准备（幂等）：COIL-20 zip 下载并解包；PenDigits 由 scikit-learn 自带，无需下载。
# 用法：bash scripts/fetch_data.sh
set -euo pipefail
cd "$(dirname "$0")/.."

URL="https://www.cs.columbia.edu/CAVE/databases/SLAM_coil-20_coil-100/coil-20/coil-20-proc.zip"
RAW="data/raw/coil20"
ZIP="$RAW/coil-20-proc.zip"
DIR="$RAW/coil-20-proc"

mkdir -p "$RAW"
if [ -d "$DIR" ] && [ "$(find "$DIR" -name 'obj*__*.png' | wc -l)" -eq 1440 ]; then
  echo "[skip] $DIR 已有 1440 张 PNG"
else
  if [ ! -s "$ZIP" ]; then
    echo "[get ] COIL-20 processed images -> $ZIP"
    curl -fsSL --retry 3 -o "$ZIP" "$URL"
  fi
  echo "[unzip] $ZIP -> $RAW"
  unzip -qo "$ZIP" -d "$RAW"
fi

.venv/bin/python - "$ZIP" "$DIR" <<'PY'
import datetime, hashlib, json, pathlib, sys

zip_path, dir_path = (pathlib.Path(x) for x in sys.argv[1:3])
pngs = sorted(dir_path.glob("obj*__*.png"))
sha = hashlib.sha256(zip_path.read_bytes()).hexdigest() if zip_path.exists() else None
log = {
    "coil20": {
        "url": "https://www.cs.columbia.edu/CAVE/databases/SLAM_coil-20_coil-100/coil-20/coil-20-proc.zip",
        "zip_sha256": sha,
        "n_png": len(pngs),
        "dir": str(dir_path),
        "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    },
    "pendigits": {"source": "sklearn.datasets.load_digits(return_X_y=True)", "n_png": None},
}
pathlib.Path("data/raw/_fetch_log.json").write_text(json.dumps(log, indent=2) + "\n")
print(f"[ok  ] coil20 n_png={len(pngs)} zip_sha256={(sha or '')[:16]}…")
PY
