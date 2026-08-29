import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aidrax_iso_preflight.preflight import IsoPreflight, MINIMUM_WORKSPACE_BYTES


def contract_path():
    return ROOT / "docs" / "ISO-TARGET-CONTRACT.json"


class PreflightTests(unittest.TestCase):
    def preflight(self, **changes):
        defaults = dict(command_exists=lambda _: "/usr/bin/tool", architecture=lambda: "x86_64", uefi_present=lambda: True, free_space=lambda _: MINIMUM_WORKSPACE_BYTES)
        defaults.update(changes)
        return IsoPreflight(contract_path=contract_path(), **defaults)

    @staticmethod
    def approved_gates():
        return {"iso_build": True, "signing_procedure": True, "mok_registration": True, "hardware_boot_test": True}

    def test_contract_is_exact_and_ready_with_all_prerequisites(self):
        result = self.preflight().assess(ROOT, self.approved_gates())
        self.assertEqual("READY", result.status)
        self.assertEqual("Ubuntu", result.contract["distribution"]["name"])

    def test_missing_toolchain_is_blocked(self):
        result = self.preflight(command_exists=lambda tool: None if tool == "xorriso" else "/usr/bin/tool").assess(ROOT, self.approved_gates())
        self.assertEqual("BLOCKED", result.status)
        self.assertIn("missing=xorriso", next(check.detail for check in result.checks if check.name == "build_toolchain"))

    def test_wrong_architecture_is_blocked(self):
        result = self.preflight(architecture=lambda: "aarch64").assess(ROOT, self.approved_gates())
        self.assertEqual("BLOCKED", result.status)

    def test_missing_owner_gates_is_blocked(self):
        result = self.preflight().assess(ROOT, {})
        self.assertEqual("BLOCKED", result.status)
        self.assertIn("iso_build", next(check.detail for check in result.checks if check.name == "owner_gates"))

    def test_assessment_does_not_create_iso_or_mutate_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = pathlib.Path(directory)
            before = set(workspace.iterdir())
            result = self.preflight().assess(workspace, self.approved_gates())
            self.assertEqual("READY", result.status)
            self.assertEqual(before, set(workspace.iterdir()))
            self.assertFalse(list(workspace.glob("*.iso")))

    def test_invalid_contract_blocks_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            invalid = pathlib.Path(directory) / "contract.json"
            document = json.loads(contract_path().read_text())
            document["key_policy"]["secure_boot_bypass"] = True
            invalid.write_text(json.dumps(document))
            result = IsoPreflight(contract_path=invalid, command_exists=lambda _: "/tool", architecture=lambda: "amd64", uefi_present=lambda: True, free_space=lambda _: MINIMUM_WORKSPACE_BYTES).assess(ROOT, self.approved_gates())
            self.assertEqual("BLOCKED", result.status)


if __name__ == "__main__":
    unittest.main()
