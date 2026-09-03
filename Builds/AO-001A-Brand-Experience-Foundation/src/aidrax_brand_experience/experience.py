"""Inert lifecycle-to-presentation mapping; no playback or host action occurs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

_EVENTS = frozenset({"POWER_ON", "BOOT_COMPLETE", "LOGIN_READY", "UPDATE_SUCCEEDED", "SHUTDOWN_REQUESTED"})


@dataclass(frozen=True, slots=True)
class ExperienceCue:
    """A presentation request for a future approved adapter, not an execution command."""

    event: str
    scene: str
    status: str = "PENDING_ADAPTER"


class ExperienceEngine:
    """Resolve declared lifecycle events to deterministic, non-executing cues."""

    def __init__(self, event_map: Mapping[str, str]) -> None:
        normalized = dict(event_map)
        if set(normalized) != _EVENTS:
            raise ValueError("experience map must declare exactly the canonical lifecycle events")
        if any(not isinstance(scene, str) or not scene.strip() for scene in normalized.values()):
            raise ValueError("experience scenes must be non-empty strings")
        self._event_map = normalized

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "ExperienceEngine":
        if payload.get("schema_version") != 1:
            raise ValueError("experience map schema_version must be 1")
        events = payload.get("events")
        if not isinstance(events, dict):
            raise ValueError("experience map events must be an object")
        return cls(events)

    def cue_for(self, event: str) -> ExperienceCue:
        if event not in self._event_map:
            raise ValueError("event is not part of the approved experience lifecycle")
        return ExperienceCue(event=event, scene=self._event_map[event])
