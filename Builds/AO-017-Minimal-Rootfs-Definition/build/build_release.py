#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "build-output"
ARCHIVE = OUT / "AO-017-Minimal-Rootfs-Definition.zip"
OUT.mkdir(exist_ok=True)
files = [path for path in sorted(ROOT.rglob("*")) if path.is_file() and not {"build-output", "__pycache__"}.intersection(path.relative_to(ROOT).parts)]
with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in files:
        archive.writestr(path.relative_to(ROOT).as_posix(), path.read_bytes())
digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
(OUT / (ARCHIVE.name + ".sha256")).write_text(f"{digest}  {ARCHIVE.name}\n")
(OUT / "release-manifest.json").write_text(json.dumps({"archive": ARCHIVE.name, "files": [path.relative_to(ROOT).as_posix() for path in files]}, indent=2, sort_keys=True) + "\n")
print(f"RELEASE_ARCHIVE={ARCHIVE}\nSHA256={digest}")
