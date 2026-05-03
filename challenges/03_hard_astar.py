"""Challenge 3 — HARD — London Tube A*
=========================================

Now the network is the simplified central London tube (12 stations, 6 lines,
see ``demo_london_tube.py``). Edge weights = Euclidean pixel distance, and
stations have known ``(x, y)`` coordinates.

Your task: implement :func:`solve` using **A\\*** with a Euclidean heuristic.
The route must be optimal (same cost as Dijkstra), but A* should explore
fewer nodes. We check optimality; the exploration savings are for your own
satisfaction (and your report).

Tips:
  * heuristic h(n) = Euclidean distance from ``n`` to ``dst``
    — admissible because no edge is shorter than the straight line.
  * f(n) = g(n) + h(n); pop smallest f from the priority queue.
  * Use the same priority-queue pattern as Dijkstra.

Run with:

    uv run python challenges/03_hard_astar.py
"""

from __future__ import annotations

import math

from envs import london_graph
from framework import Graph, run_challenge


# -----------------------------------------------------------------------------
# YOUR CODE GOES HERE
# -----------------------------------------------------------------------------
def solve(graph: Graph, src: str, dst: str) -> list[str]:
    """Return the minimum-weight station-to-station route using A*.

    Helpful bits:
        graph.stations[name] -> (x, y)
        graph.neighbours(u)  -> [(v, weight), ...]

    Suggested heuristic:
        h(n) = euclidean(graph.stations[n], graph.stations[dst])
    """
    # TODO: implement A*
    raise NotImplementedError


def euclidean(a: tuple[int, int], b: tuple[int, int]) -> float:
    """Helper you may want to use."""
    return math.hypot(a[0] - b[0], a[1] - b[1])
# -----------------------------------------------------------------------------


if __name__ == "__main__":
    run_challenge(
        graph=london_graph(),
        src="Paddington",
        dst="Waterloo",
        mode="dijkstra",  # optimal cost is the same; we just check optimality
        solve=solve,
        title="Hard: London Tube (A*)",
    )
