import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aidrax_alpha_iso_build.prepare import AlphaBuildBlocked, build_request, write_request


class AlphaBuildPreparationTests(unittest.TestCase):
    @staticmethod
    def plan():
        return {"status": "READY_TO_PROVISION_CONTEXT", "rootless": True, "network": "none", "host_mounts": "none", "device_passthrough": False, "base_image": "registry.test/ubuntu@sha256:" + "a" * 64, "podman_build": ["podman", "build", "--pull=never", "--network=none", "--userns=keep-id"]}

    @staticmethod
    def report():
        return {"status": "VERIFIED", "lock_sha256": "b" * 64}

    @staticmethod
    def gates():
        return {"alpha_iso_build": True, "alpha_iso_artifact_retention": True, "vm_boot_test": True}

    def test_verified_evidence_and_gates_authorize_request(self):
        request = build_request(self.plan(), self.report(), self.gates())
        self.assertEqual("AUTHORIZED_FOR_ALPHA_ISO_EXECUTION", request["status"])
        self.assertEqual("b" * 64, request["source_lock_sha256"])

    def test_non_isolated_plan_or_unverified_sources_block(self):
        plan = self.plan()
        plan["network"] = "host"
        with self.assertRaisesRegex(AlphaBuildBlocked, "containment"):
            build_request(plan, self.report(), self.gates())
        report = self.report()
        report["status"] = "BLOCKED"
        with self.assertRaisesRegex(AlphaBuildBlocked, "not VERIFIED"):
            build_request(self.plan(), report, self.gates())

    def test_missing_gate_and_overwrite_block(self):
        gates = self.gates()
        gates["vm_boot_test"] = False
        with self.assertRaisesRegex(AlphaBuildBlocked, "vm_boot_test"):
            build_request(self.plan(), self.report(), gates)
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "request.json"
            request = build_request(self.plan(), self.report(), self.gates())
            write_request(request, path)
            with self.assertRaisesRegex(AlphaBuildBlocked, "must not already exist"):
                write_request(request, path)

    def test_source_never_invokes_builder(self):
        source = (ROOT / "src" / "aidrax_alpha_iso_build" / "prepare.py").read_text()
        self.assertNotIn("subprocess", source)
        self.assertNotIn("os.system", source)


if __name__ == "__main__":
    unittest.main()
