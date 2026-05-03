from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from beartype import beartype

from metrogym.core.colors import ColorRGBA
from metrogym.core.coordinates import Position, PositionLike, to_position, to_positions
from metrogym.primitives.signal.runtime import RuntimeTrafficLight
from metrogym.primitives.station.runtime import RuntimeStation
from metrogym.primitives.train.runtime import RuntimeTrain
from metrogym.rendering._utils import gfx


@beartype
@dataclass(frozen=True)
class TrackLine:
    path: list[Position]
    color: ColorRGBA
    name: str


@beartype
class SimulationPanel:
    @beartype
    def __init__(self, size: PositionLike = (700, 520), render_scale: int | float = 2.0):
        self.size = to_position(size)
        self.render_scale = float(render_scale)
        self.window_size = Position(gfx.scale_value(self.size.x, self.render_scale), gfx.scale_value(self.size.y, self.render_scale))
        self.objects: list[RuntimeTrain | RuntimeTrafficLight] = []
        self.stations: list[RuntimeStation] = []
        self.track_lines: list[TrackLine] = []
        self.tick_count = 0

    @beartype
    def add_track_line(self, waypoints: Sequence[PositionLike], color: ColorRGBA, name: str) -> None:
        self.track_lines.append(TrackLine(to_positions(waypoints), color, name))

    @beartype
    def addTrackLine(self, waypoints: Sequence[PositionLike], color: ColorRGBA, name: str) -> None:
        self.add_track_line(waypoints, color, name)

    @beartype
    def add_object(self, obj: RuntimeTrain | RuntimeTrafficLight) -> None:
        self.objects.append(obj)

    @beartype
    def addObject(self, obj: RuntimeTrain | RuntimeTrafficLight) -> None:
        self.add_object(obj)

    @beartype
    def add_station(self, station: RuntimeStation) -> None:
        self.stations.append(station)

    @beartype
    def addStation(self, station: RuntimeStation) -> None:
        self.add_station(station)

    def tick(self) -> None:
        self.tick_count += 1
        for obj in self.objects:
            obj.update()

    def reset(self) -> None:
        self.tick_count = 0
        for obj in self.objects:
            obj.reset()

    @beartype
    def draw(self, surface: object, renderer: object) -> None:
        renderer.draw_panel(surface, self)
