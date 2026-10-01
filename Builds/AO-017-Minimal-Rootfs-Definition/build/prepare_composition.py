#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aidrax_minimal_rootfs.definition import composition_request, write_json

parser = argparse.ArgumentParser()
parser.add_argument("--source-root", type=Path, required=True)
parser.add_argument("--output", type=Path, default=ROOT / "build-output" / "rootfs-composition-request.json")
args = parser.parse_args()
request = composition_request(args.source_root.resolve(strict=True), json.loads((ROOT / "docs" / "ROOTFS-CONTRACT.json").read_text()))
args.output.parent.mkdir(parents=True, exist_ok=True)
write_json(request, args.output)
print(f"AO-017_COMPOSITION_REQUEST={request['status']}")
