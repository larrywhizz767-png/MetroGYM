from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Iterable

from metrogym import Color
from metrogym.runtimes import RuntimeSimulator

HIGHLIGHT_RGB = (255, 215, 0)
DIM_RGB = (70, 80, 110)


@dataclass(frozen=True)
class Graph:
    stations: dict[str, tuple[int, int]]
    edges: dict[frozenset, float]
    lines: dict[str, list[str]]
    colors: dict[str, object] = field(default_factory=dict)

    def neighbours(self, station: str) -> list[tuple[str, float]]:
        out = []
        for key, weight in self.edges.items():
            if station in key:
                (other,) = [name for name in key if name != station]
                out.append((other, weight))
        return sorted(out)

    def weight(self, a: str, b: str) -> float:
        return self.edges[frozenset({a, b})]


@dataclass
class Result:
    ok: bool
    reason: str
    total_cost: float
    route: list[str]
    optimal_cost: float


def _bfs(graph: Graph, src: str, dst: str) -> tuple[list[str], float]:
    if src == dst:
        return [src], 0.0
    prev: dict[str, str] = {src: src}
    q = deque([src])
    while q:
        u = q.popleft()
        for v, _weight in graph.neighbours(u):
            if v in prev:
                continue
            prev[v] = u
            if v == dst:
                path = [v]
                while path[-1] != src:
                    path.append(prev[path[-1]])
                return list(reversed(path)), float(len(path) - 1)
            q.append(v)
    return [], float("inf")


def _dijkstra(graph: Graph, src: str, dst: str) -> tuple[list[str], float]:
    dist = {src: 0.0}
    prev: dict[str, str] = {}
    pq = [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == dst:
            path = [u]
            while path[-1] != src:
                path.append(prev[path[-1]])
            return list(reversed(path)), d
        if d > dist.get(u, float("inf")):
            continue
        for v, w in graph.neighbours(u):
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    return [], float("inf")


def check(
    graph: Graph,
    src: str,
    dst: str,
    route: list[str],
    *,
    mode: str = "dijkstra",
    tolerance: float = 1e-6,
) -> Result:
    if not isinstance(route, list) or not all(isinstance(station, str) for station in route):
        return Result(False, "route must be a list[str]", float("inf"), [], 0)
    if not route:
        return Result(False, "route is empty", float("inf"), [], 0)
    if route[0] != src:
        return Result(False, f"route must start at {src!r}", float("inf"), route, 0)
    if route[-1] != dst:
        return Result(False, f"route must end at {dst!r}", float("inf"), route, 0)

    cost = 0.0
    for a, b in zip(route, route[1:]):
        key = frozenset({a, b})
        if key not in graph.edges:
            return Result(False, f"no edge between {a!r} and {b!r}", float("inf"), route, 0)
        cost += graph.edges[key]

    truth_fn = {"bfs": _bfs, "dijkstra": _dijkstra}[mode]
    _truth_path, truth_cost = truth_fn(graph, src, dst)
    compare_cost = float(len(route) - 1) if mode == "bfs" else cost
    ok = abs(compare_cost - truth_cost) <= tolerance
    reason = "optimal" if ok else f"suboptimal: yours={compare_cost}, optimal={truth_cost}"
    return Result(ok, reason, cost, route, truth_cost)


def visualise(
    graph: Graph,
    route: list[str],
    *,
    title: str = "Route",
    tick_ms: int = 350,
    src_name: str | None = None,
    dst_name: str | None = None,
) -> None:
    sim = RuntimeSimulator(title=title, tick_ms=tick_ms, render_scale=1)
    highlight = Color(*HIGHLIGHT_RGB)
    dim = Color(*DIM_RGB)

    for line_name, stations in graph.lines.items():
        color = graph.colors.get(line_name, dim)
        faded = Color(*_mix(color, dim, 0.65))
        sim.add_line(line_name, faded, [graph.stations[station] for station in stations])

    for name, pos in graph.stations.items():
        radius = 10 if name in {src_name, dst_name} else 6
        sim.add_station(name, pos, radius=radius)

    if route:
        path = [graph.stations[station] for station in route]
        waypoints = path + list(reversed(path[1:-1])) + [path[0]] if len(path) > 1 else path
        route_line = sim.add_line("Route", highlight, waypoints)
        sim.add_train("YOU", route_line, color=highlight)
        sim.link_peers(["YOU"])

    sim.show()


def _mix(color: object, other_color: object, t: float) -> tuple[int, int, int]:
    r = int(color.getRed() * (1 - t) + other_color.getRed() * t)
    g = int(color.getGreen() * (1 - t) + other_color.getGreen() * t)
    b = int(color.getBlue() * (1 - t) + other_color.getBlue() * t)
    return r, g, b


def run_challenge(
    *,
    graph: Graph,
    src: str,
    dst: str,
    mode: str,
    solve: Callable[[Graph, str, str], list[str]],
    title: str,
) -> None:
    route = solve(graph, src, dst)
    result = check(graph, src, dst, route, mode=mode)

    print("=" * 60)
    print(f"Challenge: {title}")
    print(f"  from: {src!r}")
    print(f"  to:   {dst!r}")
    print(f"  your route ({len(route)} stops): {' → '.join(route) if route else '(empty)'}")
    print(f"  your cost:    {result.total_cost}")
    print(f"  optimal cost: {result.optimal_cost}")
    print(f"  verdict:      {'✅ OK' if result.ok else '❌ ' + result.reason}")
    print("=" * 60)

    visualise(graph, route, title=title, src_name=src, dst_name=dst)
