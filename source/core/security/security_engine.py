from datetime import datetime, timezone

class SecurityEngine:
    def __init__(self, policy_engine=None, audit=None):
        self.policy_engine = policy_engine
        self.audit = audit
        self.events = []

    def emit(self, event_type, payload=None):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "payload": payload or {}
        }
        self.events.append(event)
        if self.audit:
            self.audit.record("SECURITY", event_type, payload or {})
        return event

    def check_permission(self, role, action):
        allowed = True
        reason = "allowed"
        if self.policy_engine:
            result = self.policy_engine.evaluate(role, action)
            allowed = result.get("allowed", False)
            reason = result.get("reason", "policy")
        self.emit("permission.check", {"role": role, "action": action, "allowed": allowed, "reason": reason})
        return {"status": "GREEN" if allowed else "DENIED", "allowed": allowed, "reason": reason}

    def health(self):
        return {"status": "GREEN", "component": "security_engine", "events": len(self.events)}
