"""Reference solution (INSTRUCTOR ONLY)."""

from __future__ import annotations

import heapq
import math

from envs import london_graph
from framework import Graph, run_challenge


def solve(graph: Graph, src: str, dst: str) -> list[str]:
    goal = graph.stations[dst]

    def h(name: str) -> float:
        p = graph.stations[name]
        return math.hypot(p[0] - goal[0], p[1] - goal[1])

    g: dict[str, float] = {src: 0.0}
    prev: dict[str, str] = {}
    pq: list[tuple[float, float, str]] = [(h(src), 0.0, src)]
    while pq:
        f, gu, u = heapq.heappop(pq)
        if u == dst:
            break
        if gu > g.get(u, float("inf")):
            continue
        for v, w in graph.neighbours(u):
            ng = gu + w
            if ng < g.get(v, float("inf")):
                g[v] = ng
                prev[v] = u
                heapq.heappush(pq, (ng + h(v), ng, v))

    if dst not in g:
        return []
    path = [dst]
    while path[-1] != src:
        path.append(prev[path[-1]])
    return list(reversed(path))


if __name__ == "__main__":
    run_challenge(graph=london_graph(), src="Paddington", dst="Waterloo",
                  mode="dijkstra", solve=solve, title="Hard — reference")
