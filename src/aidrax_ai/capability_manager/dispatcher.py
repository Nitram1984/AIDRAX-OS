from .manager import CapabilityManager

class CapabilityDispatcher:
    def __init__(self, manager: CapabilityManager):
        self.manager=manager

    def dispatch(self, capability:str, payload:dict):
        return self.manager.execute(capability,payload)
