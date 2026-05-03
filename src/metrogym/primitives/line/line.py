from __future__ import annotations

from collections.abc import Sequence

from beartype import beartype

from metrogym.core.colors import ColorRGBA
from metrogym.core.coordinates import PositionLike
from metrogym.templates.primitive import BaseMetroPrimitive


@beartype
class Line(BaseMetroPrimitive):
    primitive_group = "network"
    network_only = True

    @beartype
    def __init__(self, name: str, color: ColorRGBA, waypoints: Sequence[PositionLike]):
        self.name = name
        self.color = color
        self.waypoints = list(waypoints)

    @beartype
    def transform(self, context: object) -> object:
        if self.name in context.line_names:
            raise ValueError(f"Duplicate line name: {self.name}")
        context.simulator.add_line(self.name, self.color, self.waypoints)
        context.line_names.add(self.name)
        return context
