from .message import Message

class ConversationEngine:
    def __init__(self):
        self._history:list[Message]=[]

    def add(self, role:str, content:str)->Message:
        msg=Message(role=role,content=content)
        self._history.append(msg)
        return msg

    def history(self):
        return tuple(self._history)
