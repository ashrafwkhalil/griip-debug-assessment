from __future__ import annotations

import threading
import time
from collections.abc import Callable

from griip_debug_assessment.models import Grasp, Image


class MockRobot:
    def __init__(self, motion_delay_seconds: float, log: Callable[[str], None] | None = None) -> None:
        self._motion_delay_seconds = motion_delay_seconds
        self._log = log
        self._lock = threading.Lock()
        self._executed_grasps: list[Grasp] = []
        self.image_capture_moves = 0

    def go_to_image_capture_location(self) -> None:
        self._emit(f"robot: moving to image capture location ({self._motion_delay_seconds:.3f}s)")
        time.sleep(self._motion_delay_seconds)

        with self._lock:
            self.image_capture_moves += 1
            move_count = self.image_capture_moves

        self._emit(f"robot: reached image capture location (move {move_count})")

    def execute_pick(self, grasp: Grasp) -> None:
        self._emit(
            f"robot: executing grasp {grasp.grasp_id} from image {grasp.image_id} ({self._motion_delay_seconds:.3f}s)"
        )
        time.sleep(self._motion_delay_seconds)

        with self._lock:
            self._executed_grasps.append(grasp)

        self._emit(f"robot: finished grasp {grasp.grasp_id} from image {grasp.image_id}")

    def executed_grasps(self) -> tuple[Grasp, ...]:
        with self._lock:
            return tuple(self._executed_grasps)

    def _emit(self, message: str) -> None:
        if self._log is not None:
            self._log(message)


class MockCamera:
    def __init__(self, capture_delay_seconds: float, log: Callable[[str], None] | None = None) -> None:
        self._capture_delay_seconds = capture_delay_seconds
        self._log = log
        self._lock = threading.Lock()
        self._next_image_id = 1

    def capture(self) -> Image:
        self._emit(f"camera: capturing image ({self._capture_delay_seconds:.3f}s)")
        time.sleep(self._capture_delay_seconds)

        with self._lock:
            image = Image(image_id=self._next_image_id)
            self._next_image_id += 1

        self._emit(f"camera: captured image {image.image_id}")
        return image

    def _emit(self, message: str) -> None:
        if self._log is not None:
            self._log(message)
