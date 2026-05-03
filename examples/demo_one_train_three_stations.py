from __future__ import annotations

from metrogym import Color, MetroSystem
from metrogym.primitives import Line, Network, Station, Train


def main() -> None:
    system = MetroSystem(name="One Train, Three Stations", tick_ms=350, render_scale=1).pipeline([
        Network([
            Line("Shuttle", Color.BLUE, [(100, 260), (350, 260), (600, 260), (350, 260), (100, 260)]),
            Station("Westwood", (100, 260)),
            Station("Midtown", (350, 260)),
            Station("Eastview", (600, 260)),
        ]),
        Train("S1", line="Shuttle"),
    ])
    system.fit().run()


if __name__ == "__main__":
    main()
