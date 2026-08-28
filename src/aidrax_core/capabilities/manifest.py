"""Immutable capability manifest and lifecycle status domain objects."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from aidrax_core.capabilities.contracts import CapabilityHealth, CapabilityState
from aidrax_core.errors import CapabilityManifestError

_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
_CAPABILITY_ID = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_MANIFEST_FIELDS = frozenset(
    {
        "id",
        "name",
        "version",
        "description",
        "author",
        "dependencies",
        "permissions",
        "health",
        "priority",
        "supported_interfaces",
    }
)


@dataclass(frozen=True, order=True, slots=True)
class CapabilityVersion:
    """Strict semantic version used by manifests and dependencies."""

    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: object, field_name: str = "version") -> "CapabilityVersion":
        """Parse a strict semantic version without provider-specific semantics."""
        if not isinstance(value, str):
            raise CapabilityManifestError(f"{field_name} must be a semantic version string")
        match = _SEMVER.fullmatch(value)
        if match is None:
            raise CapabilityManifestError(f"{field_name} must use MAJOR.MINOR.PATCH semantic versioning")
        return cls(*(int(part) for part in match.groups()))

    def __str__(self) -> str:
        """Serialize the version in canonical semantic-version form."""
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True, slots=True)
class CapabilityDependency:
    """Exact required capability version for deterministic P0 resolution."""

    capability_id: str
    version: CapabilityVersion

    @classmethod
    def from_mapping(cls, value: object) -> "CapabilityDependency":
        """Validate one dependency declaration."""
        if not isinstance(value, Mapping) or set(value) != {"id", "version"}:
            raise CapabilityManifestError("each dependency must contain exactly 'id' and 'version'")
        capability_id = _capability_id(value["id"], "dependency id")
        return cls(capability_id=capability_id, version=CapabilityVersion.parse(value["version"], "dependency version"))

    def as_dict(self) -> dict[str, str]:
        """Return the canonical persisted dependency representation."""
        return {"id": self.capability_id, "version": str(self.version)}


@dataclass(frozen=True, slots=True)
class CapabilityManifest:
    """Validated canonical manifest for one internal AIDRAX capability."""

    capability_id: str
    name: str
    version: CapabilityVersion
    description: str
    author: str
    dependencies: tuple[CapabilityDependency, ...]
    permissions: tuple[str, ...]
    health: CapabilityHealth
    priority: int
    supported_interfaces: tuple[str, ...]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "CapabilityManifest":
        """Validate a complete manifest with a closed, deterministic schema."""
        if set(value) != _MANIFEST_FIELDS:
            missing = sorted(_MANIFEST_FIELDS - set(value))
            unexpected = sorted(set(value) - _MANIFEST_FIELDS)
            details = []
            if missing:
                details.append(f"missing fields: {', '.join(missing)}")
            if unexpected:
                details.append(f"unexpected fields: {', '.join(unexpected)}")
            raise CapabilityManifestError(f"capability manifest schema mismatch ({'; '.join(details)})")
        capability_id = _capability_id(value["id"], "id")
        name = _text(value["name"], "name")
        description = _text(value["description"], "description")
        author = _text(value["author"], "author")
        dependencies = _dependencies(value["dependencies"], capability_id)
        permissions = _strings(value["permissions"], "permissions", allow_empty=True)
        interfaces = _strings(value["supported_interfaces"], "supported_interfaces", allow_empty=False)
        priority = value["priority"]
        if isinstance(priority, bool) or not isinstance(priority, int):
            raise CapabilityManifestError("priority must be an integer")
        try:
            health = CapabilityHealth(value["health"])
        except (TypeError, ValueError) as error:
            values = ", ".join(item.value for item in CapabilityHealth)
            raise CapabilityManifestError(f"health must be one of: {values}") from error
        return cls(
            capability_id=capability_id,
            name=name,
            version=CapabilityVersion.parse(value["version"]),
            description=description,
            author=author,
            dependencies=dependencies,
            permissions=permissions,
            health=health,
            priority=priority,
            supported_interfaces=interfaces,
        )

    def as_dict(self) -> dict[str, object]:
        """Return the canonical JSON-compatible manifest representation."""
        return {
            "id": self.capability_id,
            "name": self.name,
            "version": str(self.version),
            "description": self.description,
            "author": self.author,
            "dependencies": [dependency.as_dict() for dependency in self.dependencies],
            "permissions": list(self.permissions),
            "health": self.health.value,
            "priority": self.priority,
            "supported_interfaces": list(self.supported_interfaces),
        }


@dataclass(frozen=True, slots=True)
class CapabilityStatus:
    """Stable status returned by the canonical capability lifecycle owner."""

    capability_id: str
    name: str
    version: CapabilityVersion
    state: CapabilityState
    health: CapabilityHealth
    priority: int
    dependencies: tuple[str, ...]
    permissions: tuple[str, ...]
    updated_at: str

    @classmethod
    def create(cls, manifest: CapabilityManifest, state: CapabilityState, health: CapabilityHealth) -> "CapabilityStatus":
        """Create a status with an explicit UTC timestamp."""
        return cls(
            capability_id=manifest.capability_id,
            name=manifest.name,
            version=manifest.version,
            state=state,
            health=health,
            priority=manifest.priority,
            dependencies=tuple(item.capability_id for item in manifest.dependencies),
            permissions=manifest.permissions,
            updated_at=datetime.now(UTC).isoformat(),
        )

    def as_dict(self) -> dict[str, object]:
        """Return the stable JSON-compatible public status object."""
        return {
            "id": self.capability_id,
            "name": self.name,
            "version": str(self.version),
            "state": self.state.value,
            "health": self.health.value,
            "priority": self.priority,
            "dependencies": list(self.dependencies),
            "permissions": list(self.permissions),
            "updated_at": self.updated_at,
        }


def _capability_id(value: object, field_name: str) -> str:
    """Validate a stable internal capability identifier."""
    if not isinstance(value, str) or _CAPABILITY_ID.fullmatch(value) is None:
        raise CapabilityManifestError(
            f"{field_name} must be a lowercase capability identifier containing letters, digits, '.', '_' or '-'"
        )
    return value


def _text(value: object, field_name: str) -> str:
    """Validate a non-empty descriptive manifest field."""
    if not isinstance(value, str) or not value.strip():
        raise CapabilityManifestError(f"{field_name} must be a non-empty string")
    return value.strip()


def _strings(value: object, field_name: str, *, allow_empty: bool) -> tuple[str, ...]:
    """Validate a deterministic unique string collection."""
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise CapabilityManifestError(f"{field_name} must be an array of strings")
    normalized = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise CapabilityManifestError(f"{field_name} must contain non-empty strings")
        normalized.append(item.strip())
    if not allow_empty and not normalized:
        raise CapabilityManifestError(f"{field_name} must not be empty")
    if len(set(normalized)) != len(normalized):
        raise CapabilityManifestError(f"{field_name} must not contain duplicates")
    return tuple(sorted(normalized))


def _dependencies(value: object, capability_id: str) -> tuple[CapabilityDependency, ...]:
    """Validate sorted, unique, non-self dependency declarations."""
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise CapabilityManifestError("dependencies must be an array")
    dependencies = tuple(sorted((CapabilityDependency.from_mapping(item) for item in value), key=lambda item: item.capability_id))
    identifiers = tuple(item.capability_id for item in dependencies)
    if capability_id in identifiers:
        raise CapabilityManifestError("a capability cannot depend on itself")
    if len(set(identifiers)) != len(identifiers):
        raise CapabilityManifestError("dependencies must not contain duplicate ids")
    return dependencies
