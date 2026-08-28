"""Deterministic in-process platform runtime model for AO-001 integration tests."""

from __future__ import annotations

from enum import StrEnum


class RuntimeState(StrEnum):
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class PlatformRuntime:
    """A state model; it never starts services, threads, providers, or processes."""

    def __init__(self) -> None:
        self._state = RuntimeState.NEW
        self._components: tuple[str, ...] = ()

    @property
    def state(self) -> RuntimeState:
        return self._state

    def prepare(self, components: list[str]) -> None:
        if self._state not in {RuntimeState.NEW, RuntimeState.STOPPED}:
            raise RuntimeError(f"cannot prepare runtime from {self._state}")
        if any(not isinstance(item, str) or not item.strip() for item in components):
            raise ValueError("component names must be non-empty strings")
        if len(set(components)) != len(components):
            raise ValueError("duplicate component names are not allowed")
        self._components = tuple(components)
        self._state = RuntimeState.READY

    def start(self, *, owner_approved: bool) -> None:
        if self._state is not RuntimeState.READY:
            raise RuntimeError(f"cannot start runtime from {self._state}")
        if not owner_approved:
            raise PermissionError("runtime start requires explicit owner approval")
        self._state = RuntimeState.RUNNING

    def stop(self) -> None:
        if self._state is RuntimeState.RUNNING:
            self._state = RuntimeState.STOPPED

    def status(self) -> dict[str, object]:
        return {"state": self._state, "components": list(self._components), "side_effects": False}
