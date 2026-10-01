#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aidrax_signed_boot_materialization.materialize import load_json, verify

parser = argparse.ArgumentParser()
parser.add_argument("--archive", type=pathlib.Path)
parser.add_argument("--packages-dir", type=pathlib.Path)
args = parser.parse_args()
manifest = json.loads((ROOT / "manifest.json").read_text())
missing = [path for path in manifest["required_paths"] if not (ROOT / path).is_file()]
if missing:
    raise SystemExit("BLOCKED: missing " + ", ".join(missing))
result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, check=False)
if result.returncode:
    raise SystemExit(result.returncode)
if args.packages_dir:
    report = verify(args.packages_dir, load_json(ROOT / "docs" / "AO-015-SIGNED-BOOT-CLOSURE-LOCK.json"))
    if report["status"] != "VERIFIED":
        raise SystemExit("BLOCKED: package bytes failed verification")
if args.archive:
    if zipfile.ZipFile(args.archive).testzip():
        raise SystemExit("BLOCKED: corrupt ZIP")
    expected = args.archive.with_suffix(args.archive.suffix + ".sha256").read_text().split()[0]
    if hashlib.sha256(args.archive.read_bytes()).hexdigest() != expected:
        raise SystemExit("BLOCKED: ZIP SHA-256 mismatch")
print("AO-016_RELEASE_VERIFICATION=GREEN")
