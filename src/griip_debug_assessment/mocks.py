from __future__ import annotations

import threading
import time
from collections.abc import Callable

from griip_debug_assessment.models import Grasp, Image


class MockRobot:
    def __init__(
        self,
        motion_delay_seconds: float,
        pick_failure_frequency: int | None = None,
        log: Callable[[str], None] | None = None,
    ) -> None:
        self._motion_delay_seconds = motion_delay_seconds
        self._pick_failure_frequency = (
            pick_failure_frequency if pick_failure_frequency is not None and pick_failure_frequency > 0 else None
        )
        self._log = log
        self._lock = threading.Lock()
        self._executed_grasps: list[Grasp] = []
        self._failed_grasps: list[Grasp] = []
        self._placed_grasps: list[Grasp] = []
        self._pick_attempt_count = 0
        self.image_capture_moves = 0

    def go_to_image_capture_location(self) -> None:
        self._emit(f"robot: moving to image capture location ({self._motion_delay_seconds:.3f}s)")
        time.sleep(self._motion_delay_seconds)

        with self._lock:
            self.image_capture_moves += 1
            move_count = self.image_capture_moves

        self._emit(f"robot: reached image capture location (move {move_count})")

    def execute_pick(self, grasp: Grasp) -> bool:
        self._emit(
            f"robot: executing grasp {grasp.grasp_id} from image {grasp.image_id} ({self._motion_delay_seconds:.3f}s)"
        )
        time.sleep(self._motion_delay_seconds)

        with self._lock:
            self._pick_attempt_count += 1
            pick_attempt_count = self._pick_attempt_count
            pick_failed = (
                self._pick_failure_frequency is not None
                and pick_attempt_count % self._pick_failure_frequency == 0
            )

        if pick_failed:
            with self._lock:
                self._failed_grasps.append(grasp)

            self._emit(f"robot: failed grasp {grasp.grasp_id} from image {grasp.image_id}")
            return False

        with self._lock:
            self._executed_grasps.append(grasp)

        self._emit(f"robot: finished grasp {grasp.grasp_id} from image {grasp.image_id}")
        return True

    def place_object(self, grasp: Grasp) -> None:
        self._emit(
            f"robot: placing object from grasp {grasp.grasp_id} "
            f"from image {grasp.image_id} ({self._motion_delay_seconds:.3f}s)"
        )
        time.sleep(self._motion_delay_seconds)

        with self._lock:
            self._placed_grasps.append(grasp)

        self._emit(f"robot: finished placing object from grasp {grasp.grasp_id}")

    def executed_grasps(self) -> tuple[Grasp, ...]:
        with self._lock:
            return tuple(self._executed_grasps)

    def failed_grasps(self) -> tuple[Grasp, ...]:
        with self._lock:
            return tuple(self._failed_grasps)

    def placed_grasps(self) -> tuple[Grasp, ...]:
        with self._lock:
            return tuple(self._placed_grasps)

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


class MockImageProcessor:
    def __init__(self, processing_delay_seconds: float, log: Callable[[str], None] | None = None) -> None:
        self._processing_delay_seconds = processing_delay_seconds
        self._log = log

    def process_image_and_generate_grasp(self, image: Image, grasp_id: int, grasp_index: int) -> Grasp:
        self._emit(
            f"image processor: processing image {image.image_id} for grasp {grasp_id} "
            f"({self._processing_delay_seconds:.3f}s)"
        )
        time.sleep(self._processing_delay_seconds)

        return Grasp(
            grasp_id=grasp_id,
            image_id=image.image_id,
            score=1.0 - (grasp_index * 0.01),
        )

    def _emit(self, message: str) -> None:
        if self._log is not None:
            self._log(message)
