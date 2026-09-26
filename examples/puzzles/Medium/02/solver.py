from __future__ import annotations


def solve_puzzle(
    graph: dict[str, list[str]],
    start: str = "Stadium",
    target: str = "Harbour",
) -> list[str]:
    """Find the shortest path to the target station using breadth-first search.

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

    `start`
        The station where the journey begins.
        Example: "Stadium"

    `target`
        The station you want to find.
        Example: "Harbour"

    Goal
    ----
    Use breadth-first search to explore the network level by level. Stop when
    you find `target`; the path must have the fewest possible stops.

    Output
    ------
    A list of station names showing the shortest path from `start` to `target`.
    Example:
    ["Stadium", "Junction", "Museum", "Harbour"]
    """

    queue = [(start, [start])]
    visited = {start}
    index = 0

    while index < len(queue):
        current, path = queue[index]
        index += 1
        if current == target:
            return path
        for neighbour in graph[current]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append((neighbour, path + [neighbour]))

    return []