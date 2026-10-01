from dataclasses import dataclass

@dataclass
class Module:

    name: str
    version: str
    author: str

    def initialize(self):
        return True

    def shutdown(self):
        return True
