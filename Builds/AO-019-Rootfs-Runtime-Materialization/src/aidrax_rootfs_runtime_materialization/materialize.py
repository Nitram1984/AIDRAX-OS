"""Atomic offline-verifiable package download helpers."""
from __future__ import annotations
import hashlib, os, urllib.request
from pathlib import Path

def digest(path: Path) -> str:
    """Return streaming SHA-256."""
    hash_value=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1048576),b""): hash_value.update(block)
    return hash_value.hexdigest()

def verify(directory: Path, lock: dict) -> bool:
    """Verify all lock entries against existing regular files."""
    return all((candidate:=directory/Path(item["filename"]).name).is_file() and not candidate.is_symlink() and candidate.stat().st_size==item["size"] and digest(candidate)==item["sha256"] for item in lock["artifacts"])

def fetch(directory: Path, lock: dict, base: str) -> int:
    """Fetch missing package bytes atomically; reject conflicting local bytes."""
    directory.mkdir(parents=True,exist_ok=True); downloaded=0
    for item in lock["artifacts"]:
        target=directory/Path(item["filename"]).name
        if target.exists():
            if target.is_symlink() or target.stat().st_size!=item["size"] or digest(target)!=item["sha256"]: raise ValueError(f"BLOCKED: conflicting file: {target}")
            continue
        partial=target.with_suffix(target.suffix+".partial")
        if partial.exists(): raise ValueError(f"BLOCKED: partial file needs review: {partial}")
        hash_value=hashlib.sha256(); size=0
        try:
            with urllib.request.urlopen(base.rstrip("/")+"/"+item["filename"],timeout=60) as response, partial.open("xb") as stream:
                for block in iter(lambda:response.read(1048576),b""):
                    stream.write(block); hash_value.update(block); size+=len(block)
            if size!=item["size"] or hash_value.hexdigest()!=item["sha256"]: raise ValueError(f"BLOCKED: checksum mismatch: {item['name']}")
            os.replace(partial,target); downloaded+=1
        except Exception:
            partial.unlink(missing_ok=True); raise
    if not verify(directory,lock): raise ValueError("BLOCKED: final package verification failed")
    return downloaded
