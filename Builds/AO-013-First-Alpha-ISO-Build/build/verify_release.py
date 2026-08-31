#!/usr/bin/env python3
"""Verify AO-013's fail-closed Alpha-build authorization contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROHIBITED = {"iso_creation": False, "container_start": False, "image_pull": False, "key_generation": False, "key_import": False, "mok_actions": False, "firmware_changes": False, "storage_changes": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args(argv)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    missing = [item for item in manifest["required_paths"] if not (ROOT / item).is_file()]
    if missing:
        raise SystemExit("BLOCKED: missing required paths: " + ", ".join(missing))
    contract = json.loads((ROOT / manifest["alpha_build_contract"]).read_text(encoding="utf-8"))
    if contract.get("prohibited_actions") != PROHIBITED:
        raise SystemExit("BLOCKED: alpha build safety contract changed")
    source = (ROOT / "src" / "aidrax_alpha_iso_build" / "prepare.py").read_text(encoding="utf-8")
    if "subprocess" in source or "os.system" in source:
        raise SystemExit("BLOCKED: authorization layer may not invoke a builder")
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, check=False)
    if result.returncode:
        return result.returncode
    if args.archive:
        with zipfile.ZipFile(args.archive) as archive:
            if bad := archive.testzip():
                raise SystemExit(f"BLOCKED: corrupt ZIP member: {bad}")
        expected = args.archive.with_suffix(args.archive.suffix + ".sha256").read_text(encoding="utf-8").split()[0]
        if hashlib.sha256(args.archive.read_bytes()).hexdigest() != expected:
            raise SystemExit("BLOCKED: SHA-256 mismatch")
    print("AO-013_RELEASE_VERIFICATION=GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
