from __future__ import annotations

from metrogym import Color, MetroSystem
from metrogym.primitives import Line, Network, Station, Train


def build_system(*, tick_ms: int = 400, render_scale: int | float = 2) -> MetroSystem:
    return MetroSystem(name="Basic: Simple Loop", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Loop", Color(80, 200, 255), [(120, 120), (560, 120), (560, 380), (120, 380), (120, 120)]),
            Station("Origin", (120, 120)),
            Station("North", (560, 120)),
            Station("Far Side", (560, 380)),
            Station("West", (120, 380)),
        ]),
        Train("A", line="Loop", asset="metro_nose"),
        Train("B", line="Loop", start_at=50, asset="city_tram"),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
