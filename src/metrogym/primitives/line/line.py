from __future__ import annotations

from collections.abc import Sequence

from beartype import beartype

from metrogym.core.colors import ColorRGBA
from metrogym.core.coordinates import PositionLike
from metrogym.templates.primitive import BaseMetroPrimitive
from metrogym.validation import validation_registry


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
        registry = validation_registry()
        if self.name in context.line_names:
            registry.raise_issue(registry.primitive_issue("Line", "duplicate_name", path=f"Line[name={self.name}]", name=self.name))
        context.simulator.add_line(self.name, self.color, self.waypoints)
        context.line_names.add(self.name)
        return context
