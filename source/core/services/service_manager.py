class ServiceManager:
    def __init__(self):
        self.services = {}

    def register(self, name, service):
        self.services[name] = {
            "service": service,
            "status": "registered"
        }

    def start(self, name):
        if name not in self.services:
            return {"status": "ERROR", "message": f"Service not found: {name}"}

        self.services[name]["status"] = "running"
        return {"status": "GREEN", "service": name, "state": "running"}

    def stop(self, name):
        if name not in self.services:
            return {"status": "ERROR", "message": f"Service not found: {name}"}

        self.services[name]["status"] = "stopped"
        return {"status": "GREEN", "service": name, "state": "stopped"}

    def health(self):
        return {
            "status": "GREEN",
            "services": {
                name: data["status"] for name, data in self.services.items()
            }
        }
