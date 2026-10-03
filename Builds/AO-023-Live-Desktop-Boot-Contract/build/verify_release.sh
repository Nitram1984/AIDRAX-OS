#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$root"
python3 - <<'PY'
import json,pathlib
root=pathlib.Path.cwd(); manifest=json.loads((root/'manifest.json').read_text())
missing=[p for p in manifest['required_paths'] if not (root/p).is_file()]
if missing: raise SystemExit('missing: '+', '.join(missing))
PY
PYTHONPATH=src python3 -m unittest discover -s tests -v
