from __future__ import annotations

"""Public panel primitives for drawing and navigating a MetroGYM scene."""

from collections.abc import Sequence
from dataclasses import dataclass

from beartype import beartype

from metrogym.core.colors import ColorRGBA
from metrogym.core.coordinates import Position, PositionLike, to_position, to_positions
from metrogym.core.ui_modes import UIMode
from metrogym.primitives.signal.runtime import RuntimeTrafficLight
from metrogym.primitives.station.runtime import RuntimeStation
from metrogym.primitives.train.runtime import RuntimeTrain
from metrogym.rendering._utils import gfx


@beartype
@dataclass(frozen=True)
class TrackLine:
    """Represent one drawable runtime track line on the simulation panel.

    Args:
        path (list[Position]):
            Dense path points for the line.
        color (ColorRGBA):
            Display color used by the renderer.
        name (str):
            Human-readable line name.
    """

    path: list[Position]
    color: ColorRGBA
    name: str


@beartype
class SimulationPanel:
    """Manage the drawable state of the visible simulation canvas.

    ``SimulationPanel`` stores runtime objects, stations, track lines, and the
    current camera transform. Most users interact with it indirectly through
    :class:`metrogym.MetroSystem`, but it remains public for advanced rendering
    and teaching scenarios.

    Args:
        size (PositionLike, default=(700, 520)):
            Logical panel size before renderer scaling.
        render_scale (int | float, default=2.0):
            Base render scale used to compute the window size.

    Attributes:
        size (Position):
            Logical panel size.
        render_scale (float):
            Base render scale.
        window_size (Position):
            Actual scaled window size.
        view_scale (float):
            Zoom factor applied to the panel.
        view_offset (Position):
            Camera pan offset.
        objects (list[RuntimeTrain | RuntimeTrafficLight]):
            Runtime objects updated and drawn each tick.
        stations (list[RuntimeStation]):
            Runtime stations drawn on the panel.
        track_lines (list[TrackLine]):
            Drawable track lines.
        tick_count (int):
            Number of ticks elapsed on the panel.
    """

    @beartype
    def __init__(self, size: PositionLike = (700, 520), render_scale: int | float = 2.0):
        self.size = to_position(size)
        self.render_scale = float(render_scale)
        self.window_size = Position(gfx.scale_value(self.size.x, self.render_scale), gfx.scale_value(self.size.y, self.render_scale))
        self.view_scale = 1.0
        self.view_offset = Position(0, 0)
        self.objects: list[RuntimeTrain | RuntimeTrafficLight] = []
        self.stations: list[RuntimeStation] = []
        self.track_lines: list[TrackLine] = []
        self.tick_count = 0

    @beartype
    def add_track_line(self, waypoints: Sequence[PositionLike], color: ColorRGBA, name: str) -> None:
        """Register a line for drawing on the panel.

        Args:
            waypoints (Sequence[PositionLike]):
                Line path points.
            color (ColorRGBA):
                Display color.
            name (str):
                Display name.
        """
        self.track_lines.append(TrackLine(to_positions(waypoints), color, name))

    @beartype
    def addTrackLine(self, waypoints: Sequence[PositionLike], color: ColorRGBA, name: str) -> None:
        """Backward-style alias for :meth:`add_track_line`."""
        self.add_track_line(waypoints, color, name)

    @beartype
    def add_object(self, obj: RuntimeTrain | RuntimeTrafficLight) -> None:
        """Register a runtime object for updates and drawing.

        Args:
            obj (RuntimeTrain | RuntimeTrafficLight):
                Runtime object to add.
        """
        self.objects.append(obj)

    @beartype
    def remove_object(self, obj: RuntimeTrain | RuntimeTrafficLight) -> None:
        """Remove a runtime object if present.

        Args:
            obj (RuntimeTrain | RuntimeTrafficLight):
                Runtime object to remove.
        """
        if obj in self.objects:
            self.objects.remove(obj)

    @beartype
    def addObject(self, obj: RuntimeTrain | RuntimeTrafficLight) -> None:
        """Backward-style alias for :meth:`add_object`."""
        self.add_object(obj)

    @beartype
    def add_station(self, station: RuntimeStation) -> None:
        """Register a runtime station for drawing.

        Args:
            station (RuntimeStation):
                Runtime station to add.
        """
        self.stations.append(station)

    @beartype
    def addStation(self, station: RuntimeStation) -> None:
        """Backward-style alias for :meth:`add_station`."""
        self.add_station(station)

    def tick(self) -> None:
        """Advance the panel by one tick.

        Signals are updated before trains so that train movement observes the
        latest signal state for the current tick.
        """
        self.tick_count += 1
        for obj in self.objects:
            if isinstance(obj, RuntimeTrafficLight):
                obj.update()
        for obj in self.objects:
            if isinstance(obj, RuntimeTrain):
                obj.update()

    def reset(self) -> None:
        """Reset tick count, camera state, and runtime objects."""
        self.tick_count = 0
        self.view_scale = 1.0
        self.view_offset = Position(0, 0)
        for obj in self.objects:
            obj.reset()

    @beartype
    def draw(self, surface: object, renderer: object, *, ui_mode: UIMode = "minimal") -> None:
        """Delegate drawing to the active renderer.

        Args:
            surface (object):
                Target pygame surface.
            renderer (object):
                Renderer exposing ``draw_panel``.
            ui_mode (UIMode, default="minimal"):
                UI mode to render.
        """
        renderer.draw_panel(surface, self, ui_mode=ui_mode)

    def pan(self, dx: int, dy: int) -> None:
        """Pan the camera by a pixel delta.

        Args:
            dx (int):
                Horizontal pan delta.
            dy (int):
                Vertical pan delta.
        """
        self.view_offset = self.view_offset.shifted(dx, dy)

    def zoom(self, factor: float) -> None:
        """Zoom the camera while keeping it within supported bounds.

        Args:
            factor (float):
                Multiplicative zoom factor.
        """
        self.view_scale = max(0.5, min(3.0, self.view_scale * factor))
