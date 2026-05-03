from __future__ import annotations

from metrogym import Color, MetroSystem
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train


def build_system(*, tick_ms: int = 500, render_scale: int | float = 2) -> MetroSystem:
    stations = [
        Station("Westgate", (80, 80)), Station("MidCity", (300, 80)), Station("Eastgate", (540, 80)),
        Station("North Hub", (200, 60)), Station("Blue Ctr", (200, 200)), Station("South Hub", (255, 385)),
        Station("Green-SW", (100, 390)), Station("Green-NE", (470, 110)),
        Station("YW-Corner", (150, 180)), Station("YE-Corner", (450, 180)),
        Station("YSE-Corner", (450, 360)), Station("YSW-Corner", (150, 360)),
        Station("Purple-W", (100, 250)), Station("Purple-N", (290, 150)),
        Station("Purple-E", (500, 280)), Station("Purple-S", (290, 400)),
        Station("CENTRAL", (300, 230), radius=10),
    ]
    return MetroSystem(name="Metro Gymulation (Python)", tick_ms=tick_ms, verbose=True, render_scale=render_scale).pipeline([
        Network([
            Line("Red Line", Color.RED, [(60, 80), (540, 80), (560, 110), (540, 140), (60, 140), (40, 110), (60, 80)]),
            Line("Blue Line", Color.BLUE, [(200, 50), (200, 350), (220, 380), (260, 390), (260, 50), (200, 50)]),
            Line("Green Line", Color.GREEN, [(80, 400), (480, 100), (500, 120), (100, 420), (80, 400)]),
            Line("Yellow Line", Color.YELLOW, [(150, 180), (450, 180), (450, 360), (150, 360), (150, 180)]),
            Line("Purple Line", Color.PURPLE, [(100, 250), (200, 150), (380, 150), (500, 280), (380, 400), (200, 400), (100, 250)]),
            *stations,
        ]),
        Train("R1", line="Red Line", asset="metro_nose"),
        Train("R2", line="Red Line", start_at=50, color=Color.RED.darker(), asset="maintenance"),
        Train("B1", line="Blue Line", asset="city_tram"),
        Train("B2", line="Blue Line", start_at=50, color=Color.BLUE.darker(), asset="bullet_metro"),
        Train("G1", line="Green Line", asset="metro_nose"),
        Train("Y1", line="Yellow Line", asset="maintenance"),
        Train("P1", line="Purple Line", asset="city_tram"),
        Signal("TL-North", (200, 80), initial_green=True, period_ticks=4, label="North Jct", controls=ControlRule("Red Line", (60, 80), (540, 80))),
        Signal("TL-Centre", (300, 270), initial_green=False, period_ticks=6, label="Central", controls=ControlRule("Red Line", (540, 140), (60, 140))),
        Signal("TL-Blue-N", (230, 100), initial_green=True, period_ticks=5, label="B-North", controls=ControlRule("Blue Line", (200, 50), (200, 350))),
        Signal("TL-Green", (290, 250), initial_green=False, period_ticks=3, label="G-Xing", controls=ControlRule("Green Line", (80, 400), (480, 100))),
        Signal("TL-Yellow-W", (150, 270), initial_green=True, period_ticks=7, label="Y-West", controls=ControlRule("Yellow Line", (150, 180), (450, 180))),
        Signal("TL-Purple-S", (290, 400), initial_green=False, period_ticks=5, label="P-South", controls=ControlRule("Purple Line", (380, 400), (200, 400))),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
