#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"
python3 - <<'PY'
import json, pathlib
root = pathlib.Path.cwd(); data = json.loads((root / "manifest.json").read_text())
missing = [p for p in data["required_paths"] if not (root / p).is_file()]
if missing: raise SystemExit("Required paths missing: " + ", ".join(missing))
expected = {"registry":"ATLAS","events":"HERMES","lifecycle":"CapabilityRuntime","observability":"ARGUS","orchestration":"AIDRAX"}
if data["authorities"] != expected: raise SystemExit("Desktop authority boundary changed")
print("Manifest and authority boundary: GREEN")
PY
for script in build/*.sh; do test -x "$script"; bash -n "$script"; done
python3 -m compileall -q src tests build/manifest.py
PYTHONPATH=src python3 -m unittest discover -s tests -v
echo "AO-006 verification: GREEN"
