"""Reference solution (INSTRUCTOR ONLY — don't share with students)."""

from __future__ import annotations

from collections import deque

from envs import easy_graph
from framework import Graph, run_challenge


def solve(graph: Graph, src: str, dst: str) -> list[str]:
    if src == dst:
        return [src]
    prev = {src: None}
    q = deque([src])
    while q:
        u = q.popleft()
        for v, _ in graph.neighbours(u):
            if v in prev:
                continue
            prev[v] = u
            if v == dst:
                path = [v]
                while prev[path[-1]] is not None:
                    path.append(prev[path[-1]])
                return list(reversed(path))
            q.append(v)
    return []


if __name__ == "__main__":
    run_challenge(graph=easy_graph(), src="A", dst="F",
                  mode="bfs", solve=solve, title="Easy — reference")
