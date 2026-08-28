class DecisionRouter:
    def __init__(self, capability_manager):
        self.capability_manager=capability_manager

    def dispatch(self, capability, payload):
        return self.capability_manager.execute(capability,payload)
