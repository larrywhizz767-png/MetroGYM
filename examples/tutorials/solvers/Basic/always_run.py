from __future__ import annotations

from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train


def build_system(*, tick_ms: int = 400, render_scale: int | float = 2) -> MetroSystem:
    return MetroSystem(name="Solver Basic: Always Run", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Loop", Color.BLUE, [(120, 120), (560, 120), (560, 360), (120, 360), (120, 120)]),
            Station("Origin", (120, 120)),
            Station("North", (560, 120)),
            Station("South", (560, 360)),
            Station("West", (120, 360)),
        ]),
        Train("RUN", line="Loop", solver=train.always_proceed(), asset="metro_nose"),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
