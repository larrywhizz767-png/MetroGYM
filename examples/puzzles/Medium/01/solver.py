from __future__ import annotations


def solve_puzzle(
    graph: dict[str, list[str]],
    start: str = "Depot",
    target: str = "Harbour",
) -> list[str]:
    """Find a path to the target station using depth-first search.

    Input
    -----
    `graph`
        A dictionary of direct station links.
        Example:
        {
            "Depot": ["Market", "Riverside"],
            "Market": ["Depot", "Museum"],
            "Harbour": ["Garden", "Riverside"],
        }

    `start`
        The station where the journey begins.
        Example: "Depot"

    `target`
        The station you want to find.
        Example: "Harbour"

    Goal
    ----
    Use depth-first search to explore one route as far as possible before
    backtracking. Stop as soon as you find `target`.

    Output
    ------
    A list of station names showing the path from `start` to `target`.
    Example:
    ["Depot", "Market", "Museum", "Garden", "Harbour"]
    """

    visited_stations = {start}
    paths_to_visit = [[start]]

    while paths_to_visit:
        current_path = paths_to_visit.pop()
        current_station = current_path[-1]
        if current_station == target:
            return current_path

        for neighbouring_station in graph[current_station]:
            if neighbouring_station in visited_stations:
                continue

            visited_stations.add(neighbouring_station)
            new_path = current_path + [neighbouring_station]
            paths_to_visit.append(new_path)

    return []
