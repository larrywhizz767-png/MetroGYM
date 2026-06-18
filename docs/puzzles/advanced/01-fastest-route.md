---
icon: lucide/hourglass
---

# Advanced 01 — Fastest route

The shortest-looking route is no longer necessarily the fastest. Each direct connection carries a travel time in minutes, so the correct objective is total journey time rather than raw stop count.

## Mission brief

| Item | Value |
|---|---|
| Difficulty | Advanced |
| Start | `Depot` |
| Goal | `Airport` |
| Objective | Minimise total travel minutes |
| Main skill | Implement [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) on weighted edges |

$$
\operatorname{time}(P) = \sum_{e \in P} w_e
$$

## Files

- Edit: [`examples/puzzles/Advanced/01/solver.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Advanced/01/solver.py)
- Reference world: [`examples/puzzles/Advanced/01/world.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Advanced/01/world.py)

## Run

```bash
uv run python examples/puzzles/Advanced/01/world.py
```

## Expected output

```text
Fastest route: Depot -> Old Town -> Central -> Museum -> Tech Park -> Airport
Journey time: 16 minutes
```

??? question "Why not [breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search) anymore?"
    Once edge costs differ, the queue order must respect accumulated travel time rather than just the number of hops.

## Next puzzle

[Advanced 02 — Transfer-aware routing](02-transfer-aware-routing.md)
