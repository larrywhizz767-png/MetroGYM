from __future__ import annotations

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
    return [], 0
