#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)";cd "$ROOT"
python3 - <<'PY'
import json,pathlib
root=pathlib.Path.cwd();data=json.loads((root/"manifest.json").read_text());missing=[p for p in data["required_paths"] if not (root/p).is_file()]
if missing:raise SystemExit("Required paths missing: "+", ".join(missing))
if data["authorities"]["lifecycle"]!="CapabilityRuntime":raise SystemExit("lifecycle owner changed")
print("Manifest and authority boundary: GREEN")
PY
for script in build/*.sh;do test -x "$script";bash -n "$script";done
python3 -m compileall -q src tests build/manifest.py
PYTHONPATH=src python3 -m unittest discover -s tests -v
echo "AO-004 verification: GREEN"
