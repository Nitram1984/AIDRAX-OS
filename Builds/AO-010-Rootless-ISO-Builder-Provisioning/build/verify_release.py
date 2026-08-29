#!/usr/bin/env python3
"""Validate AO-010's safety contract and optional source-release archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROHIBITED = {"container_start": False, "image_pull": False, "iso_creation": False, "key_generation": False, "key_import": False, "mok_actions": False, "firmware_changes": False, "storage_changes": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args(argv)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    missing = [entry for entry in manifest["required_paths"] if not (ROOT / entry).is_file()]
    if missing:
        raise SystemExit("BLOCKED: missing required paths: " + ", ".join(missing))
    contract = json.loads((ROOT / manifest["provisioning_contract"]).read_text(encoding="utf-8"))
    expected_builder = {"runtime": "podman", "rootless": True, "userns": "keep-id", "network_after_resolution": "none", "host_mounts": "none", "device_passthrough": False, "privileged": False, "secret_mounts": False}
    if contract.get("target") != {"distribution": "Ubuntu", "release": "24.04 LTS", "flavour": "Minimal", "architecture": "amd64"} or contract.get("builder") != expected_builder:
        raise SystemExit("BLOCKED: rootless builder contract changed")
    if contract.get("prohibited_actions") != PROHIBITED:
        raise SystemExit("BLOCKED: prohibited-action contract changed")
    source = (ROOT / "src" / "aidrax_rootless_iso_builder" / "provision.py").read_text(encoding="utf-8")
    if "subprocess" in source or "os.system" in source:
        raise SystemExit("BLOCKED: provisioner may not execute host commands")
    test = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, check=False)
    if test.returncode:
        return test.returncode
    if args.archive:
        with zipfile.ZipFile(args.archive) as archive:
            bad = archive.testzip()
            if bad:
                raise SystemExit(f"BLOCKED: corrupt ZIP member: {bad}")
        checksum = args.archive.with_suffix(args.archive.suffix + ".sha256")
        expected = checksum.read_text(encoding="utf-8").split()[0]
        if hashlib.sha256(args.archive.read_bytes()).hexdigest() != expected:
            raise SystemExit("BLOCKED: SHA-256 mismatch")
    print("AO-010_RELEASE_VERIFICATION=GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
