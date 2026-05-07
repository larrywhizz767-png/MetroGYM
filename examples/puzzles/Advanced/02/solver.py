from __future__ import annotations

import heapq


def build_graph(
    lines: dict[str, list[str]],
    segment_minutes: dict[tuple[str, frozenset[str]], int],
) -> dict[str, list[tuple[str, str, int]]]:
    graph: dict[str, list[tuple[str, str, int]]] = {}
    for line_name, stations in lines.items():
        for left, right in zip(stations, stations[1:]):
            minutes = segment_minutes[(line_name, frozenset({left, right}))]
            if left not in graph:
                graph[left] = []
            if right not in graph:
                graph[right] = []
            graph[left].append((right, line_name, minutes))
            graph[right].append((left, line_name, minutes))
    return graph


def transfer_penalty(
    transfer_penalties: dict[frozenset[str], int],
    default_transfer_penalty: int,
    current_line: str,
    next_line: str,
) -> int:
    if not current_line or current_line == next_line:
        return 0
    return transfer_penalties.get(frozenset({current_line, next_line}), default_transfer_penalty)


def _solve_puzzle(
    lines: dict[str, list[str]],
    segment_minutes: dict[tuple[str, frozenset[str]], int],
    transfer_penalties: dict[frozenset[str], int],
    default_transfer_penalty: int,
    start: str = "West Depot",
    goal: str = "Airport",
) -> tuple[list[str], int, list[str]]:
    graph = build_graph(lines, segment_minutes)
    if start not in graph or goal not in graph:
        raise ValueError("start and goal must be in the transfer graph")

    start_state = (start, "")
    heap: list[tuple[int, str, str]] = [(0, start, "")]
    best_cost = {start_state: 0}
    parents: dict[tuple[str, str], tuple[str, str] | None] = {start_state: None}

    while heap:
        cost_so_far, current_station, current_line = heapq.heappop(heap)
        current_state = (current_station, current_line)
        if cost_so_far > best_cost[current_state]:
            continue
        if current_station == goal:
            break
        for neighbor, next_line, travel_minutes in graph[current_station]:
            candidate = cost_so_far + travel_minutes + transfer_penalty(
                transfer_penalties,
                default_transfer_penalty,
                current_line,
                next_line,
            )
            next_state = (neighbor, next_line)
            if candidate >= best_cost.get(next_state, float("inf")):
                continue
            best_cost[next_state] = candidate
            parents[next_state] = current_state
            heapq.heappush(heap, (candidate, neighbor, next_line))

    goal_state = min(
        (state for state in best_cost if state[0] == goal),
        key=lambda state: best_cost[state],
        default=None,
    )
    if goal_state is None:
        raise ValueError("no route found with transfer costs")

    station_route: list[str] = []
    line_route: list[str] = []
    current_state: tuple[str, str] | None = goal_state
    while current_state is not None:
        station, line_name = current_state
        station_route.append(station)
        if line_name:
            line_route.append(line_name)
        current_state = parents[current_state]
    station_route.reverse()
    line_route.reverse()
    return station_route, best_cost[goal_state], line_route


def solve_puzzle(
    lines: dict[str, list[str]],
    segment_minutes: dict[tuple[str, frozenset[str]], int],
    transfer_penalties: dict[frozenset[str], int],
    default_transfer_penalty: int,
    start: str = "West Depot",
    goal: str = "Airport",
) -> tuple[list[str], int, list[str]]:
    """Find the cheapest route when changing lines has a cost.

    Input
    -----
    `lines`
        A dictionary where each key is a line name and each value is the list
        of stations visited by that line.
        Example:
        {
            "Red": ["West Depot", "Old Town", "Central", "Museum", "Harbour"],
            "Teal": ["Riverside", "Science Hub", "Airport"],
        }

    `segment_minutes`
        A dictionary where each key is `(line_name, station_pair)` and each
        value is the travel time for that direct segment.
        Example:
        {
            ("Red", frozenset({"West Depot", "Old Town"})): 3,
            ("Teal", frozenset({"Science Hub", "Airport"})): 2,
        }

    `transfer_penalties`
        A dictionary where each key is a pair of line names and each value is
        the extra cost for changing between those lines.
        Example:
        {
            frozenset({"Red", "Silver"}): 2,
            frozenset({"Silver", "Teal"}): 2,
        }

    `default_transfer_penalty`
        The transfer cost to use if a pair of lines is missing.
        Example: 9

    `start`
        The first station.
        Example: "West Depot"

    `goal`
        The destination station.
        Example: "Airport"

    Goal
    ----
    Use Dijkstra's algorithm to find the route with the lowest total cost,
    where total cost means travel time plus transfer penalties.

    Output
    ------
    A triple made of:
    - the station route
    - the total cost
    - the line names used between stations

    Example:
    (["West Depot", "Old Town", "Central", "Museum", "Riverside", "Science Hub", "Airport"], 18, ["Red", "Red", "Red", "Silver", "Teal", "Teal"])
    """
    return _solve_puzzle(
        lines,
        segment_minutes,
        transfer_penalties,
        default_transfer_penalty,
        start,
        goal,
    )
