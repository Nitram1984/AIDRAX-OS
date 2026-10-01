"""Offline byte verification for explicitly pinned signed UEFI bootstrap packages."""
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/'docs'/'SIGNED-BOOT-CONTRACT.json'
def sha256(path:Path)->str:
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()
def verify(root:Path, contract_path:Path=CONTRACT)->dict[str,object]:
    contract=json.loads(contract_path.read_text())
    checks=[]
    for name,artifact in contract['artifacts'].items():
        candidate=root/name
        actual=sha256(candidate) if candidate.is_file() and not candidate.is_symlink() else None
        checks.append({'name':name,'status':'VERIFIED' if actual==artifact['sha256'] else 'BLOCKED','sha256':actual})
    return {'status':'VERIFIED' if all(item['status']=='VERIFIED' for item in checks) else 'BLOCKED','checks':checks,'contract':contract}
