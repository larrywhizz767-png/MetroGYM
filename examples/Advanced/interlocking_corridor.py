from __future__ import annotations

from metrogym import Color, MetroSystem
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train


def build_system(*, tick_ms: int = 260, render_scale: int | float = 2) -> MetroSystem:
    return MetroSystem(name="Advanced: Interlocking Corridor", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Mainline", Color.RED, [(80, 160), (220, 160), (360, 160), (500, 160), (620, 160), (500, 160), (360, 160), (220, 160), (80, 160)]),
            Line("Airport", Color.BLUE, [(220, 60), (220, 160), (360, 260), (500, 360), (620, 360), (500, 360), (360, 260), (220, 160), (220, 60)]),
            Line("Orbital", Color.PURPLE, [(120, 360), (360, 260), (600, 360), (600, 80), (360, 160), (120, 80), (120, 360)]),
            Station("Terminal W", (80, 160)),
            Station("Junction A", (220, 160), radius=10),
            Station("Junction B", (360, 160), radius=10),
            Station("Junction C", (360, 260), radius=10),
            Station("Terminal E", (620, 160)),
            Station("Airport", (620, 360)),
            Station("North Ring", (600, 80)),
            Station("South Ring", (120, 360)),
        ]),
        Train("MAIN-W", line="Mainline", asset="metro_nose"),
        Train("MAIN-E", line="Mainline", start_at=50, asset="bullet_metro"),
        Train("AIR", line="Airport", asset="city_tram"),
        Train("ORB", line="Orbital", asset="maintenance"),
        Signal("A-Main", (220, 135), initial_green=True, period_ticks=4, label="A-M", controls=ControlRule("Mainline", (220, 160), (360, 160))),
        Signal("B-Main", (360, 135), initial_green=False, period_ticks=4, label="B-M", controls=ControlRule("Mainline", (360, 160), (500, 160))),
        Signal("C-Air", (380, 275), initial_green=True, period_ticks=5, label="C-A", controls=ControlRule("Airport", (360, 260), (500, 360))),
        Signal("Ring-N", (585, 100), initial_green=False, period_ticks=6, label="R-N", controls=ControlRule("Orbital", (600, 80), (360, 160))),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
