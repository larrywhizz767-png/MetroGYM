---
icon: lucide/train-front-tunnel
---

# Puzzles Overview

Welcome to the puzzles section of `MetroGYM`. This part of the documentation collects the runnable puzzle worlds distributed in `examples/puzzles/` and presents them as short, self-contained problem statements.

More precisely, this section is intended to help you (i) identify the puzzle objective, (ii) locate the `solver.py` file that should be edited, (iii) run the corresponding `world.py` file, and (iv) verify the expected console output before moving to the next puzzle.


## Available puzzles

<div class="grid cards" markdown>

- __Basic 01 — Single-line route__

    ---

    Slice one ordered line into the exact route from `Depot` to `Museum`.

    - Concept: route slicing
    - Goal: return all visited stations in order
    - Output: `Single-line route: Depot -> School -> Library -> Museum`

    [Open puzzle](basic/01-single-line-route.md)

- __Basic 02 — Fewest stops__

    ---

    Use [breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search) to reach `Airport` from `West` in the minimum number of hops.

    - Concept: [BFS](https://en.wikipedia.org/wiki/Breadth-first_search)
    - Goal: minimise stop count
    - Output: `Fewest-stops route: West -> Central -> Airport (2 stops)`

    [Open puzzle](basic/02-fewest-stops.md)

- __Medium 01 — Closed-station diversion__

    ---

    Re-plan around a closed station while keeping the fewest-stop objective.

    - Concept: [BFS](https://en.wikipedia.org/wiki/Breadth-first_search) with forbidden nodes
    - Goal: skip `Museum`
    - Output: `Diversion route: Depot -> Market -> College -> Garden -> Harbour`

    [Open puzzle](medium/01-closed-station-diversion.md)

- __Medium 02 — Blocked-track diversion__

    ---

    Keep all stations open, but reject one blocked direct connection.

    - Concept: [BFS](https://en.wikipedia.org/wiki/Breadth-first_search) with forbidden edges
    - Goal: skip `Museum - Harbour`
    - Output: `Diversion route: Stadium -> Junction -> Riverside -> Tech Park -> Harbour`

    [Open puzzle](medium/02-blocked-track-diversion.md)

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

