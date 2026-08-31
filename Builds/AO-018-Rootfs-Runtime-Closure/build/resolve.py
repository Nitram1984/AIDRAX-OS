#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from aidrax_rootfs_runtime_closure.resolve import closure, sha256, write_lock
parser = argparse.ArgumentParser(); parser.add_argument("--index", type=Path, required=True); parser.add_argument("--write-lock", action="store_true"); args = parser.parse_args()
contract = json.loads((ROOT / "docs" / "RUNTIME-CLOSURE-CONTRACT.json").read_text())
if sha256(args.index) != contract["snapshot"]["packages_sha256"]: raise SystemExit("BLOCKED: package index SHA-256 mismatch")
lock = closure(args.index, contract)
if args.write_lock: write_lock(lock, ROOT / "docs" / "RUNTIME-CLOSURE-LOCK.json")
print(f"AO-018_CLOSURE={lock['status']} PACKAGES={len(lock['artifacts'])}")
