#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aidrax_minimal_rootfs.definition import verify_inputs

parser = argparse.ArgumentParser()
parser.add_argument("--source-root", type=Path, required=True)
args = parser.parse_args()
contract = json.loads((ROOT / "docs" / "ROOTFS-CONTRACT.json").read_text())
report = verify_inputs(args.source_root.resolve(strict=True), contract)
print(f"AO-017_INPUTS={report['status']} CHECKS={len(report['checks'])}")
if report["status"] != "VERIFIED":
    raise SystemExit(2)
