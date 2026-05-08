from __future__ import annotations

"""Public coordinate and direction helpers for MetroGYM worlds."""

import math
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Literal, TypeAlias

from beartype import beartype

Direction: TypeAlias = Literal["forward", "reverse", "both"]


@beartype
@dataclass(frozen=True)
class Position:
    """Represent a 2D integer position in simulation space.

    Args:
        x (int):
            Horizontal coordinate.
        y (int):
            Vertical coordinate.

    Examples:
        !!! example "Create a point"

            ```python
            from metrogym import Position

            point = Position(120, 240)
            ```
    """

    x: int
    y: int

    def __iter__(self) -> Iterator[int]:
        """Iterate over ``x`` and ``y`` in order."""
        yield self.x
        yield self.y

    def __getitem__(self, index: int) -> int:
        """Expose tuple-like indexing.

        Args:
            index (int):
                Coordinate index. ``0`` returns ``x`` and ``1`` returns ``y``.

        Returns:
            int:
                Requested coordinate value.

        Raises:
            IndexError:
                If the index is not ``0`` or ``1``.
        """
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        raise IndexError(index)

    def distance(self, other: object) -> float:
        """Measure Euclidean distance to another point-like value.

        Args:
            other (object):
                Another position-like value accepted by ``to_position()``.

        Returns:
            float:
                Straight-line distance between the two points.
        """
        other_pos = to_position(other)
        return math.hypot(self.x - other_pos.x, self.y - other_pos.y)

    def shifted(self, dx: int, dy: int) -> "Position":
        """Return a shifted copy of the position.

        Args:
            dx (int):
                Horizontal delta.
            dy (int):
                Vertical delta.

        Returns:
            Position:
                Shifted position.
        """
        return Position(self.x + dx, self.y + dy)

    def pygame(self) -> tuple[int, int]:
        """Convert the position to a pygame-friendly tuple.

        Returns:
            tuple[int, int]:
                ``(x, y)``.
        """
        return self.x, self.y

    def as_tuple(self) -> tuple[int, int]:
        """Return the position as a plain tuple.

        Returns:
            tuple[int, int]:
                ``(x, y)``.
        """
        return self.pygame()


PositionLike: TypeAlias = Position | tuple[int, int]


@beartype
def to_position(point: PositionLike) -> Position:
    """Normalise a point-like value to ``Position``.

    Args:
        point (PositionLike):
            Existing ``Position`` or ``(x, y)`` tuple.

    Returns:
        Position:
            Normalised position object.
    """
    if isinstance(point, Position):
        return point
    x, y = point
    return Position(int(x), int(y))


@beartype
def to_positions(points: Sequence[PositionLike]) -> list[Position]:
    """Normalise a sequence of points.

    Args:
        points (Sequence[PositionLike]):
            Sequence of position-like values.

    Returns:
        list[Position]:
            List of normalised positions.
    """
    return [to_position(point) for point in points]
