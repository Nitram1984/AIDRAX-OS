import json
import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aidrax_rootless_iso_builder.provision import ProvisioningBlocked, context_files, provision


class RootlessProvisioningTests(unittest.TestCase):
    def lock(self):
        return {
            "target": {"distribution": "Ubuntu", "release": "24.04 LTS", "flavour": "Minimal", "architecture": "amd64"},
            "base_image": {"reference": "registry.test/ubuntu", "digest": "sha256:" + "a" * 64},
            "apt_snapshot": {"url": "https://snapshot.test/ubuntu/20260829T000000Z"},
            "packages": {"xorriso": "1.5.6-1", "squashfs-tools": "1:4.6.1-1", "grub-efi-amd64-bin": "2.12-1ubuntu7"},
        }

    @staticmethod
    def gates():
        return {"provision_rootless_builder": True, "base_image_and_snapshot_lock": True, "boot_test_environment": True}

    def test_dry_run_is_ready_and_never_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / "context"
            plan = provision(self.lock(), self.gates(), output, apply=False)
            self.assertEqual("READY_TO_PROVISION_CONTEXT", plan.as_dict()["status"])
            self.assertFalse(output.exists())

    def test_apply_creates_only_declared_context_files(self):
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / "context"
            plan = provision(self.lock(), self.gates(), output, apply=True)
            self.assertEqual({"Containerfile", "package-lock.json", "podman-build-plan.json", "sources.list"}, {path.name for path in output.iterdir()})
            self.assertEqual("none", json.loads((output / "podman-build-plan.json").read_text())["network"])
            self.assertIn("@sha256:", (output / "Containerfile").read_text())
            self.assertEqual("READY_TO_PROVISION_CONTEXT", plan.as_dict()["status"])

    def test_missing_gate_blocks(self):
        gates = self.gates()
        gates["boot_test_environment"] = False
        with self.assertRaisesRegex(ProvisioningBlocked, "boot_test_environment"):
            provision(self.lock(), gates, None, apply=False)

    def test_unpinned_image_or_credentials_block(self):
        lock = self.lock()
        lock["base_image"]["digest"] = "ubuntu:24.04"
        with self.assertRaisesRegex(ProvisioningBlocked, "immutable"):
            provision(lock, self.gates(), None, apply=False)
        lock = self.lock()
        lock["apt_snapshot"]["url"] = "https://user:secret@snapshot.test/ubuntu"
        with self.assertRaisesRegex(ProvisioningBlocked, "credential-free"):
            provision(lock, self.gates(), None, apply=False)

    def test_plan_has_no_privileged_runtime_capability(self):
        plan = provision(self.lock(), self.gates(), None, apply=False)
        rendered = json.dumps(context_files(plan))
        self.assertNotIn("--privileged", rendered)
        self.assertNotIn("--volume", rendered)
        self.assertNotIn("subprocess", (ROOT / "src" / "aidrax_rootless_iso_builder" / "provision.py").read_text())


if __name__ == "__main__":
    unittest.main()
