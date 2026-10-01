class CapabilityRegistry:
    def __init__(self):
        self._providers={}

    def register(self, provider):
        for c in provider.capabilities():
            self._providers[c]=provider

    def resolve(self, capability):
        return self._providers.get(capability)
