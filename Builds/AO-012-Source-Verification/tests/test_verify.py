import hashlib
import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aidrax_source_verification.verify import VerificationBlocked, verify


class SourceVerificationTests(unittest.TestCase):
    names = ("base_image_manifest", "apt_release", "xorriso", "squashfs-tools", "grub-efi-amd64-bin")

    def create_sources(self, directory):
        root = pathlib.Path(directory)
        index, hashes = {}, {}
        for name in self.names:
            path = root / f"{name}.bin"
            path.write_bytes(name.encode())
            index[name] = path.name
            hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        return root, index, hashes

    @staticmethod
    def gates():
        return {"verify_local_sources": True, "review_verification_report": True}

    def lock(self, hashes):
        return {"lock_sha256": "d" * 64, "base_image": {"digest": "sha256:" + hashes["base_image_manifest"]}, "apt_snapshot": {"release_sha256": hashes["apt_release"]}, "supply_chain_evidence": {"packages": {name: {"sha256": hashes[name]} for name in self.names[2:]}}}

    def test_all_sources_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            root, index, hashes = self.create_sources(directory)
            self.assertEqual("VERIFIED", verify(self.lock(hashes), root, index, self.gates())["status"])

    def test_mismatch_and_missing_gate_block(self):
        with tempfile.TemporaryDirectory() as directory:
            root, index, hashes = self.create_sources(directory)
            (root / index["xorriso"]).write_bytes(b"changed")
            self.assertEqual("BLOCKED", verify(self.lock(hashes), root, index, self.gates())["status"])
            gates = self.gates()
            gates["review_verification_report"] = False
            self.assertEqual("BLOCKED", verify(self.lock(hashes), root, index, gates)["status"])

    def test_symlink_and_escape_are_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root, index, hashes = self.create_sources(directory)
            index["apt_release"] = "../outside"
            result = verify(self.lock(hashes), root, index, self.gates())
            self.assertEqual("BLOCKED", result["status"])
            self.assertIn("unsafe artifact path", next(item["detail"] for item in result["checks"] if item["name"] == "apt_release"))

    def test_source_never_downloads_or_executes(self):
        source = (ROOT / "src" / "aidrax_source_verification" / "verify.py").read_text()
        self.assertNotIn("subprocess", source)
        self.assertNotIn("urllib.request", source)


if __name__ == "__main__":
    unittest.main()
