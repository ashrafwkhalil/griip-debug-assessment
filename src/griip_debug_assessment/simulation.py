from __future__ import annotations

from collections.abc import Callable

from griip_debug_assessment.grasp_generation_service import GraspGenerationService
from griip_debug_assessment.mocks import MockCamera, MockRobot
from griip_debug_assessment.pick_queue import PickQueue
from griip_debug_assessment.picking_manager import PickingManager


def build_mock_manager(
    motion_delay_seconds: float,
    capture_delay_seconds: float,
    grasps_per_image: int,
    grasp_delay_seconds: float,
    grasp_timeout_seconds: float,
    log: Callable[[str], None] | None = None,
) -> tuple[PickingManager, MockRobot, GraspGenerationService, PickQueue]:
    robot = MockRobot(motion_delay_seconds=motion_delay_seconds, log=log)
    camera = MockCamera(capture_delay_seconds=capture_delay_seconds, log=log)
    grasp_generation_service = GraspGenerationService(
        grasps_per_image=grasps_per_image,
        grasp_delay_seconds=grasp_delay_seconds,
        log=log,
    )
    queue = PickQueue()
    manager = PickingManager(
        robot=robot,
        camera=camera,
        grasp_generation_service=grasp_generation_service,
        queue=queue,
        grasp_timeout_seconds=grasp_timeout_seconds,
        log=log,
    )

    return manager, robot, grasp_generation_service, queue


def build_fast_mock_manager() -> tuple[PickingManager, MockRobot, GraspGenerationService, PickQueue]:
    return build_mock_manager(
        motion_delay_seconds=0.0002,
        capture_delay_seconds=0.0002,
        grasps_per_image=100,
        grasp_delay_seconds=0.0002,
        grasp_timeout_seconds=0.05,
    )


def build_demo_mock_manager(log: Callable[[str], None]) -> tuple[PickingManager, MockRobot, GraspGenerationService, PickQueue]:
    return build_mock_manager(
        motion_delay_seconds=1.4,
        capture_delay_seconds=1.0,
        grasps_per_image=12,
        grasp_delay_seconds=0.8,
        grasp_timeout_seconds=3.0,
        log=log,
    )
