from aidrax_ai.conversation.engine import ConversationEngine
e=ConversationEngine()
e.add("user","hello")
assert len(e.history())==1
print("conversation ok")
