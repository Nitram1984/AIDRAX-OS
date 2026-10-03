#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

python3 - "$ROOT" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
payload = root / "payload"

errors = []

for path in payload.rglob("*.json"):
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path}: {exc}")

if errors:
    print("VALIDATION: RED")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

print("VALIDATION: GREEN")
PY
