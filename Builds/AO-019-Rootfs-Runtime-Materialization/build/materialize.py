#!/usr/bin/env python3
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"));from aidrax_rootfs_runtime_materialization.materialize import fetch,verify
parser=argparse.ArgumentParser();parser.add_argument("--fetch",action="store_true");parser.add_argument("--packages-dir",type=Path,default=ROOT/"build-output/packages");args=parser.parse_args()
contract=json.loads((ROOT/"docs/MATERIALIZATION-CONTRACT.json").read_text());lock_path=ROOT/"docs/AO-018-RUNTIME-CLOSURE-LOCK.json"
if hashlib.sha256(lock_path.read_bytes()).hexdigest()!=contract["source"]["lock_sha256"]:raise SystemExit("BLOCKED: lock SHA mismatch")
lock=json.loads(lock_path.read_text())
if args.fetch: print(f"AO-019_MATERIALIZATION=VERIFIED DOWNLOADED={fetch(args.packages_dir,lock,contract['snapshot_base_url'])}")
elif verify(args.packages_dir,lock): print("AO-019_MATERIALIZATION=VERIFIED")
else: raise SystemExit("BLOCKED: package bytes unavailable or mismatched")
