from __future__ import annotations

from dataclasses import dataclass

from beartype import beartype

from metrogym.core.coordinates import Direction, PositionLike


@beartype
@dataclass(frozen=True)
class ControlRule:
    line: str
    start: PositionLike
    end: PositionLike
    direction: Direction = "both"


ControlRuleLike = ControlRule | tuple[str, PositionLike, PositionLike] | tuple[str, PositionLike, PositionLike, Direction]
