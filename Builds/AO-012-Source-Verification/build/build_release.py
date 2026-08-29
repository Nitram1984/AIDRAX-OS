#!/usr/bin/env python3
"""Create AO-012's deterministic source archive; never verify or fetch sources."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "build-output"
ARCHIVE = OUTPUT / "AO-012-Source-Verification.zip"


def main() -> int:
    OUTPUT.mkdir(exist_ok=True)
    files = sorted(path for path in ROOT.rglob("*") if path.is_file() and not {".git", "build-output", "__pycache__"}.intersection(path.relative_to(ROOT).parts))
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    (OUTPUT / f"{ARCHIVE.name}.sha256").write_text(f"{digest}  {ARCHIVE.name}\n", encoding="utf-8")
    (OUTPUT / "release-manifest.json").write_text(json.dumps({"archive": ARCHIVE.name, "files": [path.relative_to(ROOT).as_posix() for path in files]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"RELEASE_ARCHIVE={ARCHIVE}\nSHA256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
