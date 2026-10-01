import pathlib, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aidrax_desktop import DesktopShell, DesktopState
class Gate:
    def approved(self, control, principal_id): return control == "SESSION" and principal_id == "owner"
class DesktopShellTests(unittest.TestCase):
    def test_shell_is_locked_by_default_and_unlocks_only_with_principal(self):
        shell = DesktopShell(); self.assertEqual(DesktopState.LOCKED, shell.state())
        with self.assertRaises(PermissionError): shell.propose_control("SESSION")
        self.assertEqual(DesktopState.READY, shell.unlock("owner"))
    def test_controls_default_to_pending_and_do_not_execute(self):
        shell = DesktopShell(); shell.unlock("owner")
        self.assertEqual("PENDING_OWNER", shell.propose_control("RESTART").status)
    def test_gate_only_approves_dispatch_proposal(self):
        shell = DesktopShell(Gate()); shell.unlock("owner")
        self.assertEqual("APPROVED_FOR_DISPATCH", shell.propose_control("SESSION").status)
    def test_invalid_principal_and_control_are_rejected(self):
        shell = DesktopShell()
        with self.assertRaises(ValueError): shell.unlock("")
        shell.unlock("owner")
        with self.assertRaises(ValueError): shell.propose_control("FORMAT")
if __name__ == "__main__": unittest.main()
