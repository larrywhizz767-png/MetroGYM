"""Challenge 1 — EASY — Shortest Hops (BFS)
===============================================

You're given a tiny 6-station network. Every edge takes the same time, so the
**shortest path is the one with the fewest stops**.

Your task: implement :func:`solve` so it returns the shortest sequence of
stations from ``src`` to ``dst`` (inclusive at both ends).

Hint — breadth-first search.

Run with:

    uv run python challenges/01_easy_bfs.py
"""

from __future__ import annotations

from envs import easy_graph
from framework import Graph, run_challenge


# -----------------------------------------------------------------------------
# YOUR CODE GOES HERE
# -----------------------------------------------------------------------------
def solve(graph: Graph, src: str, dst: str) -> list[str]:
    """Return the shortest-hops path from ``src`` to ``dst``.

    ``graph.neighbours(name)`` returns ``[(neighbour, weight), ...]``.
    You can ignore weights for this challenge — every edge costs 1.

    Example expected output for src="A", dst="F":
        ["A", "B", "E", "F"]   (3 hops; alternative "A","D","E","F" also OK)
    """
    # TODO: implement BFS
    raise NotImplementedError
# -----------------------------------------------------------------------------


if __name__ == "__main__":
    run_challenge(
        graph=easy_graph(),
        src="A",
        dst="F",
        mode="bfs",
        solve=solve,
        title="Easy: Shortest Hops (BFS)",
    )
