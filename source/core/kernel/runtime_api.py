class RuntimeAPI:
    """Internal API facade for AIDRAX OS runtime."""

    def __init__(self, runtime):
        self.runtime = runtime

    def status(self):
        return self.runtime.health()

    def version(self):
        return {
            "project": "AIDRAX OS",
            "build": "005",
            "codename": "Runtime Integration",
            "runtime": "AIDRAX Core Runtime"
        }

    def services(self):
        return self.runtime.services.health()

    def modules(self):
        return self.runtime.modules.list_modules()

    def events(self):
        return self.runtime.events.list_events()
