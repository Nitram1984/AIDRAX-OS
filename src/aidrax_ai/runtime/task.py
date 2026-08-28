from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass(slots=True)
class RuntimeTask:
    capability: str
    payload: dict
    id: str = field(default_factory=lambda: str(uuid4()))
    created: datetime = field(default_factory=datetime.utcnow)
