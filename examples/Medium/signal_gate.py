from __future__ import annotations

from metrogym import Color, MetroSystem
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train


def build_system(*, tick_ms: int = 320, render_scale: int | float = 2) -> MetroSystem:
    return MetroSystem(name="Medium: Signal Gate", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Branch", Color.PURPLE, [(80, 260), (220, 260), (360, 180), (520, 180), (600, 260), (520, 340), (360, 340), (220, 260), (80, 260)]),
            Station("Depot", (80, 260)),
            Station("Junction", (220, 260), radius=10),
            Station("North Platform", (520, 180)),
            Station("South Platform", (520, 340)),
        ]),
        Train("Local", line="Branch", asset="city_tram"),
        Train("Express", line="Branch", start_at=50, asset="bullet_metro"),
        Signal(
            "Gate-North",
            (360, 165),
            initial_green=True,
            period_ticks=5,
            label="North Gate",
            controls=ControlRule("Branch", (220, 260), (360, 180), "forward"),
        ),
        Signal(
            "Gate-South",
            (360, 360),
            initial_green=False,
            period_ticks=5,
            label="South Gate",
            controls=ControlRule("Branch", (520, 340), (360, 340), "forward"),
        ),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
