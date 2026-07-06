class HealthMonitor:
    """Central health aggregation for AIDRAX OS core runtime."""

    def __init__(self):
        self.components = {}

    def register(self, name, status="GREEN", details=None):
        self.components[name] = {
            "status": status,
            "details": details or {}
        }
        return self.components[name]

    def set_status(self, name, status, details=None):
        if name not in self.components:
            return self.register(name, status, details)
        self.components[name]["status"] = status
        if details is not None:
            self.components[name]["details"] = details
        return self.components[name]

    def report(self):
        states = [item["status"] for item in self.components.values()]
        overall = "GREEN" if states and all(state == "GREEN" for state in states) else "YELLOW"
        if any(state == "RED" for state in states):
            overall = "RED"
        return {
            "status": overall,
            "component_count": len(self.components),
            "components": self.components
        }
