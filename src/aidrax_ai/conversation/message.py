from dataclasses import dataclass, field
from datetime import datetime

@dataclass(slots=True)
class Message:
    role:str
    content:str
    created:datetime=field(default_factory=datetime.utcnow)
