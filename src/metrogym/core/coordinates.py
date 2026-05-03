from __future__ import annotations

import math
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Literal, TypeAlias

from beartype import beartype

Direction: TypeAlias = Literal["forward", "reverse", "both"]


@beartype
@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __iter__(self) -> Iterator[int]:
        yield self.x
        yield self.y

    def __getitem__(self, index: int) -> int:
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        raise IndexError(index)

    def distance(self, other: object) -> float:
        other_pos = to_position(other)
        return math.hypot(self.x - other_pos.x, self.y - other_pos.y)

    def shifted(self, dx: int, dy: int) -> "Position":
        return Position(self.x + dx, self.y + dy)

    def pygame(self) -> tuple[int, int]:
        return self.x, self.y

    def as_tuple(self) -> tuple[int, int]:
        return self.pygame()


PositionLike: TypeAlias = Position | tuple[int, int]


@beartype
def to_position(point: PositionLike) -> Position:
    if isinstance(point, Position):
        return point
    x, y = point
    return Position(int(x), int(y))


@beartype
def to_positions(points: Sequence[PositionLike]) -> list[Position]:
    return [to_position(point) for point in points]
