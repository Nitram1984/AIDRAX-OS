"""Offline byte verification of local sources against an AO-011 canonical lock."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "docs" / "SOURCE-VERIFICATION-CONTRACT.json"
REQUIRED = ("base_image_manifest", "apt_release", "xorriso", "squashfs-tools", "grub-efi-amd64-bin")


class VerificationBlocked(ValueError):
    """Raised for unsafe index paths or insufficient verification evidence."""


@dataclass(frozen=True)
class Check:
    """One local source verification outcome."""

    name: str
    status: str
    detail: str


def load_object(path: Path) -> dict[str, object]:
    """Read one JSON object without resolving external content."""
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise VerificationBlocked(f"JSON object required: {path}")
    return document


def local_file(root: Path, relative: object) -> Path:
    """Resolve a regular in-root file while rejecting traversal and symlinks."""
    relative_path = Path(relative) if isinstance(relative, str) else None
    if not relative_path or not relative or relative_path.is_absolute() or ".." in relative_path.parts:
        raise VerificationBlocked(f"unsafe artifact path: {relative}")
    candidate = root / relative_path
    if candidate.is_symlink():
        raise VerificationBlocked(f"unsafe artifact path: {relative}")
    try:
        resolved_root, resolved = root.resolve(), candidate.resolve(strict=True)
    except OSError as error:
        raise VerificationBlocked(f"missing artifact path: {relative}") from error
    if resolved_root not in resolved.parents or not resolved.is_file():
        raise VerificationBlocked(f"unsafe artifact path: {relative}")
    return resolved


def sha256(path: Path) -> str:
    """Compute a streaming SHA-256 without modifying the local artifact."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_hashes(lock: Mapping[str, object]) -> dict[str, str]:
    """Extract every expected local source hash from a canonical AO-011 lock."""
    image, snapshot, evidence = lock.get("base_image"), lock.get("apt_snapshot"), lock.get("supply_chain_evidence")
    if not isinstance(image, dict) or not isinstance(snapshot, dict) or not isinstance(evidence, dict) or not isinstance(evidence.get("packages"), dict):
        raise VerificationBlocked("lock is not an AO-011 canonical lock")
    image_digest = image.get("digest")
    if not isinstance(image_digest, str) or not image_digest.startswith("sha256:"):
        raise VerificationBlocked("lock base image digest is invalid")
    release = snapshot.get("release_sha256")
    if not isinstance(release, str):
        raise VerificationBlocked("lock APT release hash is invalid")
    hashes = {"base_image_manifest": image_digest.removeprefix("sha256:"), "apt_release": release}
    for package in REQUIRED[2:]:
        entry = evidence["packages"].get(package)
        if not isinstance(entry, dict) or not isinstance(entry.get("sha256"), str):
            raise VerificationBlocked(f"lock package evidence missing: {package}")
        hashes[package] = entry["sha256"]
    return hashes


def verify(lock: Mapping[str, object], artifact_root: Path, index: Mapping[str, object], gates: Mapping[str, object]) -> dict[str, object]:
    """Compare explicit local artifact files with all hashes in the lock."""
    expected = expected_hashes(lock)
    checks: list[Check] = []
    for name in REQUIRED:
        try:
            actual = sha256(local_file(artifact_root, index.get(name)))
            checks.append(Check(name, "VERIFIED" if actual == expected[name] else "BLOCKED", f"sha256={actual}"))
        except (OSError, VerificationBlocked) as error:
            checks.append(Check(name, "BLOCKED", str(error)))
    missing_gates = [gate for gate in ("verify_local_sources", "review_verification_report") if gates.get(gate) is not True]
    checks.append(Check("owner_gates", "VERIFIED" if not missing_gates else "BLOCKED", "all owner gates approved" if not missing_gates else "unapproved=" + ",".join(missing_gates)))
    status = "VERIFIED" if all(check.status == "VERIFIED" for check in checks) else "BLOCKED"
    return {"status": status, "checks": [asdict(check) for check in checks], "lock_sha256": lock.get("lock_sha256")}


def main(argv: list[str] | None = None) -> int:
    """Run read-only verification and optionally write a report to a chosen path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--artifact-index", type=Path, required=True)
    parser.add_argument("--owner-gates", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    try:
        result = verify(load_object(args.lock), args.artifact_root, load_object(args.artifact_index), load_object(args.owner_gates))
    except (OSError, json.JSONDecodeError, VerificationBlocked) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])
    return 0 if result["status"] == "VERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
