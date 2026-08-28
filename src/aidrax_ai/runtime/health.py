class RuntimeHealth:
    def __init__(self):
        self._checks={}
    def set(self,name:str,status:bool):
        self._checks[name]=status
    def summary(self):
        return dict(self._checks)
