from __future__ import annotations

from metrogym import Color, MetroSystem
from metrogym.primitives import Line, Network, Station, Train


def main() -> None:
    system = MetroSystem(name="Two Trains, Three Stations", tick_ms=350, render_scale=1).pipeline([
        Network([
            Line("Loop", Color.GREEN, [(120, 200), (580, 200), (580, 360), (120, 360), (120, 200)]),
            Station("North-West", (120, 200)),
            Station("North-East", (580, 200)),
            Station("South", (350, 360)),
        ]),
        Train("A", line="Loop"),
        Train("B", line="Loop", start_at=50, color=Color.GREEN.darker()),
    ])
    system.fit().run()


if __name__ == "__main__":
    main()
