---
icon: lucide/binary
---

# Advanced 03 — Larger-city [BFS](https://en.wikipedia.org/wiki/Breadth-first_search)

The final puzzle returns to [breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search), but on a denser city network where scanning the topology by eye is much harder. The goal is to finish the ladder by solving a bigger instance cleanly and confidently.

## Mission brief

| Item | Value |
|---|---|
| Difficulty | Advanced |
| Start | `Depot` |
| Goal | `Airport` |
| Objective | Minimise the number of stops |
| Main skill | Apply [breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search) robustly on a larger graph |

## Files

- Edit: [`examples/puzzles/Advanced/03/solver.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Advanced/03/solver.py)
- Reference world: [`examples/puzzles/Advanced/03/world.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Advanced/03/world.py)

## Run

```bash
uv run python examples/puzzles/Advanced/03/world.py
```

## Expected output

```text
Fewest-stops route: Depot -> Old Town -> Central -> Museum -> Riverside -> Airport (5 stops)
```

!!! note "Finish line"
    This puzzle does not add a new algorithm. It checks that your [breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search) implementation still feels reliable once the network is larger and visually denser.

## Back to overview

[Puzzles Overview](../index.md)
