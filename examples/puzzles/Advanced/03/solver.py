from __future__ import annotations


def _solve_puzzle(graph: dict[str, list[str]], start: str = "Depot", goal: str = "Airport") -> list[str]:
    if start not in graph or goal not in graph:
        raise ValueError("start and goal must be in the station graph")

    queue = [start]
    parents: dict[str, str | None] = {start: None}
    queue_index = 0

    while queue_index < len(queue):
        current = queue[queue_index]
        queue_index += 1

        if current == goal:
            break

        for neighbor in graph[current]:
            if neighbor in parents:
                continue
            parents[neighbor] = current
            queue.append(neighbor)

    if goal not in parents:
        raise ValueError("no route found")

    route: list[str] = []
    current: str | None = goal
    while current is not None:
        route.append(current)
        current = parents[current]
    route.reverse()
    return route


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
    return _solve_puzzle(graph, start, goal)
