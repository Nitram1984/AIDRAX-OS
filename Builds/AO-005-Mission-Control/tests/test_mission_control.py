import pathlib
import sys
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aidrax_mission_control import MissionControl
class Registry:
    def components(self): return ({"id": "hermes", "status": "READY"}, {"id": "atlas", "status": "READY"})
class Events:
    def recent_events(self, limit): return ({"event": "health.changed", "limit": limit},)
class Health:
    def health(self): return ({"id": "node-b", "state": "DEGRADED"}, {"id": "node-a", "state": "READY"})
class Approved:
    def approved(self, action, rationale): return action == "restart.safe" and rationale == "owner requested"
class MissionControlTests(unittest.TestCase):
    def test_snapshot_is_ordered_and_read_only(self):
        snapshot = MissionControl(Registry(), Events(), Health()).snapshot()
        self.assertEqual(["atlas", "hermes"], [record["id"] for record in snapshot.components])
        self.assertEqual(["node-a", "node-b"], [record["id"] for record in snapshot.health])
        self.assertEqual("health.changed", snapshot.events[0]["event"])
        with self.assertRaises(TypeError): snapshot.components[0]["status"] = "MUTATED"
    def test_actions_are_pending_without_a_gate_and_never_execute(self):
        proposal = MissionControl(Registry(), Events(), Health()).propose_action("restart.safe", "owner requested")
        self.assertEqual("PENDING_OWNER", proposal.status); self.assertTrue(proposal.proposal_id)
    def test_gate_can_approve_dispatch_but_not_execute(self):
        proposal = MissionControl(Registry(), Events(), Health(), Approved()).propose_action("restart.safe", "owner requested")
        self.assertEqual("APPROVED_FOR_DISPATCH", proposal.status)
    def test_invalid_input_and_event_limit_are_rejected(self):
        control = MissionControl(Registry(), Events(), Health())
        with self.assertRaises(ValueError): control.snapshot(101)
        with self.assertRaises(ValueError): control.propose_action("", "reason")
if __name__ == "__main__": unittest.main()
