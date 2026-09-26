---
icon: lucide/train-front-tunnel
---

# Puzzles Overview

Welcome to the puzzles section of `MetroGYM`. This part of the documentation collects the runnable puzzle worlds distributed in `examples/puzzles/` and presents them as short, self-contained problem statements.

More precisely, this section is intended to help you (i) identify the puzzle objective, (ii) locate the `solver.py` file that should be edited, (iii) run the corresponding `world.py` file, and (iv) verify the expected console output before moving to the next puzzle.


## Available puzzles

<div class="grid cards" markdown>

- __Basic 01 — Linear Search__

    ---

    Search unsorted station data from left to right until you find `Museum`.

    - Concept: [linear search](https://www.bbc.co.uk/bitesize/guides/zjdkw6f/revision/3)
    - Goal: record every station inspected
    - Output: `Linear search checks: Harbour -> School -> Library -> Depot -> Museum`

    [Open puzzle](basic/01-linear-search.md)

- __Basic 02 — Binary Search__

    ---

    Search an alphabetically ordered station list by checking its middle and eliminating half of the remaining data.

    - Concept: [binary search](https://www.bbc.co.uk/bitesize/guides/zjdkw6f/revision/2)
    - Goal: record each middle station inspected
    - Output: `Binary search checks: Garden -> School -> Museum`

    [Open puzzle](basic/02-binary-search.md)

- __Medium 01 — Depth-first search__

    ---

    Explore one branch as far as possible before backtracking to another route.

    - Concept: iterative or recursive [DFS](https://en.wikipedia.org/wiki/Depth-first_search)
    - Goal: find `Harbour` from `Depot` and return the path
    - Output: `DFS path: Depot -> Market -> Museum -> Garden -> Harbour`

    [Open puzzle](medium/01-depth-first-search.md)

- __Medium 02 — Breadth-first search__

    ---

    Explore the graph level by level and return the path with the fewest stops.

    - Concept: [BFS](https://en.wikipedia.org/wiki/Breadth-first_search)
    - Goal: find the shortest path from `Stadium` to `Harbour`
    - Output: `Shortest BFS path: Stadium -> Junction -> Museum -> Harbour`

    [Open puzzle](medium/02-breadth-first-search.md)

- __Advanced 01 — Fastest route__

    ---

    Move from hop count to weighted travel time with [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm).

    - Concept: weighted shortest path
    - Goal: minimise total minutes
    - Output: `Journey time: 16 minutes`

    [Open puzzle](advanced/01-fastest-route.md)

- __Advanced 02 — Transfer-aware routing__

    ---

    Optimise travel minutes and line changes at the same time.

    - Concept: [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) on `(station, line)` states
    - Goal: minimise time plus transfer penalty
    - Output: `Journey time with transfer penalties: 18 minutes`

    [Open puzzle](advanced/02-transfer-aware-routing.md)

- __Advanced 03 — Larger-city [BFS](https://en.wikipedia.org/wiki/Breadth-first_search)__

    ---

    Return to [BFS](https://en.wikipedia.org/wiki/Breadth-first_search) on a denser city graph where reading the right route by eye is harder.

    - Concept: robust [BFS](https://en.wikipedia.org/wiki/Breadth-first_search) at larger scale
    - Goal: minimise stop count
    - Output: `Fewest-stops route: Depot -> Old Town -> Central -> Museum -> Riverside -> Airport (5 stops)`

    [Open puzzle](advanced/03-larger-city-bfs.md)

</div>

## Running all puzzle worlds

```bash
uv run python examples/puzzles/Basic/01/world.py
uv run python examples/puzzles/Basic/02/world.py
uv run python examples/puzzles/Medium/01/world.py
uv run python examples/puzzles/Medium/02/world.py
uv run python examples/puzzles/Advanced/01/world.py
uv run python examples/puzzles/Advanced/02/world.py
uv run python examples/puzzles/Advanced/03/world.py
```
