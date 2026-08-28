from collections import deque
from .task import RuntimeTask

class TaskScheduler:
    def __init__(self):
        self._queue = deque()

    def enqueue(self, task: RuntimeTask):
        self._queue.append(task)

    def dequeue(self):
        return self._queue.popleft() if self._queue else None

    def size(self):
        return len(self._queue)
