#!/usr/bin/env python3
import argparse,hashlib,json,pathlib,subprocess,sys,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--archive',type=pathlib.Path);args=parser.parse_args()
manifest=json.loads((ROOT/'manifest.json').read_text());missing=[p for p in manifest['required_paths'] if not (ROOT/p).is_file()]
if missing:raise SystemExit('BLOCKED: missing '+', '.join(missing))
contract=json.loads((ROOT/'docs'/'SIGNED-BOOT-CONTRACT.json').read_text())
if contract['target']!={'distribution':'Ubuntu','release':'24.04 LTS','architecture':'amd64','boot':'UEFI','secure_boot':'enabled'}:raise SystemExit('BLOCKED: target changed')
result=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,check=False)
if result.returncode:raise SystemExit(result.returncode)
if args.archive:
 if zipfile.ZipFile(args.archive).testzip():raise SystemExit('BLOCKED: corrupt ZIP')
 expected=args.archive.with_suffix(args.archive.suffix+'.sha256').read_text().split()[0]
 if hashlib.sha256(args.archive.read_bytes()).hexdigest()!=expected:raise SystemExit('BLOCKED: SHA mismatch')
print('AO-014_RELEASE_VERIFICATION=GREEN')
