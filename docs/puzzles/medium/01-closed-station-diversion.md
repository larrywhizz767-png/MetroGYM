---
icon: lucide/circle-x
---

# Medium 01 — Closed-station diversion

One station is unavailable, but the destination is still reachable. You now need the fewest-stop route that avoids every station listed in `closed_stations`.

## Mission brief

| Item | Value |
|---|---|
| Difficulty | Medium |
| Start | `Depot` |
| Goal | `Harbour` |
| Closed station | `Museum` |
| Main skill | Filter forbidden nodes during [breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search) expansion |

## Files

- Edit: [`examples/puzzles/Medium/01/solver.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Medium/01/solver.py)
- Reference world: [`examples/puzzles/Medium/01/world.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Medium/01/world.py)

## Run

```bash
uv run python examples/puzzles/Medium/01/world.py
```

## Expected output

```text
Closed station: Museum
Diversion route: Depot -> Market -> College -> Garden -> Harbour
```

!!! warning "Common failure mode"
    Do not merely avoid stopping at `Museum`; the search must behave as if that station does not exist in the frontier at all.

## Next puzzle

[Medium 02 — Blocked-track diversion](02-blocked-track-diversion.md)
