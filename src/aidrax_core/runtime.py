from typing import Dict

class Runtime:

    def __init__(self):
        self.modules: Dict[str, object] = {}
        self.running = False

    def register(self, name: str, module):
        if name in self.modules:
            raise ValueError(f"Module '{name}' already registered.")
        self.modules[name] = module

    def unregister(self, name: str):
        self.modules.pop(name, None)

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def status(self):
        return {
            "running": self.running,
            "modules": list(self.modules.keys())
        }
