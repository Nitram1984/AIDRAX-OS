import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aidrax_iso_builder_environment.preflight import BuilderEnvironmentPreflight


class BuilderEnvironmentPreflightTests(unittest.TestCase):
    def preflight(self, **changes):
        defaults = dict(command_exists=lambda _: "/tool", architecture=lambda: "x86_64")
        defaults.update(changes)
        return BuilderEnvironmentPreflight(**defaults)

    @staticmethod
    def approved_gates():
        return {"builder_environment": True, "package_source_lock": True, "boot_test_preparation": True}

    def test_exact_contract_and_approved_gates_are_ready(self):
        result = self.preflight().assess(self.approved_gates())
        self.assertEqual("READY", result.status)
        self.assertEqual("Ubuntu", result.builder_contract["target"]["distribution"])

    def test_missing_toolchain_is_blocked(self):
        result = self.preflight(command_exists=lambda tool: None if tool == "podman" else "/tool").assess(self.approved_gates())
        self.assertEqual("BLOCKED", result.status)
        self.assertIn("missing=podman", next(check.detail for check in result.checks if check.name == "builder_toolchain"))

    def test_wrong_architecture_is_blocked(self):
        self.assertEqual("BLOCKED", self.preflight(architecture=lambda: "aarch64").assess(self.approved_gates()).status)

    def test_missing_owner_gate_is_blocked(self):
        result = self.preflight().assess({"builder_environment": True})
        self.assertEqual("BLOCKED", result.status)
        self.assertIn("package_source_lock", next(check.detail for check in result.checks if check.name == "owner_gates"))

    def test_invalid_containment_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            contract = json.loads((ROOT / "docs" / "BUILDER-ENVIRONMENT-CONTRACT.json").read_text())
            contract["containment"]["privileged_mode"] = True
            path = pathlib.Path(directory) / "contract.json"
            path.write_text(json.dumps(contract))
            self.assertEqual("BLOCKED", BuilderEnvironmentPreflight(contract_path=path, command_exists=lambda _: "/tool", architecture=lambda: "amd64").assess(self.approved_gates()).status)

    def test_assessment_never_creates_iso_or_runs_builder(self):
        result = self.preflight().assess(self.approved_gates())
        self.assertEqual("READY", result.status)
        source = (ROOT / "src" / "aidrax_iso_builder_environment" / "preflight.py").read_text()
        self.assertNotIn("subprocess", source)
        self.assertNotIn("os.system", source)


if __name__ == "__main__":
    unittest.main()
