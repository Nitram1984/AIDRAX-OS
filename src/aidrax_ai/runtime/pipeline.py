from aidrax_ai.conversation.engine import ConversationEngine
from aidrax_ai.decision.router import DecisionRouter

class RuntimePipeline:
    def __init__(self, router: DecisionRouter, conversation: ConversationEngine):
        self.router=router
        self.conversation=conversation

    def process(self, capability:str, payload:dict):
        self.conversation.add("user", str(payload))
        result=self.router.dispatch(capability,payload)
        self.conversation.add("assistant", str(result))
        return result
