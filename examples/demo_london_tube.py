from __future__ import annotations

from metrogym import Color, MetroSystem
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train

STATIONS: dict[str, tuple[int, int]] = {
    "Paddington": (110, 170),
    "Baker St": (240, 150),
    "King's Cross": (400, 130),
    "Liverpool St": (610, 250),
    "Oxford Circus": (320, 240),
    "Tott. Ct. Rd": (390, 250),
    "Holborn": (470, 250),
    "Bank": (540, 270),
    "Piccadilly Cir.": (340, 320),
    "Westminster": (350, 380),
    "Waterloo": (420, 410),
    "Victoria": (250, 420),
    "Southwark": (475, 430),
    "London Bridge": (540, 430),
    "Bermondsey": (605, 420),
    "Canada Water": (660, 395),
}

TFL_RED = Color(220, 36, 31)
TFL_NAVY = Color(0, 25, 168)
TFL_GREY = Color(80, 80, 80)
TFL_YELLOW = Color(255, 206, 0)
TFL_LIGHT_BLUE = Color(0, 152, 212)
TFL_BROWN = Color(178, 99, 17)
TFL_SILVER = Color(160, 165, 169)


def s(name: str) -> tuple[int, int]:
    return STATIONS[name]


def shuttle_through(*names: str) -> list[tuple[int, int]]:
    points = [s(name) for name in names]
    return points + list(reversed(points[1:-1])) + [points[0]]


def loop(*names: str) -> list[tuple[int, int]]:
    points = [s(name) for name in names]
    return points + [points[0]]


def main() -> None:
    interchange = {"King's Cross", "Oxford Circus", "Bank", "Waterloo", "Baker St", "Holborn", "London Bridge", "Canada Water"}
    station_primitives = [
        Station(name, pos, radius=9 if name in interchange else 6)
        for name, pos in STATIONS.items()
    ]
    system = MetroSystem(name="London Tube (schematic)", tick_ms=350, size=(700, 520), render_scale=1).pipeline([
        Network([
            Line("Central", TFL_RED, shuttle_through("Oxford Circus", "Tott. Ct. Rd", "Holborn", "Bank", "Liverpool St")),
            Line("Piccadilly", TFL_NAVY, shuttle_through("King's Cross", "Holborn", "Piccadilly Cir.")),
            Line("Northern", TFL_GREY, shuttle_through("King's Cross", "Tott. Ct. Rd", "Waterloo", "Bank")),
            Line("Circle", TFL_YELLOW, loop("Paddington", "Baker St", "King's Cross", "Liverpool St", "Westminster", "Victoria")),
            Line("Victoria", TFL_LIGHT_BLUE, shuttle_through("King's Cross", "Oxford Circus", "Victoria")),
            Line("Bakerloo", TFL_BROWN, shuttle_through("Paddington", "Baker St", "Oxford Circus", "Piccadilly Cir.", "Waterloo")),
            Line("Jubilee", TFL_SILVER, shuttle_through("Baker St", "Westminster", "Waterloo", "Southwark", "London Bridge", "Bermondsey", "Canada Water")),
            *station_primitives,
        ]),
        Train("CEN", line="Central"),
        Train("PIC", line="Piccadilly"),
        Train("NOR", line="Northern"),
        Train("CIR", line="Circle"),
        Train("VIC", line="Victoria"),
        Train("BAK", line="Bakerloo"),
        Train("JUB", line="Jubilee"),
        Signal("TL-Bank", (540, 250), initial_green=True, period_ticks=5, label="Bank Jct", controls=ControlRule("Central", s("Holborn"), s("Bank"))),
        Signal("TL-Holborn", (470, 230), initial_green=False, period_ticks=4, label="Holborn Jct", controls=ControlRule("Piccadilly", s("King's Cross"), s("Holborn"))),
        Signal("TL-Oxford", (320, 220), initial_green=True, period_ticks=6, label="Oxford Cir Jct", controls=ControlRule("Victoria", s("King's Cross"), s("Oxford Circus"))),
        Signal("TL-LBridge", (540, 410), initial_green=True, period_ticks=5, label="L.Bridge Jct", controls=ControlRule("Jubilee", s("Waterloo"), s("London Bridge"))),
    ])
    system.fit().run()


if __name__ == "__main__":
    main()
