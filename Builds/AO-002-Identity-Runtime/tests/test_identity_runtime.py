import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aidrax_identity import IdentityPolicy, IdentityRuntime, IdentityRuntimeError, Principal, Role

class Registry:
    def __init__(self): self.records = []
    def add(self, component): self.records.append(component)
class Events:
    def __init__(self): self.items = []
    def publish(self, event, payload): self.items.append((event, payload))

class IdentityRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.registry, self.events = Registry(), Events()
        self.runtime = IdentityRuntime(self.registry, self.events); self.runtime.start()
        self.operator = Principal("aidrax.operator", "AIDRAX Operator", frozenset({Role.OPERATOR}))
        self.runtime.register_principal(self.operator)
        self.runtime.register_policy(IdentityPolicy("mission.deploy", frozenset({Role.OPERATOR})))
    def test_start_registers_only_runtime_identity(self):
        self.assertEqual(self.registry.records[0]["id"], "aidrax.identity.runtime")
        self.assertEqual(self.events.items[0][0], "identity.runtime_ready")
    def test_operator_is_authorized_and_session_is_ephemeral(self):
        session = self.runtime.open_session("aidrax.operator")
        self.assertEqual(self.runtime.authorize(session.session_id, "mission.deploy"), self.operator)
        self.runtime.close_session(session.session_id)
        with self.assertRaises(IdentityRuntimeError): self.runtime.authorize(session.session_id, "mission.deploy")
    def test_role_denial_is_auditable(self):
        observer = Principal("aidrax.observer", "Observer", frozenset({Role.OBSERVER}))
        self.runtime.register_principal(observer); session = self.runtime.open_session(observer.principal_id)
        with self.assertRaises(IdentityRuntimeError): self.runtime.authorize(session.session_id, "mission.deploy")
        self.assertEqual(self.events.items[-1][0], "identity.authorization_denied")
    def test_invalid_identifier_is_rejected(self):
        with self.assertRaises(ValueError): Principal("AIDRAX", "AIDRAX", frozenset({Role.OPERATOR}))

if __name__ == "__main__": unittest.main()
