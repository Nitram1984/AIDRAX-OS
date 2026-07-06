class ModuleRegistry:
    def __init__(self):
        self.modules = {}

    def register(self, name, version="0.0.0", status="registered"):
        self.modules[name] = {
            "version": version,
            "status": status
        }

    def list_modules(self):
        return self.modules

    def health(self):
        return {
            "status": "GREEN",
            "modules": self.modules
        }
