import sys
from pathlib import Path
SECURITY_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SECURITY_ROOT))

from audit import AuditLog
from rbac import RBAC
from policy_engine import PolicyEngine
from secret_manager import SecretManager
from security_engine import SecurityEngine

class SecurityRuntime:
    def __init__(self):
        self.audit = AuditLog()
        self.rbac = RBAC()
        self.policy = PolicyEngine(self.rbac)
        self.secrets = SecretManager()
        self.engine = SecurityEngine(self.policy, self.audit)

    def smoke_test(self):
        owner = self.engine.check_permission("owner", "delete_without_owner")
        agent = self.engine.check_permission("agent", "delete_without_owner")
        viewer = self.engine.check_permission("viewer", "read")
        secret = self.secrets.set_runtime_only("AIDRAX_TEST_SECRET", "runtime-only")
        return {
            "status": "GREEN" if owner["allowed"] and not agent["allowed"] and viewer["allowed"] and secret["status"] == "GREEN" else "RED",
            "owner_gate": {"owner": owner, "agent": agent},
            "viewer_read": viewer,
            "secret_manager": self.secrets.health(),
            "audit": self.audit.health(),
            "rbac": self.rbac.health(),
            "policy": self.policy.health(),
            "engine": self.engine.health()
        }

    def health(self):
        return {
            "status": "GREEN",
            "security_engine": self.engine.health(),
            "rbac": self.rbac.health(),
            "policy_engine": self.policy.health(),
            "secret_manager": self.secrets.health(),
            "audit": self.audit.health()
        }

if __name__ == "__main__":
    print(SecurityRuntime().smoke_test())
