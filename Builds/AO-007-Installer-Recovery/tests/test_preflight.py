import pathlib, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from aidrax_installer_recovery import InstallerPreflight, TargetSpec
class Gate:
    def approved(self, target, serial): return target == "/dev/sdz" and serial == "SERIAL-7"
def target(**changes):
    values = dict(device="/dev/sdz", model="Test Disk", serial="SERIAL-7", backup_reference="sha256:verified", rollback_reference="/mnt/recovery/restore.json"); values.update(changes); return TargetSpec(**values)
class Tests(unittest.TestCase):
    def test_blocks_without_gate(self): self.assertEqual("BLOCKED", InstallerPreflight().assess(target()).status)
    def test_ready_only_for_exact_gated_target(self): self.assertEqual("READY", InstallerPreflight(Gate()).assess(target()).status)
    def test_missing_backup_and_rollback_block(self):
        result = InstallerPreflight(Gate()).assess(target(backup_reference="", rollback_reference=""))
        self.assertEqual(("verified_backup_required", "rollback_required"), result.reasons)
    def test_non_device_target_blocks(self): self.assertIn("exact_device_required", InstallerPreflight(Gate()).assess(target(device="disk")).reasons)
if __name__ == "__main__": unittest.main()
