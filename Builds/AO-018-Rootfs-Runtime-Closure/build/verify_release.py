#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, pathlib, subprocess, sys, zipfile
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from aidrax_rootfs_runtime_closure.resolve import closure, sha256
parser = argparse.ArgumentParser(); parser.add_argument("--index", type=pathlib.Path, required=True); parser.add_argument("--archive", type=pathlib.Path); args = parser.parse_args()
manifest = json.loads((ROOT / "manifest.json").read_text()); missing = [p for p in manifest["required_paths"] if not (ROOT / p).is_file()]
if missing: raise SystemExit("BLOCKED: missing " + ", ".join(missing))
if subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT).returncode: raise SystemExit(1)
contract = json.loads((ROOT / "docs" / "RUNTIME-CLOSURE-CONTRACT.json").read_text()); lock = json.loads((ROOT / "docs" / "RUNTIME-CLOSURE-LOCK.json").read_text())
if sha256(args.index) != contract["snapshot"]["packages_sha256"] or closure(args.index, contract)["artifacts"] != lock.get("artifacts"): raise SystemExit("BLOCKED: closure lock mismatch")
if args.archive:
    if zipfile.ZipFile(args.archive).testzip(): raise SystemExit("BLOCKED: corrupt ZIP")
    if hashlib.sha256(args.archive.read_bytes()).hexdigest() != args.archive.with_suffix(args.archive.suffix + ".sha256").read_text().split()[0]: raise SystemExit("BLOCKED: ZIP SHA-256 mismatch")
print("AO-018_RELEASE_VERIFICATION=GREEN")
