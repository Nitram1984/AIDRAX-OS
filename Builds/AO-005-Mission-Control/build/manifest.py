#!/usr/bin/env python3
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
data["file_inventory"] = [
    {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    for path in sorted(ROOT.rglob("*"))
    if path.is_file() and not {"dist", "__pycache__"}.intersection(path.parts)
]
print(json.dumps(data, indent=2, sort_keys=True))
