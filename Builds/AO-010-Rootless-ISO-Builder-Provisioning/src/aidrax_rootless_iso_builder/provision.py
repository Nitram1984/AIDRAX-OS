"""Validate approved inputs and provision a non-executable rootless builder context."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "docs" / "PROVISIONING-CONTRACT.json"
TARGET = {"distribution": "Ubuntu", "release": "24.04 LTS", "flavour": "Minimal", "architecture": "amd64"}
REQUIRED_PACKAGES = {"xorriso", "squashfs-tools", "grub-efi-amd64-bin"}
DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")


class ProvisioningBlocked(ValueError):
    """Raised when an input would make provisioning non-reproducible or unsafe."""


@dataclass(frozen=True)
class ProvisioningPlan:
    lock: dict[str, object]
    contract: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        """Return the declarative, non-executable Podman build plan."""
        image = self.lock["base_image"]
        assert isinstance(image, dict)
        return {
            "status": "READY_TO_PROVISION_CONTEXT",
            "execution": "not-authorized-by-ao-010",
            "rootless": True,
            "network": "none",
            "host_mounts": "none",
            "device_passthrough": False,
            "podman_build": [
                "podman", "build", "--pull=never", "--network=none", "--userns=keep-id",
                "--security-opt=no-new-privileges", "--cap-drop=all", "--file", "Containerfile", ".",
            ],
            "base_image": f"{image['reference']}@{image['digest']}",
        }


def load_json(path: Path) -> dict[str, object]:
    """Load one JSON object and reject all other JSON top-level types."""
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ProvisioningBlocked(f"JSON object required: {path}")
    return document


def validate_lock(lock: Mapping[str, object]) -> None:
    """Require pinned, credential-free reproducibility inputs."""
    if lock.get("target") != TARGET:
        raise ProvisioningBlocked("lock target must be Ubuntu 24.04 LTS Minimal amd64")
    image = lock.get("base_image")
    if not isinstance(image, dict) or not isinstance(image.get("reference"), str) or not image["reference"].strip():
        raise ProvisioningBlocked("base_image.reference is required")
    if "@" in image["reference"] or not DIGEST.fullmatch(str(image.get("digest", ""))):
        raise ProvisioningBlocked("base_image.digest must be an immutable sha256 digest")
    snapshot = lock.get("apt_snapshot")
    url = snapshot.get("url") if isinstance(snapshot, dict) else None
    parsed = urlparse(url) if isinstance(url, str) else None
    if not parsed or parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ProvisioningBlocked("apt_snapshot.url must be a credential-free HTTPS URL")
    packages = lock.get("packages")
    if not isinstance(packages, dict) or not REQUIRED_PACKAGES.issubset(packages):
        raise ProvisioningBlocked("package lock misses required ISO builder packages")
    if any(not isinstance(version, str) or not version.strip() or "\n" in version for version in packages.values()):
        raise ProvisioningBlocked("every package version must be a non-empty single line")


def validate_gates(contract: Mapping[str, object], gates: Mapping[str, object]) -> None:
    """Require every declared Owner-Gate before provisioning."""
    required = contract.get("approval_requirements")
    if not isinstance(required, list):
        raise ProvisioningBlocked("contract approval requirements are invalid")
    missing = [gate for gate in required if gates.get(gate) is not True]
    if missing:
        raise ProvisioningBlocked("unapproved owner gates: " + ", ".join(missing))


def context_files(plan: ProvisioningPlan) -> dict[str, str]:
    """Render the exact four files allowed in a new build context."""
    image = plan.lock["base_image"]
    snapshot = plan.lock["apt_snapshot"]
    assert isinstance(image, dict) and isinstance(snapshot, dict)
    sources = f"deb {snapshot['url']} noble main restricted universe multiverse\n"
    containerfile = "\n".join((
        f"FROM {image['reference']}@{image['digest']}",
        "LABEL org.opencontainers.image.title=aidrax-rootless-iso-builder",
        "COPY package-lock.json /opt/aidrax/package-lock.json",
        "COPY sources.list /opt/aidrax/sources.list",
        "# AO-010 provisions context only; package installation is a separately gated operation.",
        "",
    ))
    return {
        "Containerfile": containerfile,
        "package-lock.json": json.dumps(plan.lock, indent=2, sort_keys=True) + "\n",
        "sources.list": sources,
        "podman-build-plan.json": json.dumps(plan.as_dict(), indent=2, sort_keys=True) + "\n",
    }


def provision(lock: Mapping[str, object], gates: Mapping[str, object], output_dir: Path | None, apply: bool) -> ProvisioningPlan:
    """Validate inputs and optionally create one previously absent local context."""
    contract = load_json(CONTRACT_PATH)
    validate_lock(lock)
    validate_gates(contract, gates)
    plan = ProvisioningPlan(dict(lock), contract)
    if not apply:
        return plan
    if output_dir is None:
        raise ProvisioningBlocked("--output-dir is required with --apply")
    if output_dir.exists():
        raise ProvisioningBlocked("output directory must not already exist")
    output_dir.mkdir(parents=True)
    for name, content in context_files(plan).items():
        (output_dir / name).write_text(content, encoding="utf-8")
    return plan


def main(argv: list[str] | None = None) -> int:
    """Run the non-executing CLI and return a shell-compatible status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--owner-gates", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--apply", action="store_true", help="write a new local context after validation")
    args = parser.parse_args(argv)
    try:
        plan = provision(load_json(args.lock), load_json(args.owner_gates), args.output_dir, args.apply)
    except (OSError, json.JSONDecodeError, ProvisioningBlocked) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    print(json.dumps(plan.as_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
