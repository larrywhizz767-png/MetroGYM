---
icon: lucide/compass
---

# Basic 01 — Single-line route

You are given one metro line in travel order and must return every station visited between the start and the goal. No graph search is needed yet, but this puzzle establishes the route format used everywhere else in the ladder.

## Mission brief

| Item | Value |
|---|---|
| Difficulty | Basic |
| Start | `Depot` |
| Goal | `Museum` |
| Core data | `LINE_ORDER = ["Depot", "School", "Library", "Museum", "Harbour"]` |
| What you optimise | Nothing yet; return the correct ordered slice |

!!! tip "What you are really practising"
    Representing a route as a list of station names in travel order.

## Files

- Edit: [`examples/puzzles/Basic/01/solver.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Basic/01/solver.py)
- Reference world: [`examples/puzzles/Basic/01/world.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Basic/01/world.py)

## Run

```bash
uv run python examples/puzzles/Basic/01/world.py
```

## Expected output

```text
Single-line route: Depot -> School -> Library -> Museum
```

## Success signal

The highlighted route should follow the single shuttle line from `Depot` to `Museum` with no detours and no missing stations.

## Next puzzle

[Basic 02 — Fewest stops](02-fewest-stops.md)
