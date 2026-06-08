from __future__ import annotations

import time

from griip_debug_assessment.simulation import build_demo_mock_manager


def main() -> None:
    start_time_seconds = time.monotonic()

    def log(message: str) -> None:
        elapsed_seconds = time.monotonic() - start_time_seconds
        print(f"[{elapsed_seconds:6.3f}s] {message}")

    manager, robot, grasp_generation_service, _queue = build_demo_mock_manager(log=log)

    try:
        cycle_results = manager.run(cycle_count=6)
    finally:
        manager.shutdown(join_timeout_seconds=0.1)

    picks_executed = sum(1 for cycle_result in cycle_results if cycle_result.executed_grasp is not None)

    print()
    print(f"cycles run: {len(cycle_results)}")
    print(f"picks executed: {picks_executed}")
    print(f"grasps generated: {grasp_generation_service.generated_grasp_count()}")


if __name__ == "__main__":
    main()
