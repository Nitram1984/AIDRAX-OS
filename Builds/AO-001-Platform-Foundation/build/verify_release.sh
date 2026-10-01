#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python3 - <<'PY'
import json
import pathlib
root = pathlib.Path.cwd()
manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
missing = [path for path in manifest["required_paths"] if not (root / path).is_file()]
if missing: raise SystemExit("Required paths missing: " + ", ".join(missing))
if manifest["authorities"]["registry"] != "ATLAS": raise SystemExit("ATLAS must remain the registry authority")
print("Manifest and required layout: GREEN")
PY
for script in build/*.sh; do test -x "$script" || { echo "Not executable: $script" >&2; exit 1; }; bash -n "$script"; done
python3 -m compileall -q src tests build/manifest.py
PYTHONPATH=src python3 -m unittest discover -s tests -v
echo "AO-001 verification: GREEN"
