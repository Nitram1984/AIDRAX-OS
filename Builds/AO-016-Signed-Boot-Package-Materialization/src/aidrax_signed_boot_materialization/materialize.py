"""Hash-bound package download helpers; no package installation operations exist here."""
from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    """Calculate a streaming SHA-256 digest for a local file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package_filename(artifact: dict[str, Any]) -> str:
    """Return a flat safe local filename for one locked Debian package."""
    filename = Path(artifact["filename"]).name
    if not filename.endswith(".deb") or filename != Path(filename).name:
        raise ValueError(f"unsafe package filename: {artifact['filename']}")
    return filename


def verify(packages_dir: Path, lock: dict[str, Any]) -> dict[str, Any]:
    """Verify every expected package byte against its immutable closure entry."""
    checks = []
    for artifact in lock["artifacts"]:
        candidate = packages_dir / package_filename(artifact)
        actual_size = candidate.stat().st_size if candidate.is_file() else None
        actual_sha = sha256(candidate) if candidate.is_file() else None
        checks.append({"name": artifact["name"], "status": "VERIFIED" if actual_size == artifact["size"] and actual_sha == artifact["sha256"] else "BLOCKED", "sha256": actual_sha})
    return {"status": "VERIFIED" if all(item["status"] == "VERIFIED" for item in checks) else "BLOCKED", "checks": checks}


def materialize(packages_dir: Path, lock: dict[str, Any], snapshot_base_url: str) -> dict[str, Any]:
    """Fetch missing locked bytes atomically; reject conflicting existing files."""
    packages_dir.mkdir(parents=True, exist_ok=True)
    downloaded = []
    for artifact in lock["artifacts"]:
        target = packages_dir / package_filename(artifact)
        if target.exists():
            if target.is_symlink() or target.stat().st_size != artifact["size"] or sha256(target) != artifact["sha256"]:
                raise ValueError(f"BLOCKED: conflicting package exists: {target}")
            continue
        temporary = target.with_suffix(target.suffix + ".partial")
        if temporary.exists():
            raise ValueError(f"BLOCKED: partial package requires review: {temporary}")
        request_url = snapshot_base_url.rstrip("/") + "/" + artifact["filename"]
        digest = hashlib.sha256()
        size = 0
        try:
            with urllib.request.urlopen(request_url, timeout=60) as response, temporary.open("xb") as stream:
                for block in iter(lambda: response.read(1024 * 1024), b""):
                    stream.write(block)
                    digest.update(block)
                    size += len(block)
            if size != artifact["size"] or digest.hexdigest() != artifact["sha256"]:
                raise ValueError(f"BLOCKED: downloaded bytes mismatch: {artifact['name']}")
            os.replace(temporary, target)
            downloaded.append(artifact["name"])
        except Exception:
            if temporary.exists():
                temporary.unlink()
            raise
    report = verify(packages_dir, lock)
    if report["status"] != "VERIFIED":
        raise ValueError("BLOCKED: materialization verification failed")
    return {"status": "VERIFIED", "downloaded": downloaded, "package_count": len(lock["artifacts"])}


def load_json(path: Path) -> dict[str, Any]:
    """Read a JSON object and reject unexpected document types."""
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value
