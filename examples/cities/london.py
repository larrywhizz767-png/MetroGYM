from __future__ import annotations

from metrogym import Color, MetroSystem
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train

STATIONS: dict[str, tuple[int, int]] = {
    "Paddington": (90, 170),
    "Baker St": (205, 150),
    "King's Cross": (360, 120),
    "Liverpool St": (590, 215),
    "Oxford Circus": (285, 235),
    "Holborn": (430, 235),
    "Bank": (535, 250),
    "Piccadilly": (310, 315),
    "Westminster": (335, 380),
    "Waterloo": (420, 410),
    "Victoria": (240, 420),
    "London Bridge": (550, 420),
    "Canada Water": (650, 390),
}

TFL_CENTRAL = Color(220, 36, 31)
TFL_PICCADILLY = Color(0, 25, 168)
TFL_CIRCLE = Color(255, 206, 0)
TFL_VICTORIA = Color(0, 152, 212)
TFL_BAKERLOO = Color(178, 99, 17)
TFL_JUBILEE = Color(160, 165, 169)


def s(name: str) -> tuple[int, int]:
    return STATIONS[name]


def shuttle(*names: str) -> list[tuple[int, int]]:
    points = [s(name) for name in names]
    return [*points, *reversed(points[1:-1]), points[0]]


def loop(*names: str) -> list[tuple[int, int]]:
    points = [s(name) for name in names]
    return [*points, points[0]]


def build_system(*, tick_ms: int = 330, render_scale: int | float = 2) -> MetroSystem:
    interchanges = {"Baker St", "King's Cross", "Oxford Circus", "Holborn", "Bank", "Waterloo", "London Bridge"}
    stations = [Station(name, pos, radius=9 if name in interchanges else 6) for name, pos in STATIONS.items()]
    return MetroSystem(name="City: London Underground Minimal", tick_ms=tick_ms, size=(720, 520), render_scale=render_scale).pipeline([
        Network([
            Line("Central", TFL_CENTRAL, shuttle("Oxford Circus", "Holborn", "Bank", "Liverpool St")),
            Line("Piccadilly", TFL_PICCADILLY, shuttle("King's Cross", "Holborn", "Piccadilly")),
            Line("Circle", TFL_CIRCLE, loop("Paddington", "Baker St", "King's Cross", "Liverpool St", "Westminster", "Victoria")),
            Line("Victoria", TFL_VICTORIA, shuttle("King's Cross", "Oxford Circus", "Victoria")),
            Line("Bakerloo", TFL_BAKERLOO, shuttle("Paddington", "Baker St", "Oxford Circus", "Piccadilly", "Waterloo")),
            Line("Jubilee", TFL_JUBILEE, shuttle("Baker St", "Westminster", "Waterloo", "London Bridge", "Canada Water")),
            *stations,
        ]),
        Train("CEN", line="Central", asset="metro_nose"),
        Train("PIC", line="Piccadilly", asset="bullet_metro"),
        Train("CIR", line="Circle", asset="city_tram"),
        Train("VIC", line="Victoria", asset="metro_nose"),
        Train("BAK", line="Bakerloo", asset="maintenance"),
        Train("JUB", line="Jubilee", asset="bullet_metro"),
        Signal("TL-Bank", (535, 230), initial_green=True, period_ticks=5, label="Bank", controls=ControlRule("Central", s("Holborn"), s("Bank"))),
        Signal("TL-Holborn", (430, 215), initial_green=False, period_ticks=4, label="Holborn", controls=ControlRule("Piccadilly", s("King's Cross"), s("Holborn"))),
        Signal("TL-Oxford", (285, 215), initial_green=True, period_ticks=6, label="Oxford", controls=ControlRule("Victoria", s("King's Cross"), s("Oxford Circus"))),
        Signal("TL-Waterloo", (420, 390), initial_green=False, period_ticks=5, label="Waterloo", controls=ControlRule("Jubilee", s("Westminster"), s("Waterloo"))),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
