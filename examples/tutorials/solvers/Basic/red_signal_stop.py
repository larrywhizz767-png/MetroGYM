from __future__ import annotations

from metrogym import Color, MetroSystem, signal, train
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train


def build_system(*, tick_ms: int = 360, render_scale: int | float = 2) -> MetroSystem:
    return MetroSystem(name="Solver Basic: Red Signal Stop", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Signal Demo", Color.GREEN, [(120, 240), (560, 240), (120, 240)]),
            Station("West", (120, 240)),
            Station("Gate", (340, 240), radius=10),
            Station("East", (560, 240)),
        ]),
        Train("CAREFUL", line="Signal Demo", solver=train.respect_signals(), asset="city_tram"),
        Signal(
            "ONE-WAY",
            (340, 205),
            label="1W",
            controls=ControlRule("Signal Demo", (120, 240), (340, 240), "forward"),
            solver=signal.pulse(green_ticks=4, red_ticks=3),
        ),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
