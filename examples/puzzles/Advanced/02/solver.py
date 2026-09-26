from __future__ import annotations

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
    return [], 0, []
