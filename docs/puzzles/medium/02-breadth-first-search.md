---
icon: lucide/workflow
---

# Medium 02 — Breadth-first search

Starting at `Stadium`, find `Harbour` in a network with several branches and
cycles. This time any valid path is not enough: your solver must return the
path with the fewest station-to-station hops.

Use [breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)
to explore the graph one level at a time.

## Mission brief

| Item | Value |
|---|---|
| Difficulty | Medium |
| Start | `Stadium` |
| Target | `Harbour` |
| Network size | 7 stations |
| Constraint | Minimise the number of station-to-station hops |
| Main skill | Use a first-in, first-out queue to explore level by level |

$$
\operatorname{stops}(P) = |P| - 1
$$

## Files

- Edit: [`examples/puzzles/Medium/02/solver.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Medium/02/solver.py)
- Reference world: [`examples/puzzles/Medium/02/world.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Medium/02/world.py)

## Run

```bash
uv run python examples/puzzles/Medium/02/world.py
```

## Expected output

```text
Target station: Harbour
Shortest BFS path: Stadium -> Junction -> Museum -> Harbour
```

??? question "Why does BFS find the shortest path?"
    Every direct track has the same cost. BFS explores every path with one hop
    before paths with two hops, every path with two hops before paths with
    three, and so on. The first path that reaches `Harbour` is therefore a
    shortest path.

!!! tip "Mark stations when they enter the queue"
    Add a station to the visited set when you enqueue it. This prevents the
    same station being queued repeatedly through different routes.

## Next puzzle

[Advanced 01 — Fastest route](../advanced/01-fastest-route.md)
