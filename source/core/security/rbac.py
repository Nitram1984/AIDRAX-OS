class RBAC:
    DEFAULT_ROLES = {
        "owner": ["*"],
        "admin": ["read", "write", "execute", "manage_services"],
        "developer": ["read", "write", "test"],
        "agent": ["read", "analyze", "recommend"],
        "viewer": ["read"]
    }

    def __init__(self, roles=None):
        self.roles = roles or dict(self.DEFAULT_ROLES)

    def allowed(self, role, action):
        permissions = self.roles.get(role, [])
        return "*" in permissions or action in permissions

    def health(self):
        return {"status": "GREEN", "component": "rbac", "roles": sorted(self.roles.keys())}
