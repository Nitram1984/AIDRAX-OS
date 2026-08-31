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
from aidrax_signed_boot_closure.resolver import verify_lock

parser = argparse.ArgumentParser()
parser.add_argument("--archive", type=pathlib.Path)
parser.add_argument("--index", type=pathlib.Path, default=ROOT / "build-output" / "noble-main-amd64-Packages.gz")
parser.add_argument("--artifacts-dir", type=pathlib.Path)
args = parser.parse_args()
manifest = json.loads((ROOT / "manifest.json").read_text())
missing = [path for path in manifest["required_paths"] if not (ROOT / path).is_file()]
if missing:
    raise SystemExit("BLOCKED: missing " + ", ".join(missing))
result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, check=False)
if result.returncode:
    raise SystemExit(result.returncode)
if not args.index.is_file():
    raise SystemExit(f"BLOCKED: package index missing: {args.index}")
report = verify_lock(args.index, json.loads((ROOT / "docs" / "SIGNED-BOOT-CLOSURE-CONTRACT.json").read_text()), json.loads((ROOT / "docs" / "SIGNED-BOOT-CLOSURE-LOCK.json").read_text()), args.artifacts_dir)
if report["status"] != "VERIFIED":
    raise SystemExit("BLOCKED: closure verification failed")
if args.archive:
    if zipfile.ZipFile(args.archive).testzip():
        raise SystemExit("BLOCKED: corrupt ZIP")
    expected = args.archive.with_suffix(args.archive.suffix + ".sha256").read_text().split()[0]
    if hashlib.sha256(args.archive.read_bytes()).hexdigest() != expected:
        raise SystemExit("BLOCKED: ZIP SHA-256 mismatch")
print("AO-015_RELEASE_VERIFICATION=GREEN")
