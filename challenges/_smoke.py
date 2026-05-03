"""Instructor sanity test: runs the three reference solvers against their
envs and asserts the checker reports optimal. Run from the repository root:

    uv run python challenges/_smoke.py
"""
import importlib.util
import pathlib
import sys

from metrogym.runtimes import RuntimeSimulator

RuntimeSimulator.show = lambda self, **kw: None

from envs import easy_graph, london_graph, medium_graph
from framework import check


def load(path: str):
    spec = importlib.util.spec_from_file_location(pathlib.Path(path).stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cases = [
    ("challenges/solutions/01_easy_bfs.py",        easy_graph(),   "A", "F", "bfs"),
    ("challenges/solutions/02_medium_dijkstra.py", medium_graph(), "N1", "S2", "dijkstra"),
    ("challenges/solutions/03_hard_astar.py",      london_graph(), "Paddington", "Waterloo", "dijkstra"),
]

bad = 0
for path, g, s, d, mode in cases:
    mod = load(path)
    route = mod.solve(g, s, d)
    r = check(g, s, d, route, mode=mode)
    ok = "✅" if r.ok else "❌"
    print(f"{ok} {path}: cost={r.total_cost} optimal={r.optimal_cost} route={route}")
    if not r.ok:
        bad += 1

sys.exit(1 if bad else 0)
