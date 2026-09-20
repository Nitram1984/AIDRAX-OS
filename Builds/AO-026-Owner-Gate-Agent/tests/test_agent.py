import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aidrax_owner_gate_agent import OwnerGateAgent


class OwnerGateAgentTests(unittest.TestCase):
    def test_default_is_prepared_and_does_not_execute(self):
        agent = OwnerGateAgent()
        receipt = agent.submit("git.push", {"repository": "aidrax-os", "branch": "main"}, "release evidence")
        self.assertEqual("PREPARED", agent.status)
        self.assertEqual("PENDING_OWNER", receipt.status)
        approved = agent.approve(receipt.request_id, receipt.scope_hash, True)
        self.assertEqual("APPROVED_FOR_DISPATCH", approved.status)

    def test_scope_mismatch_and_denial_fail_closed(self):
        agent = OwnerGateAgent()
        receipt = agent.submit("service.restart", {"unit": "example.service"}, "verified repair")
        self.assertEqual("RED/STOP", agent.approve(receipt.request_id, "wrong", True).status)
        self.assertEqual("RED/STOP", agent.approve(receipt.request_id, receipt.scope_hash, False).status)

    def test_injected_executor_needs_matching_approval_and_auto_apply(self):
        calls = []
        agent = OwnerGateAgent(executor=lambda request: calls.append(request.action) or "executed", auto_apply=True)
        receipt = agent.submit("test.action", {"target": "fixture"}, "unit test")
        result = agent.approve(receipt.request_id, receipt.scope_hash, True)
        self.assertEqual("GREEN", result.status)
        self.assertEqual(["test.action"], calls)


if __name__ == "__main__":
    unittest.main()
