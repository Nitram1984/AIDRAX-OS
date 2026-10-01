from .registry import CapabilityRegistry
from .result import CapabilityResult

class CapabilityManager:
    def __init__(self):
        self.registry=CapabilityRegistry()

    def register(self, provider):
        self.registry.register(provider)

    def execute(self, capability, payload):
        p=self.registry.resolve(capability)
        if p is None:
            return CapabilityResult(capability,"",False,error="capability not registered")
        data=p.execute(capability,payload)
        return CapabilityResult(capability,p.name(),True,data=data)
