---
icon: lucide/sliders-horizontal
---

# Advanced 02 — Transfer-aware routing

Now the network cares about both movement and inconvenience. Travelling along a segment costs minutes, and changing from one line to another adds a transfer penalty. Your solver must therefore reason over a richer state than just the current station.

## Mission brief

| Item | Value |
|---|---|
| Difficulty | Advanced |
| Start | `West Depot` |
| Goal | `Airport` |
| Objective | Minimise travel time plus transfer cost |
| Main skill | Run [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) on `(station, line)` states |

$$
\operatorname{cost}(P) = \sum_{e \in P} w_e + \sum_{\ell \in \text{transfers}(P)} \tau_{\ell}
$$

## Files

- Edit: [`examples/puzzles/Advanced/02/solver.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Advanced/02/solver.py)
- Reference world: [`examples/puzzles/Advanced/02/world.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Advanced/02/world.py)

## Run

```bash
uv run python examples/puzzles/Advanced/02/world.py
```

## Expected output

```text
Transfer-aware route: West Depot -> Old Town -> Central -> Museum -> Riverside -> Science Hub -> Airport
Lines used: Red -> Red -> Red -> Silver -> Teal -> Teal
Journey time with transfer penalties: 18 minutes
```

!!! tip "State design matters"
    If you only store the best cost per station, you can discard a route that arrives slightly later on a much better line for the next transfer.

## Next puzzle

[Advanced 03 — Larger-city BFS](03-larger-city-bfs.md)
