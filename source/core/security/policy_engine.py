from rbac import RBAC

class PolicyEngine:
    def __init__(self, rbac=None):
        self.rbac = rbac or RBAC()
        self.denied_actions = {"delete_without_owner", "publish_without_owner", "sudo_without_owner"}

    def evaluate(self, role, action):
        if action in self.denied_actions and role != "owner":
            return {"allowed": False, "reason": "owner_gate_required"}
        if self.rbac.allowed(role, action):
            return {"allowed": True, "reason": "rbac_allowed"}
        return {"allowed": False, "reason": "rbac_denied"}

    def health(self):
        return {"status": "GREEN", "component": "policy_engine"}
