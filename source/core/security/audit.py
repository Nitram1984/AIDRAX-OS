from datetime import datetime, timezone

class AuditLog:
    def __init__(self):
        self.records = []

    def record(self, category, action, details=None):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "category": category,
            "action": action,
            "details": details or {}
        }
        self.records.append(entry)
        return entry

    def health(self):
        return {"status": "GREEN", "component": "audit_log", "records": len(self.records)}
