class LifecycleManager:
    def __init__(self):
        self.state = "initialized"

    def boot(self):
        self.state = "booted"
        return self.state

    def shutdown(self):
        self.state = "shutdown"
        return self.state
