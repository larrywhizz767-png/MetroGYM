from __future__ import annotations

from metrogym import Color, MetroSystem, train
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train


def build_system(*, tick_ms: int = 280, render_scale: int | float = 2) -> MetroSystem:
    stations = [
        Station("West End", (60, 120)),
        Station("Museum", (210, 120)),
        Station("Central", (360, 220), radius=11),
        Station("Harbour", (560, 120)),
        Station("University", (560, 340)),
        Station("Old Town", (210, 340)),
        Station("Depot", (60, 340)),
    ]
    parked = train.always_hold()
    return MetroSystem(name="Advanced: Multi Asset Control Room", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Civic", Color.BLUE, [(60, 120), (210, 120), (360, 220), (560, 120), (560, 340), (360, 220), (210, 340), (60, 340), (60, 120)]),
            Line("Harbour", Color.GREEN, [(60, 340), (210, 340), (360, 220), (560, 340), (560, 120), (360, 220), (210, 120), (60, 120), (60, 340)]),
            Line("Express", Color.YELLOW, [(60, 120), (360, 220), (560, 340), (360, 220), (560, 120), (360, 220), (60, 340), (60, 120)]),
            *stations,
        ]),
        Train("CIV-1", line="Civic", solver=parked, asset="metro_nose"),
        Train("CIV-2", line="Civic", start_at=45, solver=parked, asset="city_tram"),
        Train("HAR-1", line="Harbour", solver=parked, asset="maintenance"),
        Train("EXP", line="Express", solver=parked, asset="bullet_metro"),
        Signal("Central-West", (325, 205), initial_green=True, period_ticks=4, label="C-W", controls=ControlRule("Civic", (210, 120), (360, 220))),
        Signal("Central-East", (400, 205), initial_green=False, period_ticks=5, label="C-E", controls=ControlRule("Harbour", (560, 120), (360, 220))),
        Signal("Central-South", (360, 260), initial_green=True, period_ticks=6, label="C-S", controls=ControlRule("Express", (360, 220), (560, 340))),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
