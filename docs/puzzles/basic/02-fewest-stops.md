---
icon: lucide/git-branch
---

# Basic 02 — Fewest stops

The network now branches. Your task is to compute the route with the lowest number of stops from `West` to `Airport`. This is the first true graph-search puzzle and the best place to make [breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search) concrete.

## Mission brief

| Item | Value |
|---|---|
| Difficulty | Basic |
| Start | `West` |
| Goal | `Airport` |
| Constraint | Minimise the number of station-to-station hops |
| Main skill | Build and backtrack a [breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search) parent map |

$$
\operatorname{stops}(P) = |P| - 1
$$

## Files

- Edit: [`examples/puzzles/Basic/02/solver.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Basic/02/solver.py)
- Reference world: [`examples/puzzles/Basic/02/world.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Basic/02/world.py)

## Run

```bash
uv run python examples/puzzles/Basic/02/world.py
```

## Expected output

```text
Fewest-stops route: West -> Central -> Airport (2 stops)
```

??? question "Why [breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)?"
    Every move has the same cost, so the first time [breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search) reaches the goal, it has also found a route with the minimum number of stops.

## Next puzzle

[Medium 01 — Closed-station diversion](../medium/01-closed-station-diversion.md)
