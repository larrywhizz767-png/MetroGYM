from __future__ import annotations


def _solve_puzzle(line_order: list[str], start: str = "Depot", goal: str = "Museum") -> list[str]:
    if start not in line_order or goal not in line_order:
        raise ValueError("start and goal must be stations on the line")

    start_index = line_order.index(start)
    goal_index = line_order.index(goal)

    if start_index <= goal_index:
        return line_order[start_index : goal_index + 1]

    route = line_order[goal_index : start_index + 1]
    route.reverse()
    return route


def solve_puzzle(line_order: list[str], start: str = "Depot", goal: str = "Museum") -> list[str]:
    """Find the route on a single metro line.

    Input
    -----
    `line_order`
        A list of station names in travel order.
        Example:
        ["Depot", "School", "Library", "Museum", "Harbour"]

    `start`
        The station where the train starts.
        Example: "Depot"

    `goal`
        The station where the train must finish.
        Example: "Museum"

    Goal
    ----
    Return every station visited from `start` to `goal`.
    There is only one line, so you only need to take the correct slice.

    Output
    ------
    A list of station names, including both ends.
    Example:
    ["Depot", "School", "Library", "Museum"]
    """
    return _solve_puzzle(line_order, start, goal)
