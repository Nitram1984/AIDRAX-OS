#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aidrax_signed_boot_materialization.materialize import load_json, materialize, verify

parser = argparse.ArgumentParser()
parser.add_argument("--fetch", action="store_true")
parser.add_argument("--packages-dir", type=Path, default=ROOT / "build-output" / "packages")
args = parser.parse_args()
contract = load_json(ROOT / "docs" / "MATERIALIZATION-CONTRACT.json")
lock_path = ROOT / "docs" / "AO-015-SIGNED-BOOT-CLOSURE-LOCK.json"
if hashlib.sha256(lock_path.read_bytes()).hexdigest() != contract["source"]["closure_lock_sha256"]:
    raise SystemExit("BLOCKED: imported closure lock SHA-256 mismatch")
lock = load_json(lock_path)
if args.fetch:
    result = materialize(args.packages_dir, lock, contract["snapshot_base_url"])
    print(f"AO-016_MATERIALIZATION={result['status']} DOWNLOADED={len(result['downloaded'])}")
else:
    result = verify(args.packages_dir, lock)
    print(f"AO-016_MATERIALIZATION={result['status']}")
    if result["status"] != "VERIFIED":
        raise SystemExit(2)
