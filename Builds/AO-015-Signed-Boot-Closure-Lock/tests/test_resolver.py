from __future__ import annotations

import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aidrax_signed_boot_closure.resolver import resolve, verify_lock


def stanza(name: str, version: str, depends: str = "") -> str:
    fields = [f"Package: {name}", "Architecture: amd64", f"Version: {version}"]
    if depends:
        fields.append(f"Depends: {depends}")
    fields.extend([f"Filename: pool/main/{name}_{version}_amd64.deb", "Size: 1", f"SHA256: {'a' * 64}"])
    return "\n".join(fields)


class ResolverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = {"build_id": "AO-015", "snapshot": {"packages_url": "https://example.invalid/Packages.gz", "packages_sha256": ""}, "root_packages": {"shim-signed": "1", "grub-efi-amd64-signed": "1"}, "alternative_preferences": {"grub-efi-amd64|grub-pc": "grub-efi-amd64"}}

    def test_resolves_predepends_depends_and_uefi_alternative(self) -> None:
        content = "\n\n".join([stanza("shim-signed", "1", "grub-efi-amd64-signed, grub-efi-amd64 | grub-pc"), stanza("grub-efi-amd64-signed", "1", "grub-common"), stanza("grub-efi-amd64", "1"), stanza("grub-pc", "1"), stanza("grub-common", "1")])
        with tempfile.TemporaryDirectory() as directory:
            index = Path(directory) / "Packages.gz"
            with gzip.open(index, "wt") as stream:
                stream.write(content)
            self.contract["snapshot"]["packages_sha256"] = __import__("hashlib").sha256(index.read_bytes()).hexdigest()
            lock = resolve(index, self.contract)
        self.assertEqual([item["name"] for item in lock["artifacts"]], ["grub-common", "grub-efi-amd64", "grub-efi-amd64-signed", "shim-signed"])

    def test_lock_mismatch_is_blocked(self) -> None:
        content = "\n\n".join([stanza("shim-signed", "1"), stanza("grub-efi-amd64-signed", "1")])
        with tempfile.TemporaryDirectory() as directory:
            index = Path(directory) / "Packages.gz"
            with gzip.open(index, "wt") as stream:
                stream.write(content)
            self.contract["snapshot"]["packages_sha256"] = __import__("hashlib").sha256(index.read_bytes()).hexdigest()
            lock = resolve(index, self.contract)
            lock["artifacts"] = []
            report = verify_lock(index, self.contract, lock)
        self.assertEqual(report["status"], "BLOCKED")
