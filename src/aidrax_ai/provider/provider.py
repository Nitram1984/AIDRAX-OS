from abc import ABC, abstractmethod

class Provider(ABC):
    @abstractmethod
    def name(self)->str: ...

    @abstractmethod
    def capabilities(self)->tuple[str,...]: ...

    @abstractmethod
    def execute(self, capability:str, payload:dict):
        ...
