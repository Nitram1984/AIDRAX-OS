from dataclasses import dataclass

@dataclass(slots=True)
class Identity:
    name:str="AIDRAX"
    version:str="0.12.0-alpha"
    profile:str="primary"
