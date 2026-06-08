from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Image:
    image_id: int


@dataclass(frozen=True)
class Grasp:
    grasp_id: int
    image_id: int
    score: float


@dataclass(frozen=True)
class CycleResult:
    image: Image
    executed_grasp: Grasp | None
