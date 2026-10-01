#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
def main() -> int:
    manifest = json.loads((ROOT / "manifest.json").read_text())
    files = [p for p in sorted(ROOT.rglob("*")) if p.is_file() and not {"dist", "__pycache__"}.intersection(p.parts)]
    manifest["file_inventory"] = [{"path": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    print(json.dumps(manifest, indent=2, sort_keys=True)); return 0
if __name__ == "__main__": raise SystemExit(main())
