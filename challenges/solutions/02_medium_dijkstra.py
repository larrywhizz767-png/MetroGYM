"""Reference solution (INSTRUCTOR ONLY)."""

from __future__ import annotations

import heapq

from envs import medium_graph
from framework import Graph, run_challenge


def solve(graph: Graph, src: str, dst: str) -> list[str]:
    dist: dict[str, float] = {src: 0.0}
    prev: dict[str, str] = {}
    pq: list[tuple[float, str]] = [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == dst:
            break
        if d > dist.get(u, float("inf")):
            continue
        for v, w in graph.neighbours(u):
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    if dst not in dist:
        return []
    path = [dst]
    while path[-1] != src:
        path.append(prev[path[-1]])
    return list(reversed(path))


if __name__ == "__main__":
    run_challenge(graph=medium_graph(), src="N1", dst="S2",
                  mode="dijkstra", solve=solve, title="Medium — reference")
