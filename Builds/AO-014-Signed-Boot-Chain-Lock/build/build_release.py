#!/usr/bin/env python3
import hashlib,json,pathlib,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'build-output';ARCHIVE=OUT/'AO-014-Signed-Boot-Chain-Lock.zip'
OUT.mkdir(exist_ok=True)
files=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and not {'build-output','__pycache__'}.intersection(p.relative_to(ROOT).parts)]
with zipfile.ZipFile(ARCHIVE,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files:z.writestr(p.relative_to(ROOT).as_posix(),p.read_bytes())
digest=hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
(OUT/(ARCHIVE.name+'.sha256')).write_text(f'{digest}  {ARCHIVE.name}\n')
(OUT/'release-manifest.json').write_text(json.dumps({'archive':ARCHIVE.name,'files':[p.relative_to(ROOT).as_posix() for p in files]},indent=2,sort_keys=True)+'\n')
print(f'RELEASE_ARCHIVE={ARCHIVE}\nSHA256={digest}')
