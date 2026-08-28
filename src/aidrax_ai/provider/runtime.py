class ProviderRuntime:
    def __init__(self):
        self._providers=[]

    def add(self, provider):
        self._providers.append(provider)

    def providers(self):
        return tuple(self._providers)
