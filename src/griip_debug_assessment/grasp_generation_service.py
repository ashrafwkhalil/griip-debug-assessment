from __future__ import annotations

import itertools
import threading
import time
from collections.abc import Callable

from griip_debug_assessment.models import Grasp, Image
from griip_debug_assessment.pick_queue import PickQueue


class GraspGenerationService:
    def __init__(
        self,
        grasps_per_image: int,
        grasp_delay_seconds: float,
        log: Callable[[str], None] | None = None,
    ) -> None:
        self._grasps_per_image = grasps_per_image
        self._grasp_delay_seconds = grasp_delay_seconds
        self._log = log
        self._grasp_id_counter = itertools.count(start=1)
        self._lock = threading.Lock()
        self._generated_grasp_count = 0
        self._threads: list[threading.Thread] = []

    def start_generation(self, image: Image, queue: PickQueue) -> None:
        self._emit(f"grasp generation: starting thread for image {image.image_id}")
        thread = threading.Thread(
            target=self._generate_grasps,
            args=(image, queue),
            name=f"grasp-generation-image-{image.image_id}",
            daemon=True,
        )

        with self._lock:
            self._threads.append(thread)

        thread.start()

    def generated_grasp_count(self) -> int:
        with self._lock:
            return self._generated_grasp_count

    def join_all(self, timeout_seconds: float | None) -> None:
        with self._lock:
            threads = tuple(self._threads)

        for thread in threads:
            thread.join(timeout=timeout_seconds)

    def _generate_grasps(self, image: Image, queue: PickQueue) -> None:
        for grasp_index in range(self._grasps_per_image):
            time.sleep(self._grasp_delay_seconds)

            grasp = Grasp(
                grasp_id=next(self._grasp_id_counter),
                image_id=image.image_id,
                score=1.0 - (grasp_index * 0.01),
            )
            queue.push(grasp)
            self._emit(f"grasp generation: queued grasp {grasp.grasp_id} from image {image.image_id}")

            with self._lock:
                self._generated_grasp_count += 1

    def _emit(self, message: str) -> None:
        if self._log is not None:
            self._log(message)
