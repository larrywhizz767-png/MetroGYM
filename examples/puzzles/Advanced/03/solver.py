from __future__ import annotations


def solve_puzzle(graph: dict[str, list[str]], start: str = "Depot", goal: str = "Airport") -> list[str]:
    """Find the route with the fewest stops in a larger network.

    Input
    -----
    `graph`
        A dictionary of direct station links.
        Example:
        {
            "Depot": ["Old Town"],
            "Old Town": ["Depot", "Central", "South Gate"],
            "Airport": ["Skyport", "Junction 7", "Riverside"],
        }

    `start`
        The station where the journey begins.
        Example: "Depot"

    `goal`
        The station you want to reach.
        Example: "Airport"

    Goal
    ----
    Use breadth-first search to find the route with the lowest number of stops.
    The network is bigger, but the algorithm idea is the same as in easier BFS
    puzzles.

    Output
    ------
    A list of station names in travel order.
    Example:
    ["Depot", "Old Town", "Central", "Museum", "Riverside", "Airport"]
    """
    return []
