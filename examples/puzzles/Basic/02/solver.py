from __future__ import annotations


def solve_puzzle(ordered_station_data: list[str], target: str = "Museum") -> list[str]:
    """Return the stations inspected by a binary search.

    Input
    -----
    `ordered_station_data`
        A list of station names in ascending alphabetical order.
        Example:
        ["Airport", "Central", "Depot", "Garden", "Museum", "School", "Stadium", "West"]

    `target`
        The station to find.
        Example: "Airport"

    Goal
    ----
    Use binary search. Inspect the middle item of the remaining range, then
    discard the half that cannot contain `target`.

    Output
    ------
    A list of each station inspected, including the matching station.
    Example:
    ["Garden", "School", "Museum"]
    """

    first = 0
    last = len(ordered_station_data) - 1
    inspected_station_list = []

    while first <= last:
        mid = (first + last) // 2
        inspected_station_list.append(ordered_station_data[mid])
        if target == ordered_station_data[mid]:
            break
        elif target > ordered_station_data[mid]:
            first = mid + 1
        else:
            last = mid - 1


    return inspected_station_list
