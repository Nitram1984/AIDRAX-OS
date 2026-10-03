from dataclasses import dataclass, field
from datetime import UTC, datetime

@dataclass(slots=True)
class Message:
    role:str
    content:str
    created:datetime=field(default_factory=lambda: datetime.now(UTC))
