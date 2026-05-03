from __future__ import annotations

from beartype import beartype

from metrogym.core.coordinates import PositionLike
from metrogym.templates.primitive import BaseMetroPrimitive


@beartype
class Station(BaseMetroPrimitive):
    primitive_group = "network"
    network_only = True

    @beartype
    def __init__(self, name: str, position: PositionLike, radius: int = 7):
        self.name = name
        self.position = position
        self.radius = radius

    @beartype
    def transform(self, context: object) -> object:
        if self.name in context.station_names:
            raise ValueError(f"Duplicate station name: {self.name}")
        context.simulator.add_station(self.name, self.position, self.radius)
        context.station_names.add(self.name)
        return context
