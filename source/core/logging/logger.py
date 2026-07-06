from datetime import datetime

class AidraxLogger:
    def __init__(self):
        self.entries = []

    def log(self, level, message, component="core"):
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "component": component,
            "message": message
        }
        self.entries.append(entry)
        return entry

    def list_entries(self):
        return self.entries

    def health(self):
        return {
            "status": "GREEN",
            "entries": len(self.entries)
        }
