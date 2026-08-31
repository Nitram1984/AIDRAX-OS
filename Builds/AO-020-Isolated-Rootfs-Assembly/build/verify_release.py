#!/usr/bin/env python3
import json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];manifest=json.loads((ROOT/"manifest.json").read_text());missing=[p for p in manifest["required_paths"] if not (ROOT/p).is_file()]
if missing:raise SystemExit("BLOCKED: missing "+", ".join(missing))
raise SystemExit(subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-v"],cwd=ROOT).returncode)
