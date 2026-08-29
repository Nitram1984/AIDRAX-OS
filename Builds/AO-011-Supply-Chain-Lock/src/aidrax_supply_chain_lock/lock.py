"""Offline validation and canonicalization of an approved ISO supply-chain manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Mapping
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "docs" / "SUPPLY-CHAIN-CONTRACT.json"
TARGET = {"distribution": "Ubuntu", "release": "24.04 LTS", "flavour": "Minimal", "architecture": "amd64"}
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class LockBlocked(ValueError):
    """Raised when supplied evidence is insufficient for a reproducible lock."""


def load_object(path: Path) -> dict[str, object]:
    """Load one JSON object, never an arbitrary JSON document."""
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise LockBlocked(f"JSON object required: {path}")
    return document


def require_sha256(value: object, field: str) -> str:
    """Return one canonical SHA-256 value or stop before a lock is emitted."""
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise LockBlocked(f"{field} must be a lowercase SHA-256 hex digest")
    return value


def require_https_url(value: object, field: str) -> str:
    """Reject unencrypted, credential-bearing, or malformed source URLs."""
    if not isinstance(value, str):
        raise LockBlocked(f"{field} must be an HTTPS URL")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise LockBlocked(f"{field} must be a credential-free HTTPS URL")
    return value


def validate_gates(contract: Mapping[str, object], gates: Mapping[str, object]) -> None:
    """Require each supply-chain Owner-Gate before normalization."""
    required = contract.get("approval_requirements")
    if not isinstance(required, list):
        raise LockBlocked("invalid approval requirements")
    missing = [gate for gate in required if gates.get(gate) is not True]
    if missing:
        raise LockBlocked("unapproved owner gates: " + ", ".join(missing))


def canonical_lock(manifest: Mapping[str, object]) -> dict[str, object]:
    """Validate an input manifest and return the AO-010 compatible canonical lock."""
    if manifest.get("target") != TARGET:
        raise LockBlocked("manifest target must be Ubuntu 24.04 LTS Minimal amd64")
    image = manifest.get("base_image")
    if not isinstance(image, dict) or not isinstance(image.get("reference"), str) or not image["reference"].strip() or "@" in image["reference"]:
        raise LockBlocked("base_image.reference must be a repository without a tag digest")
    image_digest = require_sha256(str(image.get("digest", "")).removeprefix("sha256:"), "base_image.digest")
    snapshot = manifest.get("apt_snapshot")
    if not isinstance(snapshot, dict):
        raise LockBlocked("apt_snapshot is required")
    snapshot_url = require_https_url(snapshot.get("url"), "apt_snapshot.url")
    snapshot_hash = require_sha256(snapshot.get("release_sha256"), "apt_snapshot.release_sha256")
    packages = manifest.get("packages")
    if not isinstance(packages, dict):
        raise LockBlocked("packages object is required")
    required_packages = {"xorriso", "squashfs-tools", "grub-efi-amd64-bin"}
    if not required_packages.issubset(packages):
        raise LockBlocked("manifest misses required ISO builder packages")
    normalized_packages: dict[str, dict[str, str]] = {}
    for name in sorted(required_packages):
        package = packages[name]
        if not isinstance(package, dict) or not isinstance(package.get("version"), str) or not package["version"].strip() or "\n" in package["version"]:
            raise LockBlocked(f"packages.{name}.version must be a non-empty single line")
        normalized_packages[name] = {
            "version": package["version"],
            "url": require_https_url(package.get("url"), f"packages.{name}.url"),
            "sha256": require_sha256(package.get("sha256"), f"packages.{name}.sha256"),
        }
    evidence = manifest.get("independent_verification")
    if not isinstance(evidence, dict) or not isinstance(evidence.get("evidence_id"), str) or not evidence["evidence_id"].strip():
        raise LockBlocked("independent_verification.evidence_id is required")
    result: dict[str, object] = {
        "lock_version": "1.0.0",
        "target": TARGET,
        "base_image": {"reference": image["reference"], "digest": "sha256:" + image_digest},
        "apt_snapshot": {"url": snapshot_url, "release_sha256": snapshot_hash},
        "packages": {name: value["version"] for name, value in normalized_packages.items()},
        "supply_chain_evidence": {"packages": normalized_packages, "independent_verification": {"evidence_id": evidence["evidence_id"]}},
    }
    payload = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    result["lock_sha256"] = hashlib.sha256(payload).hexdigest()
    return result


def write_lock(lock: Mapping[str, object], output: Path) -> None:
    """Write exactly one new lock file, never overwrite prior evidence."""
    if output.exists():
        raise LockBlocked("output lock must not already exist")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Run validation and optionally create a canonical lock without network access."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--owner-gates", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        contract = load_object(CONTRACT_PATH)
        validate_gates(contract, load_object(args.owner_gates))
        lock = canonical_lock(load_object(args.manifest))
        if args.apply:
            if args.output is None:
                raise LockBlocked("--output is required with --apply")
            write_lock(lock, args.output)
    except (OSError, json.JSONDecodeError, LockBlocked) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    print(json.dumps(lock, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
