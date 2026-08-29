import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aidrax_supply_chain_lock.lock import LockBlocked, canonical_lock, write_lock


class SupplyChainLockTests(unittest.TestCase):
    def manifest(self):
        return {
            "target": {"distribution": "Ubuntu", "release": "24.04 LTS", "flavour": "Minimal", "architecture": "amd64"},
            "base_image": {"reference": "registry.test/ubuntu", "digest": "sha256:" + "a" * 64},
            "apt_snapshot": {"url": "https://snapshot.test/ubuntu/noble", "release_sha256": "b" * 64},
            "packages": {name: {"version": "1.0-1", "url": f"https://mirror.test/{name}.deb", "sha256": "c" * 64} for name in ("xorriso", "squashfs-tools", "grub-efi-amd64-bin")},
            "independent_verification": {"evidence_id": "owner-record-20260829"},
        }

    def test_valid_manifest_produces_ao010_compatible_lock(self):
        lock = canonical_lock(self.manifest())
        self.assertEqual("sha256:" + "a" * 64, lock["base_image"]["digest"])
        self.assertEqual("1.0-1", lock["packages"]["xorriso"])
        self.assertEqual(64, len(lock["lock_sha256"]))

    def test_unsafe_source_or_missing_hash_is_blocked(self):
        manifest = self.manifest()
        manifest["apt_snapshot"]["url"] = "http://mirror.test/noble"
        with self.assertRaisesRegex(LockBlocked, "HTTPS"):
            canonical_lock(manifest)
        manifest = self.manifest()
        manifest["packages"]["xorriso"]["sha256"] = "not-a-hash"
        with self.assertRaisesRegex(LockBlocked, "SHA-256"):
            canonical_lock(manifest)

    def test_lock_write_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = pathlib.Path(directory) / "lock.json"
            write_lock(canonical_lock(self.manifest()), output)
            with self.assertRaisesRegex(LockBlocked, "must not already exist"):
                write_lock(canonical_lock(self.manifest()), output)

    def test_source_never_executes_commands(self):
        source = (ROOT / "src" / "aidrax_supply_chain_lock" / "lock.py").read_text()
        self.assertNotIn("subprocess", source)
        self.assertNotIn("urllib.request", source)


if __name__ == "__main__":
    unittest.main()
