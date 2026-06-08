# GRIIP Debug Assessment Sandbox

This project is a small, self-contained exercise inspired by a GRIIP pick-and-place flow.

The system is intentionally simplified:

- `MockRobot` simulates robot motion with blocking timed calls.
- `MockCamera` simulates image capture with blocking timed calls.
- `MockImageProcessor` simulates blocking image processing and grasp generation.
- `GraspGenerationService` simulates asynchronous grasp generation in background threads.
- `PickQueue` stores grasps that are ready for execution.
- `PickingManager` coordinates image capture, grasp generation, pick retries, and placement.

The high-level flow is:

1. Move to the image capture location.
2. Capture an image.
3. Start generating grasps for that image.
4. Wait for a grasp to become available.
5. Execute the pick.
6. If the pick fails, wait for another grasp and try again.
7. If the pick succeeds, place the object.
8. Repeat the cycle.

## Setup

Requires Python 3.10+. There are no third-party dependencies.

```bash
git clone https://github.com/ashrafwkhalil/griip-debug-assessment.git
cd griip-debug-assessment
PYTHONPATH=src python -m griip_debug_assessment
```

On Windows (cmd), set the path inline first:

```bat
set PYTHONPATH=src && python -m griip_debug_assessment
```

The demo logs each step of every cycle with timestamps.

Your task is to study how the system behaves across multiple cycles, decide whether it behaves the way it should, and improve it where it does not. Make the smallest reasonable changes and be ready to walk through your reasoning.
