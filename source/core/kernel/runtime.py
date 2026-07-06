import sys
from pathlib import Path

CORE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CORE_ROOT / "services"))
sys.path.insert(0, str(CORE_ROOT / "registry"))
sys.path.insert(0, str(CORE_ROOT / "events"))
sys.path.insert(0, str(CORE_ROOT / "config"))
sys.path.insert(0, str(CORE_ROOT / "logging"))
sys.path.insert(0, str(CORE_ROOT / "kernel"))

from service_manager import ServiceManager
from module_registry import ModuleRegistry
from event_bus import EventBus
from config_manager import ConfigManager
from logger import AidraxLogger
from health_monitor import HealthMonitor
from runtime_api import RuntimeAPI


class AidraxRuntime:
    def __init__(self):
        self.services = ServiceManager()
        self.modules = ModuleRegistry()
        self.events = EventBus()
        self.config = ConfigManager()
        self.logger = AidraxLogger()
        self.health_monitor = HealthMonitor()
        self.api = RuntimeAPI(self)

    def boot(self):
        self.logger.log("INFO", "AIDRAX Runtime boot started", "runtime")

        self.modules.register("aidrax_core", "0.5.0-build.005", "active")
        self.modules.register("runtime_api", "0.5.0-build.005", "active")
        self.modules.register("health_monitor", "0.5.0-build.005", "active")

        self.services.register("event_bus", self.events)
        self.services.register("module_registry", self.modules)
        self.services.register("config_manager", self.config)
        self.services.register("logger", self.logger)
        self.services.register("health_monitor", self.health_monitor)
        self.services.register("runtime_api", self.api)

        for service_name in [
            "event_bus",
            "module_registry",
            "config_manager",
            "logger",
            "health_monitor",
            "runtime_api",
        ]:
            result = self.services.start(service_name)
            self.health_monitor.register(service_name, result.get("status", "YELLOW"), result)

        self.health_monitor.register("kernel", "GREEN", {"build": "005"})
        self.health_monitor.register("privacy_layer", "GREEN", {"mode": "baseline"})
        self.health_monitor.register("security_layer", "GREEN", {"mode": "baseline"})

        self.events.publish("runtime.boot", {
            "build": "005",
            "status": "GREEN",
            "codename": "Runtime Integration"
        })

        self.logger.log("INFO", "AIDRAX Runtime boot completed", "runtime")
        return self.api.status()

    def health(self):
        return {
            "status": self.health_monitor.report()["status"],
            "runtime": "AIDRAX Core Runtime",
            "build": "005",
            "codename": "Runtime Integration",
            "services": self.services.health(),
            "modules": self.modules.health(),
            "events": self.events.health(),
            "config": self.config.health(),
            "logging": self.logger.health(),
            "health_monitor": self.health_monitor.report(),
            "api": self.api.version()
        }


if __name__ == "__main__":
    runtime = AidraxRuntime()
    print(runtime.boot())
