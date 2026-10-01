from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aidrax_signed_boot_materialization.materialize import materialize, verify


class MaterializationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bytes = b"aidrax-test-package"
        self.lock = {"artifacts": [{"name": "shim-signed", "filename": "pool/main/s/shim-signed/shim-signed_1_amd64.deb", "size": len(self.bytes), "sha256": hashlib.sha256(self.bytes).hexdigest()}]}

    def test_verifies_matching_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "shim-signed_1_amd64.deb"
            path.write_bytes(self.bytes)
            self.assertEqual(verify(Path(directory), self.lock)["status"], "VERIFIED")

    def test_rejects_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "shim-signed_1_amd64.deb"
            path.write_bytes(b"incorrect")
            self.assertEqual(verify(Path(directory), self.lock)["status"], "BLOCKED")

    def test_rejects_conflicting_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "shim-signed_1_amd64.deb"
            path.write_bytes(b"incorrect")
            with self.assertRaisesRegex(ValueError, "conflicting package"):
                materialize(Path(directory), self.lock, "https://example.invalid")
