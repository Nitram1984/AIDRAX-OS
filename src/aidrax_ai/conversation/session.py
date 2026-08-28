from .engine import ConversationEngine

class ConversationSession:
    def __init__(self):
        self.engine=ConversationEngine()

    def history(self):
        return self.engine.history()
