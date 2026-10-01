"""Immutable identity-domain objects with no provider or credential concept."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

_IDENTITY = re.compile(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$")


class Role(StrEnum):
    OPERATOR = "operator"
    OBSERVER = "observer"
    AUTOMATION = "automation"


@dataclass(frozen=True, slots=True)
class Principal:
    principal_id: str
    display_name: str
    roles: frozenset[Role]

    def __post_init__(self) -> None:
        if not isinstance(self.principal_id, str) or not _IDENTITY.fullmatch(self.principal_id):
            raise ValueError("principal_id must be a lowercase dotted local identifier")
        if not isinstance(self.display_name, str) or not self.display_name.strip():
            raise ValueError("display_name must be non-empty")
        if not self.roles:
            raise ValueError("principal must have at least one role")

    def audit_record(self) -> dict[str, object]:
        return {"principal_id": self.principal_id, "roles": sorted(role.value for role in self.roles)}


@dataclass(frozen=True, slots=True)
class IdentityPolicy:
    action: str
    allowed_roles: frozenset[Role]

    def __post_init__(self) -> None:
        if not isinstance(self.action, str) or not _IDENTITY.fullmatch(self.action):
            raise ValueError("action must be a lowercase dotted identifier")
        if not self.allowed_roles:
            raise ValueError("policy requires at least one allowed role")

    def permits(self, principal: Principal) -> bool:
        return bool(self.allowed_roles & principal.roles)
