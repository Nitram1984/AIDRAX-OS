#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; parser=argparse.ArgumentParser();parser.add_argument("source",type=Path);args=parser.parse_args()
contract=json.loads((ROOT/"docs/MATERIALIZATION-CONTRACT.json").read_text()); data=args.source.read_bytes()
if args.source.is_symlink() or hashlib.sha256(data).hexdigest()!=contract["source"]["lock_sha256"]:raise SystemExit("BLOCKED: AO-018 lock mismatch")
lock=json.loads(data)
if len(lock.get("artifacts",[]))!=contract["source"]["package_count"]:raise SystemExit("BLOCKED: AO-018 package count mismatch")
(ROOT/"docs/AO-018-RUNTIME-CLOSURE-LOCK.json").write_bytes(data);print("AO-019_LOCK_IMPORT=GREEN")
