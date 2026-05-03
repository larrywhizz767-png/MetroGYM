from __future__ import annotations

from metrogym import Color, MetroSystem
from metrogym.primitives import Line, Network, Station, Train


def main() -> None:
    system = MetroSystem(name="My First Metro", tick_ms=400, render_scale=1).pipeline([
        Network([
            Line("Loop", Color(80, 200, 255), [(120, 120), (560, 120), (560, 380), (120, 380), (120, 120)]),
            Station("Origin", (120, 120)),
            Station("Far Side", (560, 380)),
        ]),
        Train("A", line="Loop"),
        Train("B", line="Loop", start_at=50),
    ])
    system.fit().run()


if __name__ == "__main__":
    main()
