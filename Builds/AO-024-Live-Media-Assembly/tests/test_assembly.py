import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aidrax_live_media import AssemblyPlan, MissingInputError


class AssemblyTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads((ROOT / "config/media-contract.json").read_text())

    def test_refuses_missing_signed_efi_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            (root / "boot").mkdir()
            (root / "boot/vmlinuz-6.8.0-31-generic").touch()
            (root / "boot/initrd.img-6.8.0-31-generic").touch()
            plan = AssemblyPlan.from_contract(self.contract, root, root / "efi")
            with self.assertRaises(MissingInputError):
                plan.assert_ready_for_iso_materialization()

    def test_accepts_complete_immutable_input_set(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            for relative in ("boot/vmlinuz-6.8.0-31-generic", "boot/initrd.img-6.8.0-31-generic", "efi/EFI/BOOT/BOOTX64.EFI", "efi/EFI/BOOT/grubx64.efi"):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"test")
            self.contract["efi_sha256"] = {
                "EFI/BOOT/BOOTX64.EFI": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                "EFI/BOOT/grubx64.efi": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
            }
            plan = AssemblyPlan.from_contract(self.contract, root, root / "efi")
            plan.assert_ready_for_iso_materialization()
            self.assertEqual(plan.missing_inputs(), ())

    def test_sddm_surface_uses_real_brand_asset_name(self):
        qml = (ROOT / "desktop/sddm-theme/Main.qml").read_text()
        self.assertIn("aidrax-spectral-dragon-001.png", qml)
        self.assertIn("sddm.login", qml)
        self.assertIn("QtQuick.Controls", qml)

    def test_contract_cannot_allow_automatic_install(self):
        unsafe = dict(self.contract)
        unsafe["prohibited_actions"] = []
        with self.assertRaises(ValueError):
            AssemblyPlan.from_contract(unsafe, pathlib.Path("/rootfs"), pathlib.Path("/efi"))

    def test_rejects_tampered_efi_input(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            for relative in ("boot/vmlinuz-6.8.0-31-generic", "boot/initrd.img-6.8.0-31-generic", "efi/EFI/BOOT/BOOTX64.EFI", "efi/EFI/BOOT/grubx64.efi"):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"tampered")
            plan = AssemblyPlan.from_contract(self.contract, root, root / "efi")
            with self.assertRaises(MissingInputError):
                plan.assert_ready_for_iso_materialization()
