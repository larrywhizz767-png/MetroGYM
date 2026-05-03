from __future__ import annotations

from metrogym import Color, MetroSystem
from metrogym.primitives import Line, Network, Station, Train


def main() -> None:
    system = MetroSystem(name="Collision Without Control", tick_ms=350, render_scale=1).pipeline([
        Network([
            Line("Unsafe Loop", Color.RED, [(160, 180), (540, 180), (540, 340), (160, 340), (160, 180)]),
            Station("West", (160, 180)),
            Station("East", (540, 180)),
            Station("South", (350, 340)),
        ]),
        Train("A", line="Unsafe Loop"),
        Train("B", line="Unsafe Loop"),
    ])
    system.fit().run()


if __name__ == "__main__":
    main()
