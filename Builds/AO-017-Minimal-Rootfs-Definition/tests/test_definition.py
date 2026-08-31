from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aidrax_minimal_rootfs.definition import composition_request, verify_inputs


class DefinitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = b"base"; self.kernel = b"kernel"
        self.contract = {"build_id": "AO-017", "target": {"architecture": "amd64"}, "base_rootfs": {"path": "base.tar.gz", "sha256": hashlib.sha256(self.base).hexdigest()}, "runtime_packages": [{"path": "artifacts/kernel.deb", "package": "kernel", "sha256": hashlib.sha256(self.kernel).hexdigest()}], "integration": {"package_install_order": ["kernel"]}}

    def test_verified_inputs_make_composition_request(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / "base.tar.gz").write_bytes(self.base); (root / "artifacts").mkdir(); (root / "artifacts/kernel.deb").write_bytes(self.kernel)
            request = composition_request(root, self.contract)
        self.assertEqual(request["status"], "AUTHORIZED_FOR_SEPARATE_ROOTFS_ASSEMBLY")

    def test_missing_input_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / "base.tar.gz").write_bytes(self.base)
            self.assertEqual(verify_inputs(root, self.contract)["status"], "BLOCKED")
