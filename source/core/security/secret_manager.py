import os

class SecretManager:
    def __init__(self):
        self.allowed_prefixes = ("AIDRAX_",)

    def get(self, name, default=None):
        if not name.startswith(self.allowed_prefixes):
            return default
        return os.environ.get(name, default)

    def set_runtime_only(self, name, value):
        if not name.startswith(self.allowed_prefixes):
            return {"status": "DENIED", "reason": "secret_prefix_not_allowed"}
        os.environ[name] = value
        return {"status": "GREEN", "scope": "runtime_only", "name": name}

    def health(self):
        return {"status": "GREEN", "component": "secret_manager", "storage": "environment_runtime_only"}
