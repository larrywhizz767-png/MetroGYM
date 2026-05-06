from __future__ import annotations

from metrogym import Color, MetroSystem, train
from metrogym.primitives import Line, Network, Station, Train

RING_WAYPOINTS = [
    (180, 80),
    (300, 55),
    (430, 80),
    (530, 155),
    (565, 260),
    (530, 365),
    (430, 440),
    (300, 465),
    (180, 440),
    (80, 365),
    (45, 260),
    (80, 155),
    (180, 80),
]

INNER_CONNECTOR = [
    (300, 465),
    (300, 350),
    (300, 260),
    (300, 170),
    (300, 55),
    (300, 170),
    (300, 260),
    (300, 350),
    (300, 465),
]

CROSS_CONNECTOR = [
    (45, 260),
    (140, 260),
    (220, 260),
    (300, 260),
    (380, 260),
    (460, 260),
    (565, 260),
    (460, 260),
    (380, 260),
    (300, 260),
    (220, 260),
    (140, 260),
    (45, 260),
]


def build_system(*, tick_ms: int = 260, render_scale: int | float = 2) -> MetroSystem:
    parked = train.always_hold()
    return MetroSystem(name="Advanced: Circular City Ring", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Outer Ring", Color.BLUE, RING_WAYPOINTS),
            Line("North-South Chord", Color.GREEN, INNER_CONNECTOR),
            Line("Cross-City Chord", Color.YELLOW, CROSS_CONNECTOR),
            Station("North Arc", (300, 55)),
            Station("North-East", (475, 120)),
            Station("East Arc", (565, 260), radius=10),
            Station("South-East", (475, 400)),
            Station("South Arc", (300, 465)),
            Station("South-West", (125, 400)),
            Station("West Arc", (45, 260), radius=10),
            Station("North-West", (125, 120)),
            Station("Grand Circle", (300, 260), radius=12),
        ]),
        Train("RING-1", line="Outer Ring", solver=parked, asset="metro_nose"),
        Train("RING-2", line="Outer Ring", start_at=33, solver=parked, asset="city_tram"),
        Train("RING-3", line="Outer Ring", start_at=66, solver=parked, asset="bullet_metro"),
        Train("NS", line="North-South Chord", solver=parked, asset="maintenance"),
        Train("XC", line="Cross-City Chord", solver=parked, asset="city_tram"),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
