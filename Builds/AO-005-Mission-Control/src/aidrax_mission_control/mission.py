"""Mission Control status projection without control-plane authority."""
from __future__ import annotations
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Protocol, Sequence
from uuid import uuid4

class RegistryView(Protocol):
    def components(self) -> Sequence[Mapping[str, object]]:
        """Return the current ATLAS component records."""
        ...
class EventView(Protocol):
    def recent_events(self, limit: int) -> Sequence[Mapping[str, object]]:
        """Return no more than the requested redacted HERMES event records."""
        ...
class HealthView(Protocol):
    def health(self) -> Sequence[Mapping[str, object]]:
        """Return the current ARGUS health records."""
        ...
class OwnerGate(Protocol):
    def approved(self, action: str, rationale: str) -> bool:
        """Return the canonical Owner-Gate decision for one proposed action."""
        ...

@dataclass(frozen=True, slots=True)
class MissionSnapshot:
    components: tuple[Mapping[str, object], ...]
    health: tuple[Mapping[str, object], ...]
    events: tuple[Mapping[str, object], ...]

@dataclass(frozen=True, slots=True)
class ActionProposal:
    """An audit record, not permission or an instruction to execute."""
    proposal_id: str
    action: str
    rationale: str
    status: str

class MissionControl:
    """Project evidence and request approval without owning execution."""
    _MAX_EVENT_LIMIT = 100
    _MAX_TEXT_LENGTH = 512
    def __init__(self, registry: RegistryView, events: EventView, health: HealthView, owner_gate: OwnerGate | None = None) -> None:
        """Bind read-only evidence sources and an optional canonical gate."""
        self._registry = registry
        self._event_view = events
        self._health = health
        self._owner_gate = owner_gate
    def snapshot(self, event_limit: int = 20) -> MissionSnapshot:
        """Return immutable copies of source evidence without mutating a source."""
        if isinstance(event_limit, bool) or not isinstance(event_limit, int): raise TypeError("event_limit must be an integer")
        if not 0 <= event_limit <= self._MAX_EVENT_LIMIT: raise ValueError(f"event_limit must be between 0 and {self._MAX_EVENT_LIMIT}")
        return MissionSnapshot(self._records(self._registry.components(), "id"), self._records(self._health.health(), "id"), self._events(self._event_view.recent_events(event_limit)))
    def propose_action(self, action: str, rationale: str) -> ActionProposal:
        """Return a proposal status only; no code path dispatches an action."""
        self._validate_text(action, "action"); self._validate_text(rationale, "rationale")
        approved = self._owner_gate is not None and self._owner_gate.approved(action, rationale)
        return ActionProposal(str(uuid4()), action, rationale, "APPROVED_FOR_DISPATCH" if approved else "PENDING_OWNER")
    @staticmethod
    def _records(records: Sequence[Mapping[str, object]], identifier: str) -> tuple[Mapping[str, object], ...]:
        """Validate, freeze, and order identifier-keyed records."""
        normalized: list[Mapping[str, object]] = []
        for record in records:
            if not isinstance(record, Mapping): raise TypeError("view records must be mappings")
            value = record.get(identifier)
            if not isinstance(value, str) or not value.strip(): raise ValueError(f"view record requires a non-empty {identifier}")
            normalized.append(MappingProxyType(dict(record)))
        return tuple(sorted(normalized, key=lambda record: str(record[identifier])))
    @staticmethod
    def _events(events: Sequence[Mapping[str, object]]) -> tuple[Mapping[str, object], ...]:
        """Validate and freeze ordered event records."""
        normalized: list[Mapping[str, object]] = []
        for event in events:
            if not isinstance(event, Mapping): raise TypeError("events must be mappings")
            name = event.get("event")
            if not isinstance(name, str) or not name.strip(): raise ValueError("event record requires a non-empty event")
            normalized.append(MappingProxyType(dict(event)))
        return tuple(normalized)
    @classmethod
    def _validate_text(cls, value: str, label: str) -> None:
        """Reject empty or oversized proposal metadata."""
        if not isinstance(value, str) or not value.strip(): raise ValueError(f"{label} must be a non-empty string")
        if len(value) > cls._MAX_TEXT_LENGTH: raise ValueError(f"{label} exceeds {cls._MAX_TEXT_LENGTH} characters")
