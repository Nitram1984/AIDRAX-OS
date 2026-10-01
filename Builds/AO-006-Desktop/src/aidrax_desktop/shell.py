"""Desktop state projection without host-control authority."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Protocol
from uuid import uuid4

class DesktopState(str, Enum):
    LOCKED = "LOCKED"
    READY = "READY"

class OwnerGate(Protocol):
    def approved(self, control: str, principal_id: str) -> bool:
        """Return the canonical owner decision for a desktop control."""
        ...

@dataclass(frozen=True, slots=True)
class DesktopControlProposal:
    """Audit data for a request; it never executes the control."""
    proposal_id: str
    control: str
    principal_id: str
    status: str

class DesktopShell:
    """Expose local shell state while retaining AIDRAX execution authority."""
    _CONTROLS = frozenset({"SESSION", "RESTART", "POWER"})
    def __init__(self, owner_gate: OwnerGate | None = None) -> None:
        """Create a locked shell with an optional canonical Owner Gate."""
        self._owner_gate = owner_gate
        self._state = DesktopState.LOCKED
        self._principal_id: str | None = None
    def state(self) -> DesktopState:
        """Return the current local presentation state."""
        return self._state
    def unlock(self, principal_id: str) -> DesktopState:
        """Accept a pre-authenticated principal; do not authenticate locally."""
        self._validate_principal(principal_id)
        self._principal_id, self._state = principal_id, DesktopState.READY
        return self._state
    def lock(self) -> DesktopState:
        """Clear the local presentation principal without closing external sessions."""
        self._principal_id, self._state = None, DesktopState.LOCKED
        return self._state
    def propose_control(self, control: str) -> DesktopControlProposal:
        """Return a gated proposal and never perform a system action."""
        if self._state is not DesktopState.READY or self._principal_id is None:
            raise PermissionError("desktop must be READY before proposing a control")
        if control not in self._CONTROLS:
            raise ValueError("control must be one of: POWER, RESTART, SESSION")
        approved = self._owner_gate is not None and self._owner_gate.approved(control, self._principal_id)
        return DesktopControlProposal(str(uuid4()), control, self._principal_id, "APPROVED_FOR_DISPATCH" if approved else "PENDING_OWNER")
    @staticmethod
    def _validate_principal(principal_id: str) -> None:
        """Reject blank or oversized local presentation identities."""
        if not isinstance(principal_id, str) or not principal_id.strip(): raise ValueError("principal_id must be a non-empty string")
        if len(principal_id) > 128: raise ValueError("principal_id exceeds 128 characters")
