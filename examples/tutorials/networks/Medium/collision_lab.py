from __future__ import annotations

from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train


def build_system(*, tick_ms: int = 300, render_scale: int | float = 2) -> MetroSystem:
    parked = train.always_hold()
    return MetroSystem(name="Network Medium: Straight Collision Lab", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Single Track", Color.RED, [(80, 240), (620, 240), (80, 240)]),
            Station("West Yard", (80, 240)),
            Station("Meeting Point", (350, 240), radius=10),
            Station("East Yard", (620, 240)),
        ]),
        Train("T-1", line="Single Track", start_at=0, solver=parked, asset="metro_nose"),
        Train("T-2", line="Single Track", start_at=18, solver=parked, asset="city_tram"),
        Train("T-3", line="Single Track", start_at=50, solver=parked, asset="bullet_metro"),
        Train("T-4", line="Single Track", start_at=68, solver=parked, asset="maintenance"),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
