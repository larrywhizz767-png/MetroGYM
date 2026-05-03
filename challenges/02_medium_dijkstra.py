"""Challenge 2 — MEDIUM — Fastest Route (Dijkstra)
====================================================

Now edges have **different weights** (= travel time in ticks). The fewest
stops is NOT the fastest journey: there is a "Hub" that lets you bypass
long direct edges cheaply.

Your task: implement :func:`solve` so it returns the route with the smallest
*total weight* from ``src`` to ``dst``.

Hint — Dijkstra's algorithm (priority queue by accumulated cost).

Run with:

    uv run python challenges/02_medium_dijkstra.py
"""

from __future__ import annotations

from envs import medium_graph
from framework import Graph, run_challenge


# -----------------------------------------------------------------------------
# YOUR CODE GOES HERE
# -----------------------------------------------------------------------------
def solve(graph: Graph, src: str, dst: str) -> list[str]:
    """Return the route that minimises total edge weight.

    Useful bits:
        graph.neighbours(u) -> [(v, weight), ...]
        graph.weight(a, b)  -> float

    Expected output for src="N1", dst="S2":
        the path whose weights sum to the smallest total ticks.
    """
    # TODO: implement Dijkstra's algorithm
    raise NotImplementedError
# -----------------------------------------------------------------------------


if __name__ == "__main__":
    run_challenge(
        graph=medium_graph(),
        src="N1",
        dst="S2",
        mode="dijkstra",
        solve=solve,
        title="Medium: Fastest Route (Dijkstra)",
    )
