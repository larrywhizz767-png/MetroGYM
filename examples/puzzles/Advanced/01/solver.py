from __future__ import annotations

import heapq


def build_graph(travel_minutes: dict[frozenset[str], int]) -> dict[str, list[tuple[str, int]]]:
    graph: dict[str, list[tuple[str, int]]] = {}
    for edge, minutes in travel_minutes.items():
        left, right = tuple(edge)
        if left not in graph:
            graph[left] = []
        if right not in graph:
            graph[right] = []
        graph[left].append((right, minutes))
        graph[right].append((left, minutes))
    return graph


def _solve_puzzle(
    travel_minutes: dict[frozenset[str], int],
    start: str = "Depot",
    goal: str = "Airport",
) -> tuple[list[str], int]:
    graph = build_graph(travel_minutes)
    if start not in graph or goal not in graph:
        raise ValueError("start and goal must be in the weighted graph")

    heap: list[tuple[int, str]] = [(0, start)]
    best_time = {start: 0}
    parents: dict[str, str | None] = {start: None}

    while heap:
        minutes_so_far, current = heapq.heappop(heap)
        if minutes_so_far > best_time[current]:
            continue
        if current == goal:
            break
        for neighbor, minutes in graph[current]:
            candidate = minutes_so_far + minutes
            if candidate >= best_time.get(neighbor, float("inf")):
                continue
            best_time[neighbor] = candidate
            parents[neighbor] = current
            heapq.heappush(heap, (candidate, neighbor))

    if goal not in best_time:
        raise ValueError("no weighted route found")

    route: list[str] = []
    current: str | None = goal
    while current is not None:
        route.append(current)
        current = parents[current]
    route.reverse()
    return route, best_time[goal]


def solve_puzzle(
    travel_minutes: dict[frozenset[str], int],
    start: str = "Depot",
    goal: str = "Airport",
) -> tuple[list[str], int]:
    """Find the fastest route in a weighted metro network.

    Input
    -----
    `travel_minutes`
        A dictionary where each key is an unordered pair of stations and each
        value is the time needed to travel between them.
        Example:
        {
            frozenset({"Depot", "Old Town"}): 4,
            frozenset({"Central", "Museum"}): 2,
            frozenset({"Tech Park", "Airport"}): 4,
        }

    `start`
        The first station.
        Example: "Depot"

    `goal`
        The destination station.
        Example: "Airport"

    Goal
    ----
    Use Dijkstra's algorithm to find the route with the lowest total travel
    time, even if that route does not have the fewest stops.

    Output
    ------
    A pair made of:
    - the route as a list of station names
    - the total travel time in minutes

    Example:
    (["Depot", "Old Town", "Central", "Museum", "Tech Park", "Airport"], 16)
    """
    return _solve_puzzle(travel_minutes, start, goal)
