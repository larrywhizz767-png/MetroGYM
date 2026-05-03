from __future__ import annotations

import math

from framework import Graph
from metrogym import Color


def easy_graph() -> Graph:
    stations = {
        "A": (150, 180),
        "B": (350, 180),
        "C": (550, 180),
        "D": (150, 360),
        "E": (350, 360),
        "F": (550, 360),
    }
    edges = {
        frozenset({"A", "B"}): 1,
        frozenset({"B", "C"}): 1,
        frozenset({"A", "D"}): 1,
        frozenset({"B", "E"}): 1,
        frozenset({"C", "F"}): 1,
        frozenset({"D", "E"}): 1,
        frozenset({"E", "F"}): 1,
    }
    lines = {
        "Top": ["A", "B", "C"],
        "Bottom": ["D", "E", "F"],
        "Left": ["A", "D"],
        "Middle": ["B", "E"],
        "Right": ["C", "F"],
    }
    return Graph(stations=stations, edges=edges, lines=lines, colors={})


def medium_graph() -> Graph:
    stations = {
        "N1": (200, 100),
        "N2": (500, 100),
        "M1": (100, 260),
        "M2": (350, 260),
        "M3": (600, 260),
        "S1": (200, 420),
        "S2": (500, 420),
        "Hub": (350, 180),
    }
    edges = {
        frozenset({"N1", "N2"}): 9,
        frozenset({"N1", "Hub"}): 2,
        frozenset({"N2", "Hub"}): 2,
        frozenset({"N1", "M1"}): 4,
        frozenset({"N2", "M3"}): 4,
        frozenset({"M1", "M2"}): 3,
        frozenset({"M2", "M3"}): 3,
        frozenset({"M1", "S1"}): 4,
        frozenset({"M3", "S2"}): 4,
        frozenset({"S1", "S2"}): 9,
        frozenset({"M2", "Hub"}): 2,
    }
    lines = {
        "North": ["N1", "N2"],
        "South": ["S1", "S2"],
        "Spine": ["M1", "M2", "M3"],
        "West": ["N1", "M1", "S1"],
        "East": ["N2", "M3", "S2"],
        "Hubline": ["N1", "Hub", "M2", "Hub", "N2"],
    }
    return Graph(stations=stations, edges=edges, lines=lines, colors={})


def _dist(a: tuple[int, int], b: tuple[int, int]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def london_graph() -> Graph:
    stations = {
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
    }
    lines = {
        "Central": ["Oxford Circus", "Tott. Ct. Rd", "Holborn", "Bank", "Liverpool St"],
        "Piccadilly": ["King's Cross", "Holborn", "Piccadilly Cir."],
        "Northern": ["King's Cross", "Tott. Ct. Rd", "Waterloo", "Bank"],
        "Circle": ["Paddington", "Baker St", "King's Cross", "Liverpool St", "Westminster", "Victoria", "Paddington"],
        "Victoria": ["King's Cross", "Oxford Circus", "Victoria"],
        "Bakerloo": ["Paddington", "Baker St", "Oxford Circus", "Piccadilly Cir.", "Waterloo"],
    }
    colors = {
        "Central": Color(220, 36, 31),
        "Piccadilly": Color(0, 25, 168),
        "Northern": Color(80, 80, 80),
        "Circle": Color(255, 206, 0),
        "Victoria": Color(0, 152, 212),
        "Bakerloo": Color(178, 99, 17),
    }
    edges: dict[frozenset, float] = {}
    for stops in lines.values():
        for a, b in zip(stops, stops[1:]):
            if a == b:
                continue
            key = frozenset({a, b})
            weight = _dist(stations[a], stations[b])
            if key not in edges or weight < edges[key]:
                edges[key] = weight
    return Graph(stations=stations, edges=edges, lines=lines, colors=colors)
