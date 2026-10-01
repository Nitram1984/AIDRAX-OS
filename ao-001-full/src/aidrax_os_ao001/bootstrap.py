"""Bootstrap planning without machine mutation or provider access."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class BootstrapState(StrEnum):
    PLANNED = "PLANNED"
    READY_FOR_OWNER_APPROVAL = "READY_FOR_OWNER_APPROVAL"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class BootstrapPlan:
    """Validate an additive target; application is deliberately outside this package."""

    target: Path

    def evaluate(self) -> BootstrapState:
        if not self.target.is_dir():
            return BootstrapState.BLOCKED
        required = ("src/atlas", "src/hermes", "src/aidrax_core")
        if not all((self.target / item).is_dir() for item in required):
            return BootstrapState.BLOCKED
        return BootstrapState.READY_FOR_OWNER_APPROVAL

    def summary(self) -> dict[str, str]:
        state = self.evaluate()
        return {
            "state": state,
            "target": str(self.target),
            "action": "No changes made; use installer/install.sh --apply only after owner approval."
            if state is BootstrapState.READY_FOR_OWNER_APPROVAL
            else "Target is not a recognized AIDRAX OS checkout; no changes made.",
        }
