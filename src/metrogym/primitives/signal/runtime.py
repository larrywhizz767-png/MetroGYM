from __future__ import annotations

from beartype import beartype

from metrogym.core.coordinates import PositionLike, to_position


@beartype
class RuntimeTrafficLight:
    @beartype
    def __init__(self, id: str, position: PositionLike, initial_green: bool = True, period_ticks: int = 5, label: str | None = None):
        self.id = id
        self.position = to_position(position)
        self.green = initial_green
        self.period_ticks = max(1, period_ticks)
        self.label = label
        self._initial_green = initial_green
        self._ticks_since_change = 0

    def reset(self) -> None:
        self.green = self._initial_green
        self._ticks_since_change = 0

    @beartype
    def set_state(self, *, green: bool) -> None:
        self.green = green
        self._ticks_since_change = 0

    def update(self) -> None:
        self._ticks_since_change += 1
        if self._ticks_since_change >= self.period_ticks:
            self.green = not self.green
            self._ticks_since_change = 0

    @property
    def ticks_since_change(self) -> int:
        return self._ticks_since_change

    def draw(self, surface: object, *args: object, **kwargs: object) -> None:
        renderer = kwargs.get("renderer")
        if renderer is None:
            raise ValueError("TrafficLight.draw requires renderer=...")
        renderer.draw_traffic_light(surface, self, *args)


TrafficLight = RuntimeTrafficLight
