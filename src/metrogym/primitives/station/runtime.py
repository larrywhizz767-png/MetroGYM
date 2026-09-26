from __future__ import annotations

from dataclasses import dataclass
from beartype import beartype
from metrogym.core.coordinates import Position, PositionLike, to_position


@beartype
@dataclass(frozen=True)
class RuntimeStation:
    name: str
    position: Position
    radius: int = 7
    label: str | None = None

    @beartype
    def __init__(self, name: str, position: PositionLike, radius: int = 7, label: str | None = None):
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "position", to_position(position))
        object.__setattr__(self, "radius", radius)
        object.__setattr__(self, "label", label)
