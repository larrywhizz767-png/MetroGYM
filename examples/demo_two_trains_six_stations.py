from __future__ import annotations

from metrogym import Color, MetroSystem
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train


def main() -> None:
    system = MetroSystem(name="Two Trains, Six Stations + Lights", tick_ms=300, render_scale=1).pipeline([
        Network([
            Line("City Loop", Color.PURPLE, [(90, 140), (600, 140), (600, 380), (90, 380), (90, 140)]),
            Station("Northgate", (90, 140)),
            Station("Highbury", (350, 140)),
            Station("Eastfield", (600, 140)),
            Station("Southport", (600, 380)),
            Station("Riverside", (350, 380)),
            Station("Westgate", (90, 380)),
        ]),
        Train("M1", line="City Loop"),
        Train("M2", line="City Loop", start_at=50, color=Color.PURPLE.darker()),
        Signal("TL-N", (350, 120), initial_green=True, period_ticks=4, label="N-Jct", controls=ControlRule("City Loop", (90, 140), (600, 140))),
        Signal("TL-E", (620, 260), initial_green=True, period_ticks=5, label="E-Jct", controls=ControlRule("City Loop", (600, 140), (600, 380))),
        Signal("TL-S", (350, 400), initial_green=False, period_ticks=6, label="S-Jct", controls=ControlRule("City Loop", (600, 380), (90, 380))),
        Signal("TL-W", (70, 260), initial_green=False, period_ticks=5, label="W-Jct", controls=ControlRule("City Loop", (90, 380), (90, 140))),
    ])
    system.fit().run()


if __name__ == "__main__":
    main()
