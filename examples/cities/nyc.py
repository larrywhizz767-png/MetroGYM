from __future__ import annotations

from metrogym import Color, MetroSystem
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train

STATIONS: dict[str, tuple[int, int]] = {
    "Times Sq": (305, 190),
    "Grand Central": (415, 190),
    "Union Sq": (395, 300),
    "Brooklyn Br": (430, 405),
    "Wall St": (430, 465),
    "Columbus Circle": (235, 120),
    "Penn Station": (290, 245),
    "W 4 St": (310, 330),
    "Jay St": (470, 470),
    "Atlantic Av": (560, 420),
    "Court Sq": (530, 180),
    "Queensboro": (500, 115),
    "Jackson Hts": (640, 110),
    "Fulton St": (420, 440),
}

NYC_RED = Color(238, 53, 46)
NYC_GREEN = Color(0, 147, 60)
NYC_BLUE = Color(0, 57, 166)
NYC_ORANGE = Color(255, 99, 25)
NYC_PURPLE = Color(185, 51, 173)
NYC_GREY = Color(167, 169, 172)


def s(name: str) -> tuple[int, int]:
    return STATIONS[name]


def shuttle(*names: str) -> list[tuple[int, int]]:
    points = [s(name) for name in names]
    return [*points, *reversed(points[1:-1]), points[0]]


def loop(*names: str) -> list[tuple[int, int]]:
    points = [s(name) for name in names]
    return [*points, points[0]]


def build_system(*, tick_ms: int = 320, render_scale: int | float = 2) -> MetroSystem:
    interchanges = {"Times Sq", "Grand Central", "Union Sq", "Fulton St", "Jay St", "Atlantic Av"}
    stations = [Station(name, pos, radius=9 if name in interchanges else 6) for name, pos in STATIONS.items()]
    return MetroSystem(name="City: NYC Subway Minimal", tick_ms=tick_ms, size=(720, 540), render_scale=render_scale).pipeline([
        Network([
            Line("1/2/3 Broadway", NYC_RED, shuttle("Columbus Circle", "Times Sq", "Penn Station", "W 4 St", "Fulton St", "Wall St")),
            Line("4/5/6 Lexington", NYC_GREEN, shuttle("Grand Central", "Union Sq", "Brooklyn Br", "Wall St")),
            Line("A/C/E 8 Avenue", NYC_BLUE, shuttle("Columbus Circle", "Penn Station", "W 4 St", "Jay St")),
            Line("B/D/F/M 6 Avenue", NYC_ORANGE, shuttle("Times Sq", "W 4 St", "Jay St", "Atlantic Av")),
            Line("7 Flushing", NYC_PURPLE, shuttle("Times Sq", "Grand Central", "Court Sq", "Queensboro", "Jackson Hts")),
            Line("G Crosstown", NYC_GREY, loop("Court Sq", "Jay St", "Atlantic Av", "Union Sq")),
            *stations,
        ]),
        Train("123", line="1/2/3 Broadway", asset="metro_nose"),
        Train("456", line="4/5/6 Lexington", asset="bullet_metro"),
        Train("ACE", line="A/C/E 8 Avenue", asset="city_tram"),
        Train("BDFM", line="B/D/F/M 6 Avenue", asset="metro_nose"),
        Train("7", line="7 Flushing", asset="bullet_metro"),
        Train("G", line="G Crosstown", asset="maintenance"),
        Signal("TL-Times", (305, 170), initial_green=True, period_ticks=5, label="Times", controls=ControlRule("7 Flushing", s("Times Sq"), s("Grand Central"))),
        Signal("TL-Union", (395, 280), initial_green=False, period_ticks=4, label="Union", controls=ControlRule("4/5/6 Lexington", s("Grand Central"), s("Union Sq"))),
        Signal("TL-Fulton", (420, 420), initial_green=True, period_ticks=6, label="Fulton", controls=ControlRule("1/2/3 Broadway", s("W 4 St"), s("Fulton St"))),
        Signal("TL-Jay", (470, 450), initial_green=False, period_ticks=5, label="Jay", controls=ControlRule("A/C/E 8 Avenue", s("W 4 St"), s("Jay St"))),
        Signal("TL-Queens", (530, 160), initial_green=True, period_ticks=7, label="Court", controls=ControlRule("G Crosstown", s("Court Sq"), s("Jay St"))),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
