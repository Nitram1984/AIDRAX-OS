"""Fail-closed authorization for the first rootless AIDRAX Alpha ISO build."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Mapping


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "docs" / "ALPHA-BUILD-CONTRACT.json"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class AlphaBuildBlocked(ValueError):
    """Raised when the alpha build cannot be evidenced safely."""


def load_object(path: Path) -> dict[str, object]:
    """Load a JSON object supplied by a prior verified stage."""
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise AlphaBuildBlocked(f"JSON object required: {path}")
    return document


def validate_builder_plan(plan: Mapping[str, object]) -> None:
    """Require the exact constrained rootless plan emitted by AO-010."""
    if plan.get("status") != "READY_TO_PROVISION_CONTEXT" or plan.get("rootless") is not True:
        raise AlphaBuildBlocked("AO-010 rootless builder plan is not ready")
    if plan.get("network") != "none" or plan.get("host_mounts") != "none" or plan.get("device_passthrough") is not False:
        raise AlphaBuildBlocked("AO-010 plan does not enforce isolated build containment")
    command = plan.get("podman_build")
    if not isinstance(command, list) or command[:2] != ["podman", "build"] or "--pull=never" not in command or "--network=none" not in command:
        raise AlphaBuildBlocked("AO-010 plan lacks the required rootless Podman command")
    image = plan.get("base_image")
    if not isinstance(image, str) or "@sha256:" not in image:
        raise AlphaBuildBlocked("AO-010 plan lacks a pinned base image")


def validate_source_report(report: Mapping[str, object]) -> str:
    """Require AO-012's byte-verified supply-chain report."""
    digest = report.get("lock_sha256")
    if report.get("status") != "VERIFIED" or not isinstance(digest, str) or not SHA256.fullmatch(digest):
        raise AlphaBuildBlocked("AO-012 source report is not VERIFIED with a valid lock hash")
    return digest


def validate_gates(contract: Mapping[str, object], gates: Mapping[str, object]) -> None:
    """Require every Alpha-specific Owner-Gate before request creation."""
    required = contract.get("approval_requirements")
    if not isinstance(required, list):
        raise AlphaBuildBlocked("invalid alpha build approval requirements")
    missing = [gate for gate in required if gates.get(gate) is not True]
    if missing:
        raise AlphaBuildBlocked("unapproved owner gates: " + ", ".join(missing))


def build_request(plan: Mapping[str, object], report: Mapping[str, object], gates: Mapping[str, object]) -> dict[str, object]:
    """Bind the isolated builder plan and verified source report into one request."""
    validate_builder_plan(plan)
    lock_hash = validate_source_report(report)
    validate_gates(load_object(CONTRACT_PATH), gates)
    request: dict[str, object] = {
        "request_version": "1.0.0",
        "status": "AUTHORIZED_FOR_ALPHA_ISO_EXECUTION",
        "execution": "requires-separate-owner-gate",
        "source_lock_sha256": lock_hash,
        "base_image": plan["base_image"],
        "rootless_podman_build": plan["podman_build"],
        "prohibited_actions": ["key_generation", "key_import", "mok_actions", "firmware_changes", "storage_changes"],
    }
    payload = json.dumps(request, sort_keys=True, separators=(",", ":")).encode("utf-8")
    request["request_sha256"] = hashlib.sha256(payload).hexdigest()
    return request


def write_request(request: Mapping[str, object], path: Path) -> None:
    """Write one new immutable request file without overwriting evidence."""
    if path.exists():
        raise AlphaBuildBlocked("build request path must not already exist")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Prepare a request only; this CLI never invokes Podman or writes an ISO."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--builder-plan", type=Path, required=True)
    parser.add_argument("--source-report", type=Path, required=True)
    parser.add_argument("--owner-gates", type=Path, required=True)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        request = build_request(load_object(args.builder_plan), load_object(args.source_report), load_object(args.owner_gates))
        if args.apply:
            if args.request is None:
                raise AlphaBuildBlocked("--request is required with --apply")
            write_request(request, args.request)
    except (OSError, json.JSONDecodeError, AlphaBuildBlocked) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    print(json.dumps(request, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
