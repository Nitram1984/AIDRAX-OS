"""Local-only runtime with explicit adapters for canonical AIDRAX authorities."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

from .domain import IdentityPolicy, Principal


class RegistryAdapter(Protocol):
    def add(self, component: dict[str, object]) -> None: ...


class EventBusAdapter(Protocol):
    def publish(self, event: str, payload: dict[str, object]) -> None: ...


class IdentityRuntimeError(PermissionError):
    """Raised when a local principal is not authorised for an action."""


@dataclass(frozen=True, slots=True)
class Session:
    session_id: str
    principal_id: str
    issued_at: str

    def audit_record(self) -> dict[str, str]:
        return {"session_id": self.session_id, "principal_id": self.principal_id, "issued_at": self.issued_at}


class IdentityRuntime:
    """Authorize explicit local actions; never authenticate external accounts."""

    COMPONENT_ID = "aidrax.identity.runtime"

    def __init__(self, registry: RegistryAdapter, events: EventBusAdapter) -> None:
        self._registry, self._events = registry, events
        self._principals: dict[str, Principal] = {}
        self._policies: dict[str, IdentityPolicy] = {}
        self._sessions: dict[str, Session] = {}

    def start(self) -> None:
        self._registry.add({"id": self.COMPONENT_ID, "status": "READY", "health": "HEALTHY"})
        self._emit("identity.runtime_ready", {"component_id": self.COMPONENT_ID})

    def register_principal(self, principal: Principal) -> None:
        if principal.principal_id in self._principals:
            raise ValueError(f"duplicate principal: {principal.principal_id}")
        self._principals[principal.principal_id] = principal
        self._emit("identity.principal_registered", principal.audit_record())

    def register_policy(self, policy: IdentityPolicy) -> None:
        if policy.action in self._policies:
            raise ValueError(f"duplicate action policy: {policy.action}")
        self._policies[policy.action] = policy

    def open_session(self, principal_id: str) -> Session:
        principal = self._principal(principal_id)
        session = Session(str(uuid4()), principal.principal_id, datetime.now(timezone.utc).isoformat())
        self._sessions[session.session_id] = session
        self._emit("identity.session_opened", session.audit_record())
        return session

    def authorize(self, session_id: str, action: str) -> Principal:
        session = self._sessions.get(session_id)
        if session is None:
            raise IdentityRuntimeError("unknown or closed session")
        policy = self._policies.get(action)
        if policy is None:
            raise IdentityRuntimeError(f"no policy for action: {action}")
        principal = self._principal(session.principal_id)
        if not policy.permits(principal):
            self._emit("identity.authorization_denied", {"action": action, **principal.audit_record()})
            raise IdentityRuntimeError(f"principal is not allowed: {action}")
        self._emit("identity.authorization_granted", {"action": action, **principal.audit_record()})
        return principal

    def close_session(self, session_id: str) -> None:
        session = self._sessions.pop(session_id, None)
        if session is None:
            raise IdentityRuntimeError("unknown or closed session")
        self._emit("identity.session_closed", session.audit_record())

    def _principal(self, principal_id: str) -> Principal:
        try: return self._principals[principal_id]
        except KeyError as error: raise IdentityRuntimeError(f"unknown principal: {principal_id}") from error

    def _emit(self, event: str, payload: dict[str, object]) -> None:
        self._events.publish(event, payload)
