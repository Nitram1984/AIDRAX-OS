#!/usr/bin/env python3
"""Emit deterministic release provenance for AO-001 without dependencies."""
from __future__ import annotations
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXCLUDED = {".git", "dist", "__pycache__"}

def files() -> list[pathlib.Path]:
    return [p for p in sorted(ROOT.rglob("*")) if p.is_file() and not any(x in p.parts for x in EXCLUDED)]

def main() -> int:
    document = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    document["file_inventory"] = [{"path": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files()]
    print(json.dumps(document, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
