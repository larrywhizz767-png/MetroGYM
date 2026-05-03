from __future__ import annotations

from metrogym import Color, MetroSystem
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train


def build_system(*, tick_ms: int = 300, render_scale: int | float = 2) -> MetroSystem:
    return MetroSystem(
        name="Medium: Collision Lab",
        tick_ms=tick_ms,
        render_scale=render_scale,
        stop_all_on_collision=True,
    ).pipeline([
        Network([
            Line("Protected Loop", Color.RED, [(100, 120), (560, 120), (560, 280), (100, 280), (100, 120)]),
            Line("Service Spur", Color.YELLOW, [(330, 80), (330, 200), (330, 380), (330, 80)]),
            Station("West", (100, 120)),
            Station("East", (560, 120)),
            Station("Crossing", (330, 200), radius=10),
            Station("Yard", (330, 380)),
        ]),
        Train("Loop-A", line="Protected Loop", asset="metro_nose"),
        Train("Loop-B", line="Protected Loop", start_at=50, asset="maintenance"),
        Train("Spur", line="Service Spur", peer_with_line=False, asset="city_tram"),
        Signal(
            "Crossing-Hold",
            (360, 200),
            initial_green=False,
            period_ticks=4,
            label="Hold",
            controls=ControlRule("Protected Loop", (100, 120), (560, 120)),
        ),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
