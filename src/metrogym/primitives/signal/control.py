from __future__ import annotations

from beartype import beartype

from metrogym.core.coordinates import Position


@beartype
def on_segment(point: Position, start: Position, end: Position, tolerance: float = 1.5) -> bool:
    segment_length = start.distance(end)
    if segment_length == 0:
        return point.distance(start) <= tolerance
    return abs((point.distance(start) + point.distance(end)) - segment_length) <= tolerance


@beartype
def same_position(a: Position, b: Position, tolerance: float = 1.5) -> bool:
    return a.distance(b) <= tolerance


@beartype
def is_entering_segment(start: Position, end: Position, current: Position, next_position: Position) -> bool:
    next_on_segment = on_segment(next_position, start, end)
    if not next_on_segment:
        return False
    current_on_segment = on_segment(current, start, end)
    if not current_on_segment:
        return True
    return same_position(current, start) and not same_position(next_position, start)


@beartype
def path_contains(path: list[object], point: object, tolerance: float = 1.5) -> bool:
    return any(candidate.distance(point) <= tolerance for candidate in path)
