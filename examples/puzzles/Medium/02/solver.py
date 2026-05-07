from __future__ import annotations


def track_is_blocked(blocked_tracks: list[list[str]], start: str, end: str) -> bool:
    for blocked_start, blocked_end in blocked_tracks:
        if start == blocked_start and end == blocked_end:
            return True
        if start == blocked_end and end == blocked_start:
            return True
    return False


def _solve_puzzle(
    graph: dict[str, list[str]],
    blocked_tracks: list[list[str]],
    start: str = "Stadium",
    goal: str = "Harbour",
) -> list[str]:
    queue = [start]
    parents: dict[str, str | None] = {start: None}
    queue_index = 0

    while queue_index < len(queue):
        current = queue[queue_index]
        queue_index += 1

        if current == goal:
            break

        for neighbor in graph[current]:
            if track_is_blocked(blocked_tracks, current, neighbor):
                continue
            if neighbor in parents:
                continue
            parents[neighbor] = current
            queue.append(neighbor)

    if goal not in parents:
        raise ValueError("no route found around the blocked track")

    route: list[str] = []
    current: str | None = goal
    while current is not None:
        route.append(current)
        current = parents[current]
    route.reverse()
    return route


def solve_puzzle(
    graph: dict[str, list[str]],
    blocked_tracks: list[list[str]],
    start: str = "Stadium",
    goal: str = "Harbour",
) -> list[str]:
    """Find the best diversion when some direct tracks are blocked.

    Input
    -----
    `graph`
        A dictionary of direct station links.
        Example:
        {
            "Stadium": ["Junction"],
            "Junction": ["Stadium", "Museum", "Hilltop", "Riverside"],
            "Harbour": ["Museum", "Tech Park"],
        }

    `blocked_tracks`
        A list of blocked direct links.
        Example:
        [["Museum", "Harbour"]]

    `start`
        The station where the journey begins.
        Example: "Stadium"

    `goal`
        The destination station.
        Example: "Harbour"

    Goal
    ----
    Use breadth-first search to find the route with the fewest stops while
    skipping every blocked direct link.

    Output
    ------
    A list of station names showing the diversion route.
    Example:
    ["Stadium", "Junction", "Riverside", "Tech Park", "Harbour"]
    """
    return _solve_puzzle(graph, blocked_tracks, start, goal)
