#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 -m unittest discover -s "$root/tests" -v
python3 - "$root" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
manifest = json.loads((root / "manifest.json").read_text())
missing = [item for item in manifest["required_paths"] if not (root / item).is_file()]
if missing:
    raise SystemExit("manifest paths missing: " + ", ".join(missing))
print("AO-024_MANIFEST_GREEN")
PY
