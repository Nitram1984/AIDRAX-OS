import sys
from pathlib import Path

CORE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CORE_ROOT / "services"))
sys.path.insert(0, str(CORE_ROOT / "registry"))
sys.path.insert(0, str(CORE_ROOT / "events"))
sys.path.insert(0, str(CORE_ROOT / "config"))
sys.path.insert(0, str(CORE_ROOT / "logging"))

from service_manager import ServiceManager
from module_registry import ModuleRegistry
from event_bus import EventBus
from config_manager import ConfigManager
from logger import AidraxLogger

class AidraxRuntime:
    def __init__(self):
        self.services = ServiceManager()
        self.modules = ModuleRegistry()
        self.events = EventBus()
        self.config = ConfigManager()
        self.logger = AidraxLogger()

    def boot(self):
        self.logger.log("INFO", "AIDRAX Runtime boot started", "runtime")

        self.modules.register("aidrax_core", "0.4.0-build.004", "active")
        self.services.register("event_bus", self.events)
        self.services.register("module_registry", self.modules)
        self.services.register("config_manager", self.config)
        self.services.register("logger", self.logger)

        self.services.start("event_bus")
        self.services.start("module_registry")
        self.services.start("config_manager")
        self.services.start("logger")

        self.events.publish("runtime.boot", {
            "build": "004",
            "status": "GREEN"
        })

        self.logger.log("INFO", "AIDRAX Runtime boot completed", "runtime")

        return self.health()

    def health(self):
        return {
            "status": "GREEN",
            "runtime": "AIDRAX Core Runtime",
            "services": self.services.health(),
            "modules": self.modules.health(),
            "events": self.events.health(),
            "config": self.config.health(),
            "logging": self.logger.health()
        }

if __name__ == "__main__":
    runtime = AidraxRuntime()
    print(runtime.boot())
