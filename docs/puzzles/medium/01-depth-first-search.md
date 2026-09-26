---
icon: lucide/git-branch
---

# Medium 01 — Depth-first search

The network now branches and contains cycles. Starting at `Depot`, find
`Harbour` by exploring one route as far as possible before backtracking. Your
solver must return the complete station path to the target.

You may solve the puzzle with an explicit stack or with recursion. Both are
valid implementations of [depth-first search](https://en.wikipedia.org/wiki/Depth-first_search).

## Mission brief

| Item | Value |
|---|---|
| Difficulty | Medium |
| Start | `Depot` |
| Target | `Harbour` |
| Network size | 6 stations |
| Required output | One valid path from the start to the target |
| Main skill | Explore deeply, track visited stations, and backtrack when needed |

!!! note "DFS does not promise the shortest path"
    The path returned by DFS depends on the order in which neighbouring
    stations are explored. A shorter route may exist even when the returned
    DFS path is completely correct.

## Files

- Edit: [`examples/puzzles/Medium/01/solver.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Medium/01/solver.py)
- Reference world: [`examples/puzzles/Medium/01/world.py`](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Medium/01/world.py)

## Run

```bash
uv run python examples/puzzles/Medium/01/world.py
```

## Expected output

With the neighbour order supplied by the puzzle, the path is:

```text
Target station: Harbour
DFS path: Depot -> Market -> Museum -> Garden -> Harbour
```

??? tip "Iterative or recursive?"
    An iterative DFS stores paths on a last-in, first-out stack. A recursive
    DFS uses the call stack and returns the successful path through its nested
    calls. Whichever approach you choose, keep a set of visited stations so a
    cycle cannot trap the search.

## Next puzzle

[Medium 02 — Breadth-first search](02-breadth-first-search.md)
