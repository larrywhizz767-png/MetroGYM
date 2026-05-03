from __future__ import annotations

from metrogym import Color, MetroSystem
from metrogym.primitives import Line, Network, Station, Train


def shuttle(*points: tuple[int, int]) -> list[tuple[int, int]]:
    return [*points, *reversed(points[1:-1]), points[0]]


def build_system(*, tick_ms: int = 350, render_scale: int | float = 2) -> MetroSystem:
    return MetroSystem(name="Basic: Two Line Shuttle", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("East-West", Color.BLUE, shuttle((80, 180), (300, 180), (540, 180))),
            Line("North-South", Color.GREEN, shuttle((300, 80), (300, 180), (300, 380))),
            Station("West", (80, 180)),
            Station("Central", (300, 180), radius=10),
            Station("East", (540, 180)),
            Station("North", (300, 80)),
            Station("South", (300, 380)),
        ]),
        Train("EW", line="East-West", asset="metro_nose"),
        Train("NS", line="North-South", asset="bullet_metro"),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
