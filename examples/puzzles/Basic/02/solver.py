from __future__ import annotations


def _solve_puzzle(graph: dict[str, list[str]], start: str = "West", goal: str = "Airport") -> list[str]:
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


def solve_puzzle(graph: dict[str, list[str]], start: str = "West", goal: str = "Airport") -> list[str]:
    """Find the route with the fewest stops.

    Input
    -----
    `graph`
        A dictionary where each key is a station and each value is the list of
        stations you can reach in one move.
        Example:
        {
            "West": ["Central"],
            "Central": ["West", "East", "North", "South", "Airport"],
            "Airport": ["Central"],
        }

    `start`
        The station where the journey begins.
        Example: "West"

    `goal`
        The station you want to reach.
        Example: "Airport"

    Goal
    ----
    Use breadth-first search to find the path with the lowest number of stops.

    Output
    ------
    A list of station names in travel order.
    Example:
    ["West", "Central", "Airport"]
    """
    return _solve_puzzle(graph, start, goal)
