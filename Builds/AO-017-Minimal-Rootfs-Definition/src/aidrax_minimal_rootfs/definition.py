"""Offline verifier for a precisely supplied AIDRAX custom-rootfs input set."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    """Return the SHA-256 digest of a local regular input file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_relative(path: str) -> Path:
    """Reject absolute and traversal paths before resolving an input path."""
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"unsafe contract path: {path}")
    return candidate


def verify_inputs(source_root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    """Verify every rootfs and package input byte required by the contract."""
    entries = [("base-rootfs", contract["base_rootfs"]), *[(item["package"], item) for item in contract["runtime_packages"]]]
    checks = []
    for name, entry in entries:
        candidate = source_root / safe_relative(entry["path"])
        actual = sha256(candidate) if candidate.is_file() and not candidate.is_symlink() else None
        checks.append({"name": name, "status": "VERIFIED" if actual == entry["sha256"] else "BLOCKED", "sha256": actual})
    return {"status": "VERIFIED" if all(item["status"] == "VERIFIED" for item in checks) else "BLOCKED", "checks": checks}


def composition_request(source_root: Path, contract: dict[str, Any]) -> dict[str, Any]:
    """Create a declarative future assembly request only for verified local bytes."""
    report = verify_inputs(source_root, contract)
    if report["status"] != "VERIFIED":
        raise ValueError("BLOCKED: rootfs inputs are not verified")
    return {
        "build_id": contract["build_id"],
        "status": "AUTHORIZED_FOR_SEPARATE_ROOTFS_ASSEMBLY",
        "target": contract["target"],
        "base_rootfs": contract["base_rootfs"],
        "runtime_packages": contract["runtime_packages"],
        "install_order": contract["integration"]["package_install_order"],
        "source_root_sha256": sha256(source_root / safe_relative(contract["base_rootfs"]["path"])),
        "limitations": ["This request does not extract a rootfs.", "This request does not install packages or create an ISO."]
    }


def write_json(value: dict[str, Any], path: Path) -> None:
    """Write a canonical reviewable JSON request."""
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
