# Student Challenges

Three graph-search challenges on pre-built networks. You only write
`solve(graph, src, dst) -> list[str]`. The framework verifies the answer
against the optimal solution and animates your route on the simulator.

| # | Level  | Algorithm | Env                | File                              |
|---|--------|-----------|--------------------|-----------------------------------|
| 1 | Easy   | BFS       | 6-station grid     | `challenges/01_easy_bfs.py`       |
| 2 | Medium | Dijkstra  | 8-station weighted | `challenges/02_medium_dijkstra.py`|
| 3 | Hard   | A*        | London tube (12 st)| `challenges/03_hard_astar.py`     |

Run a challenge:

```bash
cd python
uv run python challenges/01_easy_bfs.py
```

The terminal prints ✅/❌ and the optimal cost; then a window opens with:

- every tube line dimmed in the background,
- every station drawn (endpoints enlarged),
- **your route in gold** with a single gold train animating it.

## The `Graph` you get

```python
@dataclass(frozen=True)
class Graph:
    stations: dict[str, tuple[int, int]]          # name -> (x, y)
    edges: dict[frozenset[str, str], float]        # unordered pair -> weight
    lines: dict[str, list[str]]                    # for rendering only
    colors: dict[str, java.awt.Color]              # for rendering only

    graph.neighbours(name) -> [(neighbour, weight), ...]   # sorted
    graph.weight(a, b)     -> float                        # raises KeyError if no edge
```

## What you must return

A `list[str]` of station names from `src` to `dst` (both inclusive). Every
consecutive pair must exist as an edge. The framework then:

- sums edge weights for your route,
- computes the ground-truth optimum (BFS for easy, Dijkstra for medium/hard),
- verifies your cost equals the optimum (or hop count for easy).

## Rules

- **No external libraries** beyond the Python stdlib. Use `collections.deque`,
  `heapq`, `math`. No `networkx`.
- **Don't modify** `challenges/framework.py` or `challenges/envs.py`.
- Your algorithm must work for *any* `src`/`dst`, not just the ones in `__main__`.
  Try changing them and re-running.

## Stretch goals

- **Easy →** report *all* shortest-hop paths, not just one.
- **Medium →** support disruption: given a closed edge `("N1","Hub")`, re-plan.
- **Hard →** instrument your A* to count expanded nodes and compare with Dijkstra.
  Extra credit: make the heuristic inadmissible (e.g. multiply by 1.5) and
  observe when the result is no longer optimal.

## Reference solutions

Instructor-only references live in `challenges/solutions/`. Don't peek. 🙈
