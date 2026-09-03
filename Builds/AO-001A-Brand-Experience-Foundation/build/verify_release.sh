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
if missing:
    raise SystemExit("Required paths missing: " + ", ".join(missing))
expected = {"registry": "ATLAS", "event_bus": "HERMES", "lifecycle": "CapabilityRuntime", "observability": "ARGUS", "orchestration": "AIDRAX"}
if manifest["authorities"] != expected:
    raise SystemExit("AO-001A authority boundary changed")
catalog = json.loads((root / "config/brand-catalog.json").read_text(encoding="utf-8"))
experience = json.loads((root / "config/experience-map.json").read_text(encoding="utf-8"))
if catalog.get("schema_version") != 1 or experience.get("schema_version") != 1:
    raise SystemExit("Configuration schema version changed")
print("Manifest, authority, and configuration boundaries: GREEN")
PY
for script in build/*.sh; do test -x "$script"; bash -n "$script"; done
python3 -m compileall -q src tests build/manifest.py
PYTHONPATH=src python3 -m unittest discover -s tests -v
echo "AO-001A verification: GREEN"
