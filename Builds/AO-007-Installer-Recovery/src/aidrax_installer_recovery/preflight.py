"""No-write installer and recovery preflight boundary."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

class OwnerGate(Protocol):
    def approved(self, target: str, serial: str) -> bool:
        """Return a current owner decision bound to the exact target identity."""
        ...

@dataclass(frozen=True, slots=True)
class TargetSpec:
    device: str
    model: str
    serial: str
    backup_reference: str
    rollback_reference: str

@dataclass(frozen=True, slots=True)
class PreflightResult:
    status: str
    reasons: tuple[str, ...]

class InstallerPreflight:
    """Assess supplied evidence without discovering or modifying host storage."""
    def __init__(self, owner_gate: OwnerGate | None = None) -> None:
        """Bind the optional current Owner-Gate decision source."""
        self._owner_gate = owner_gate
    def assess(self, target: TargetSpec) -> PreflightResult:
        """Return READY only when exact identity, backup, rollback and gate agree."""
        reasons = []
        if not target.device.startswith("/dev/") or target.device.count("/") != 2: reasons.append("exact_device_required")
        for label, value in (("model", target.model), ("serial", target.serial), ("verified_backup", target.backup_reference), ("rollback", target.rollback_reference)):
            if not isinstance(value, str) or not value.strip(): reasons.append(f"{label}_required")
        if not reasons and (self._owner_gate is None or not self._owner_gate.approved(target.device, target.serial)):
            reasons.append("owner_gate_required")
        return PreflightResult("READY" if not reasons else "BLOCKED", tuple(reasons))
