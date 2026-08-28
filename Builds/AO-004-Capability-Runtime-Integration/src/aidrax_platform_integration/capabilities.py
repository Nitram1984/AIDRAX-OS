"""Platform composition boundary; lifecycle remains owned by CapabilityRuntime."""
from __future__ import annotations
from typing import Protocol

class CapabilityRuntimeAdapter(Protocol):
    def discover_and_activate(self) -> list[object]: ...
    def shutdown(self) -> list[object]: ...

class CapabilityBootstrap:
    def __init__(self, runtime: CapabilityRuntimeAdapter) -> None:
        self._runtime=runtime; self._started=False; self._snapshot: tuple[object,...]=()
    def start(self) -> tuple[object,...]:
        if self._started: return self._snapshot
        self._snapshot=tuple(self._runtime.discover_and_activate()); self._started=True
        return self._snapshot
    def status(self) -> tuple[object,...]: return self._snapshot
    def stop(self) -> tuple[object,...]:
        if not self._started: return ()
        result=tuple(self._runtime.shutdown()); self._started=False; self._snapshot=()
        return result
