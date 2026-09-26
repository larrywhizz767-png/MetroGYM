---
icon: lucide/binary
---

# Basic 02 — Binary Search

Search the ordered station data for Museum. Binary search repeatedly checks
the middle of the remaining range and discards the half that cannot contain the
target.

## Mission brief

| Item | Value |
|---|---|
| Difficulty | Basic |
| Target | Museum |
| Core data | `['Airport', 'Central', 'Depot', 'Garden', 'Museum', 'School', 'Stadium', 'West']` |
| Main skill | Keep lower and upper bounds for an ordered data set |

!!! warning "The data must be ordered"
    Binary search only works when the data is ordered. The station names here
    are in ascending alphabetical order.

## Files

- Edit: [examples/puzzles/Basic/02/solver.py](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Basic/02/solver.py)
- Reference world: [examples/puzzles/Basic/02/world.py](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Basic/02/world.py)

## Run

~~~bash
uv run python examples/puzzles/Basic/02/world.py
~~~

## Expected output

~~~text
Binary search checks: Garden -> School -> Museum
~~~

## Further reading

[BBC Bitesize: Binary search](https://www.bbc.co.uk/bitesize/guides/zjdkw6f/revision/2)

## Next puzzle

[Medium 01 — Depth-first search](../medium/01-depth-first-search.md)
