from __future__ import annotations


def solve_puzzle(station_data: list[str], target: str = "Museum") -> list[str]:
    """Return the stations inspected by a linear search.

    Input
    -----
    `station_data`
        A list of station names. The values are not sorted.
        Example:
        ["Harbour", "School", "Library", "Depot", "Museum"]

    `target`
        The station to find.
        Example: "Museum"

    Goal
    ----
    Use a linear search: inspect the data from the first item onwards and stop
    as soon as you find `target`.

    Output
    ------
    A list of every station inspected, including the matching station.
    Example:
    ["Harbour", "School", "Library", "Depot", "Museum"]


    found = False
    i = 0
    looped_list = []
    while i < len(station_data) and found == False:
        item = station_data[i]
        looped_list.append(item)

        if item == target:
            found = True
            return looped_list

        i += 1

    raise ValueError("Not found")
    """

    inspected_stations: list[str] = []
    for station_name in station_data:
        inspected_stations.append(station_name)
        if station_name == target:
            return inspected_stations
    raise ValueError("target is not in the station data")
