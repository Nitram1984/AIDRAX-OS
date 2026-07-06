class ConfigManager:
    def __init__(self):
        self.config = {
            "project": "AIDRAX OS",
            "ring": "Development",
            "host": "AIDRAX-Backup"
        }

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        return {"status": "GREEN", "key": key, "value": value}

    def all(self):
        return self.config

    def health(self):
        return {
            "status": "GREEN",
            "config_keys": list(self.config.keys())
        }
