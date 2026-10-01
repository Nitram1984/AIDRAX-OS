#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aidrax_signed_boot_closure.resolver import dump_json, resolve, sha256

parser = argparse.ArgumentParser()
parser.add_argument("--fetch-index", action="store_true")
parser.add_argument("--index", type=Path)
parser.add_argument("--write-lock", action="store_true")
args = parser.parse_args()
contract = json.loads((ROOT / "docs" / "SIGNED-BOOT-CLOSURE-CONTRACT.json").read_text())
index = args.index or ROOT / "build-output" / "noble-main-amd64-Packages.gz"
if args.fetch_index:
    index.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(contract["snapshot"]["packages_url"], timeout=30) as response:
        index.write_bytes(response.read())
if not index.is_file():
    raise SystemExit(f"BLOCKED: package index missing: {index}")
if sha256(index) != contract["snapshot"]["packages_sha256"]:
    raise SystemExit("BLOCKED: package index SHA-256 mismatch")
lock = resolve(index, contract)
if args.write_lock:
    dump_json(lock, ROOT / "docs" / "SIGNED-BOOT-CLOSURE-LOCK.json")
print(f"AO-015_CLOSURE={lock['status']} PACKAGES={len(lock['artifacts'])}")
