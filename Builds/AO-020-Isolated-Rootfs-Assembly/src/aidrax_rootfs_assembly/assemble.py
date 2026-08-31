"""Safe extraction of already-verified rootfs and Debian package payloads."""
from __future__ import annotations
import hashlib, shutil, subprocess, tarfile
from pathlib import Path

def digest(path: Path) -> str:
 """Return SHA-256 for a regular file."""
 value=hashlib.sha256()
 with path.open("rb") as stream:
  for block in iter(lambda:stream.read(1048576),b""):value.update(block)
 return value.hexdigest()

def safe_extract(archive: Path,target: Path) -> None:
 """Extract a pinned tar after rejecting traversal and device entries.

 Absolute symlink targets are retained because Ubuntu base rootfs uses them for
 standard alternatives; archive member names themselves may never be absolute.
 """
 with tarfile.open(archive,"r:*") as tar:
  for member in tar.getmembers():
   relative=Path(member.name)
   if relative.is_absolute() or ".." in relative.parts or member.isdev():raise ValueError(f"unsafe tar member: {member.name}")
  tar.extractall(target,filter=lambda member, _: member)

def assemble(base: Path,packages: Path,lock: dict,overlay: Path,target: Path,base_sha: str) -> dict:
 """Create a new rootfs directory, fail if target exists, and extract only payload data."""
 if target.exists():raise ValueError(f"BLOCKED: target exists: {target}")
 if digest(base)!=base_sha:raise ValueError("BLOCKED: base rootfs SHA-256 mismatch")
 if not shutil.which("dpkg-deb"):raise ValueError("BLOCKED: dpkg-deb unavailable")
 target.mkdir(parents=True);safe_extract(base,target)
 for item in lock["artifacts"]:
  package=packages/Path(item["filename"]).name
  if not package.is_file() or package.is_symlink() or package.stat().st_size!=item["size"] or digest(package)!=item["sha256"]:raise ValueError(f"BLOCKED: package mismatch: {item['name']}")
  result=subprocess.run(["dpkg-deb","--fsys-tarfile",str(package)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
  if result.returncode:raise ValueError(f"BLOCKED: payload read failed: {item['name']}")
  payload=target/".aidrax-payload.tar";payload.write_bytes(result.stdout)
  safe_extract(payload,target);payload.unlink()
 shutil.copytree(overlay,target,dirs_exist_ok=True,symlinks=True)
 return {"status":"PAYLOAD_ROOTFS_ASSEMBLED_NOT_BOOTABLE","package_count":len(lock["artifacts"]),"rootfs":str(target)}
