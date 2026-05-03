from __future__ import annotations

import math
from collections.abc import Sequence

from beartype import beartype

from metrogym.core.constants import PATH_STEP
from metrogym.core.coordinates import Position, PositionLike, to_position


@beartype
def build_path(waypoints: Sequence[PositionLike]) -> list[Position]:
    if len(waypoints) < 2:
        raise ValueError("Need at least two waypoints to build a path.")
    positions = [to_position(point) for point in waypoints]
    points: list[Position] = []
    for start, end in zip(positions, positions[1:]):
        interpolate(points, start, end)
    return points


@beartype
def interpolate(out: list[Position], start: Position, end: Position) -> None:
    dx = end.x - start.x
    dy = end.y - start.y
    dist = math.hypot(dx, dy)
    steps = max(1, int(dist / PATH_STEP))
    for index in range(steps + 1):
        t = index / steps
        out.append(Position(round(start.x + t * dx), round(start.y + t * dy)))
