#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

python3 - "$ROOT" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1]) / "payload"

json_files = list(root.rglob("*.json"))

if not json_files:
    raise SystemExit("RED: no JSON files found")

for path in json_files:
    json.loads(path.read_text(encoding="utf-8"))

print("VALIDATION: GREEN")
print("JSON files:", len(json_files))
PY
