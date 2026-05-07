from __future__ import annotations

"""Public value object for describing signal-controlled segments."""

from dataclasses import dataclass

from beartype import beartype

from metrogym.core.coordinates import Direction, PositionLike


@beartype
@dataclass(frozen=True)
class ControlRule:
    """Describe one protected line segment for a signal.

    Args:
        line (str):
            Name of the controlled line.
        start (PositionLike):
            First endpoint of the protected segment.
        end (PositionLike):
            Second endpoint of the protected segment.
        direction (Direction, default="both"):
            Travel direction governed by the rule.
    """

    line: str
    start: PositionLike
    end: PositionLike
    direction: Direction = "both"


ControlRuleLike = ControlRule | tuple[str, PositionLike, PositionLike] | tuple[str, PositionLike, PositionLike, Direction]
