---
icon: lucide/git-compare-arrows
---

# Medium 02 — Blocked-track diversion

The stations remain open, but a direct segment is blocked. This time the forbidden object is an edge rather than a node, so your search must skip specific station pairs while still exploring the rest of the graph.

## Mission brief

| Item | Value |
|---|---|
| Difficulty | Medium |
| Start | `Stadium` |
| Goal | `Harbour` |
| Blocked track | `Museum - Harbour` |
| Main skill | Reject forbidden edges while keeping valid neighbours |

## Files

- Edit: [`examples/puzzles/Medium/02/solver.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Medium/02/solver.py)
- Reference world: [`examples/puzzles/Medium/02/world.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Medium/02/world.py)

## Run

```bash
uv run python examples/puzzles/Medium/02/world.py
```

## Expected output

```text
Blocked track: Museum - Harbour
Diversion route: Stadium -> Junction -> Riverside -> Tech Park -> Harbour
```

!!! tip "Mental model"
    The optimisation target is unchanged from the earlier [breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search) puzzle. Only the legal move set has changed.

## Next puzzle

[Advanced 01 — Fastest route](../advanced/01-fastest-route.md)
