#!/usr/bin/env python3
"""Validate the AO-008 source contract, tests and optionally its release ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args(argv)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    missing = [entry for entry in manifest["required_paths"] if not (ROOT / entry).is_file()]
    if missing:
        raise SystemExit("BLOCKED: missing required paths: " + ", ".join(missing))
    contract = json.loads((ROOT / manifest["iso_target_contract"]).read_text(encoding="utf-8"))
    if contract["execution_policy"] != {"iso_creation": False, "bootloader_changes": False, "firmware_changes": False, "storage_changes": False, "mok_actions": False}:
        raise SystemExit("BLOCKED: execution policy permits a prohibited action")
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
        actual = hashlib.sha256(args.archive.read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit("BLOCKED: SHA-256 mismatch")
    print("AO-008_RELEASE_VERIFICATION=GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
