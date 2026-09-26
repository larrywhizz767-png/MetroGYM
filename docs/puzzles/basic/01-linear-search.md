---
icon: lucide/search-code
---

# Basic 01 — Linear Search

Search an unsorted data set for Museum. A linear search starts at the first
item, inspects one item at a time, and stops at the first match.

## Mission brief

| Item | Value |
|---|---|
| Difficulty | Basic |
| Target | Museum |
| Core data | `['Harbour', 'School', 'Library', 'Depot', 'Museum']` |
| Main skill | Inspect values from the beginning until the target is found |

!!! tip "Why linear search?"
    Linear search works with ordered and unordered data. In this puzzle the
    data is deliberately not alphabetically ordered, so each item before
    Museum must be checked.

## Files

- Edit: [examples/puzzles/Basic/01/solver.py](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Basic/01/solver.py)
- Reference world: [examples/puzzles/Basic/01/world.py](https://github.com/larrywhizz767-png/MetroGYM/blob/main/examples/puzzles/Basic/01/world.py)

## Run

~~~bash
uv run python examples/puzzles/Basic/01/world.py
~~~

## Expected output

~~~text
Linear search checks: Harbour -> School -> Library -> Depot -> Museum
~~~

## Further reading

[BBC Bitesize: Linear search](https://www.bbc.co.uk/bitesize/guides/zjdkw6f/revision/3)

## Next puzzle

[Basic 02 — Binary Search](02-binary-search.md)
