from __future__ import annotations

from collections.abc import Callable

from griip_debug_assessment.grasp_generation_service import GraspGenerationService
from griip_debug_assessment.mocks import MockCamera, MockRobot
from griip_debug_assessment.models import CycleResult, Grasp
from griip_debug_assessment.pick_queue import PickQueue


class PickingManager:
    def __init__(
        self,
        robot: MockRobot,
        camera: MockCamera,
        grasp_generation_service: GraspGenerationService,
        queue: PickQueue,
        grasp_timeout_seconds: float,
        log: Callable[[str], None] | None = None,
    ) -> None:
        self._robot = robot
        self._camera = camera
        self._grasp_generation_service = grasp_generation_service
        self._queue = queue
        self._grasp_timeout_seconds = grasp_timeout_seconds
        self._log = log

    def run_cycle(self, cycle_number: int | None = None) -> CycleResult:
        cycle_label = f"cycle {cycle_number}" if cycle_number is not None else "cycle"
        self._emit(f"manager: starting {cycle_label}")
        self._robot.go_to_image_capture_location()
        image = self._camera.capture()
        self._emit(f"manager: captured image {image.image_id}; starting grasp generation")
        self._grasp_generation_service.start_generation(image=image, queue=self._queue)

        self._emit(f"manager: waiting for grasp for image {image.image_id}")
        grasp = self._execute_next_available_grasp(image_id=image.image_id)

        self._emit("manager: clearing pick queue")
        self._queue.clear()
        self._emit(f"manager: finished {cycle_label} for image {image.image_id}")

        return CycleResult(image=image, executed_grasp=grasp)

    def run(self, cycle_count: int) -> tuple[CycleResult, ...]:
        return tuple(self.run_cycle(cycle_number=cycle_number) for cycle_number in range(1, cycle_count + 1))

    def shutdown(self, join_timeout_seconds: float | None) -> None:
        self._grasp_generation_service.join_all(timeout_seconds=join_timeout_seconds)

    def _execute_next_available_grasp(self, image_id: int) -> Grasp | None:
        grasp = self._queue.wait_for_grasp(timeout_seconds=self._grasp_timeout_seconds)

        if grasp is None:
            self._emit(f"manager: no grasp ready for image {image_id}")
            return None

        self._emit(f"manager: received grasp {grasp.grasp_id} from image {grasp.image_id}")

        if not self._robot.execute_pick(grasp):
            self._emit(f"manager: grasp {grasp.grasp_id} failed; waiting for another grasp")
            return self._execute_next_available_grasp(image_id=image_id)

        self._robot.place_object(grasp)
        return grasp

    def _emit(self, message: str) -> None:
        if self._log is not None:
            self._log(message)
