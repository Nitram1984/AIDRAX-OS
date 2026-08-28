from aidrax_ai.runtime.engine import RuntimeEngine
from aidrax_ai.runtime.health import RuntimeHealth

class RuntimeBootstrap:
    def __init__(self, engine: RuntimeEngine):
        self.engine=engine
        self.health=RuntimeHealth()

    def start(self):
        self.health.set("runtime", True)
        return self.health.summary()
