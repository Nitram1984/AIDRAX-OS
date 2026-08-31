#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--from-ao015", type=Path, required=True)
args = parser.parse_args()
contract = json.loads((ROOT / "docs" / "MATERIALIZATION-CONTRACT.json").read_text())
source = args.from_ao015.resolve(strict=True)
if source.is_symlink() or hashlib.sha256(source.read_bytes()).hexdigest() != contract["source"]["closure_lock_sha256"]:
    raise SystemExit("BLOCKED: AO-015 closure lock mismatch")
lock = json.loads(source.read_text())
if lock.get("status") != "VERIFIED_METADATA_CLOSURE_ONLY" or len(lock.get("artifacts", [])) != contract["package_count"]:
    raise SystemExit("BLOCKED: AO-015 closure lock contract mismatch")
target = ROOT / "docs" / "AO-015-SIGNED-BOOT-CLOSURE-LOCK.json"
target.write_bytes(source.read_bytes())
print(f"AO-016_LOCK_IMPORT=GREEN PACKAGES={len(lock['artifacts'])}")
