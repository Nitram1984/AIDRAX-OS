from __future__ import annotations

from .task import RuntimeTask

class IntelligenceKernel:
    def __init__(self):
        self._queue: list[RuntimeTask] = []

    def submit(self, capability: str, payload: dict) -> RuntimeTask:
        task = RuntimeTask(capability=capability, payload=payload)
        self._queue.append(task)
        return task

    def pending(self) -> int:
        return len(self._queue)
