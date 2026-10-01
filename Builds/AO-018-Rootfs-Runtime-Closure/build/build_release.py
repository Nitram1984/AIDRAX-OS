#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, pathlib, zipfile
ROOT = pathlib.Path(__file__).resolve().parents[1]; OUT = ROOT / "build-output"; ARCHIVE = OUT / "AO-018-Rootfs-Runtime-Closure.zip"; OUT.mkdir(exist_ok=True)
files = [p for p in sorted(ROOT.rglob("*")) if p.is_file() and not {"build-output", "__pycache__"}.intersection(p.relative_to(ROOT).parts)]
with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in files: archive.writestr(path.relative_to(ROOT).as_posix(), path.read_bytes())
digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(); (OUT / (ARCHIVE.name + ".sha256")).write_text(f"{digest}  {ARCHIVE.name}\n"); (OUT / "release-manifest.json").write_text(json.dumps({"archive": ARCHIVE.name, "files": [p.relative_to(ROOT).as_posix() for p in files]}, indent=2, sort_keys=True) + "\n")
print(f"RELEASE_ARCHIVE={ARCHIVE}\nSHA256={digest}")
