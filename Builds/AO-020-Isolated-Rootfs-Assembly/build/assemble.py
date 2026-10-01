#!/usr/bin/env python3
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"));from aidrax_rootfs_assembly.assemble import assemble
parser=argparse.ArgumentParser();parser.add_argument("--base",type=Path,required=True);parser.add_argument("--packages",type=Path,required=True);parser.add_argument("--runtime-lock",type=Path,required=True);parser.add_argument("--target",type=Path,default=ROOT/"build-output/rootfs");args=parser.parse_args()
contract=json.loads((ROOT/"docs/ASSEMBLY-CONTRACT.json").read_text())
if hashlib.sha256(args.runtime_lock.read_bytes()).hexdigest()!=contract["inputs"]["runtime_lock_sha256"]:raise SystemExit("BLOCKED: runtime lock SHA mismatch")
print(json.dumps(assemble(args.base,args.packages,json.loads(args.runtime_lock.read_text()),ROOT/"overlay",args.target,contract["inputs"]["base_rootfs_sha256"]),sort_keys=True))
