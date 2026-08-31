#!/usr/bin/env python3
import argparse,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"));from aidrax_rootfs_runtime_materialization.materialize import verify
parser=argparse.ArgumentParser();parser.add_argument("--packages-dir",type=pathlib.Path,required=True);args=parser.parse_args()
manifest=json.loads((ROOT/"manifest.json").read_text());missing=[p for p in manifest["required_paths"] if not (ROOT/p).is_file()]
if missing:raise SystemExit("BLOCKED: missing "+", ".join(missing))
if subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-v"],cwd=ROOT).returncode:raise SystemExit(1)
if not verify(args.packages_dir,json.loads((ROOT/"docs/AO-018-RUNTIME-CLOSURE-LOCK.json").read_text())):raise SystemExit("BLOCKED: package verification failed")
print("AO-019_RELEASE_VERIFICATION=GREEN")
