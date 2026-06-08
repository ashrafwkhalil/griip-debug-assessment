from __future__ import annotations

import threading
import time
from collections import deque

from griip_debug_assessment.models import Grasp


class PickQueue:
    def __init__(self) -> None:
        self._condition = threading.Condition()
        self._grasps: deque[Grasp] = deque()

    def clear(self) -> None:
        with self._condition:
            self._grasps.clear()
            self._condition.notify_all()

    def push(self, grasp: Grasp) -> None:
        with self._condition:
            self._grasps.append(grasp)
            self._condition.notify()

    def wait_for_grasp(self, timeout_seconds: float) -> Grasp | None:
        deadline_seconds = time.monotonic() + timeout_seconds

        with self._condition:
            while not self._grasps:
                remaining_seconds = deadline_seconds - time.monotonic()

                if remaining_seconds <= 0:
                    return None

                self._condition.wait(timeout=remaining_seconds)

            return self._grasps.popleft()

    def pending_grasps(self) -> tuple[Grasp, ...]:
        with self._condition:
            return tuple(self._grasps)
