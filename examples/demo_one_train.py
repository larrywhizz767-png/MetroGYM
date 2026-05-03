from __future__ import annotations

from metrogym import Color, MetroSystem
from metrogym.primitives import Line, Network, Station, Train


def main() -> None:
    system = MetroSystem(name="One Train Demo", tick_ms=400, render_scale=1).pipeline([
        Network([
            Line("My Line", Color.RED, [(120, 120), (560, 120), (560, 380), (120, 380), (120, 120)]),
            Station("Start", (120, 120)),
        ]),
        Train("T1", line="My Line"),
    ])
    system.fit().run()


if __name__ == "__main__":
    main()
