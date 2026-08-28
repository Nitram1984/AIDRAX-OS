from dataclasses import dataclass
from typing import Any

@dataclass(slots=True)
class CapabilityResult:
    capability:str
    provider:str
    success:bool
    data:Any=None
    error:str|None=None
