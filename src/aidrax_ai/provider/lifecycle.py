class ProviderLifecycle:
    def __init__(self):
        self._state="created"
    @property
    def state(self):
        return self._state
    def initialize(self):
        self._state="ready"
    def shutdown(self):
        self._state="stopped"
