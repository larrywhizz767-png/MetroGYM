from __future__ import annotations


def _solve_puzzle(
    graph: dict[str, list[str]],
    closed_stations: list[str],
    start: str = "Depot",
    goal: str = "Harbour",
) -> list[str]:
    if start in closed_stations or goal in closed_stations:
        raise ValueError("start and goal must be open stations")

    queue = [start]
    parents: dict[str, str | None] = {start: None}
    queue_index = 0

    while queue_index < len(queue):
        current = queue[queue_index]
        queue_index += 1

        if current == goal:
            break

        for neighbor in graph[current]:
            if neighbor in closed_stations:
                continue
            if neighbor in parents:
                continue
            parents[neighbor] = current
            queue.append(neighbor)

    if goal not in parents:
        raise ValueError("no route found with the closed station removed")

    route: list[str] = []
    current: str | None = goal
    while current is not None:
        route.append(current)
        current = parents[current]
    route.reverse()
    return route


def solve_puzzle(
    graph: dict[str, list[str]],
    closed_stations: list[str],
    start: str = "Depot",
    goal: str = "Harbour",
) -> list[str]:
    """Find the best diversion when some stations are closed.

    Input
    -----
    `graph`
        A dictionary of direct station links.
        Example:
        {
            "Depot": ["Market"],
            "Market": ["Depot", "Museum", "College"],
            "Garden": ["Museum", "Harbour", "Arena", "College"],
        }

    `closed_stations`
        A list of stations that cannot be used.
        Example:
        ["Museum"]

    `start`
        The station where the journey begins.
        Example: "Depot"

    `goal`
        The destination station.
        Example: "Harbour"

    Goal
    ----
    Use breadth-first search to find the route with the fewest stops while
    skipping every station in `closed_stations`.

    Output
    ------
    A list of station names showing the diversion route.
    Example:
    ["Depot", "Market", "College", "Garden", "Harbour"]
    """
    return _solve_puzzle(graph, closed_stations, start, goal)
