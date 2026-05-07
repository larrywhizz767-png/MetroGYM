from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from metrogym import Color, MetroSystem, TrainAgent, TrainObservation, train
from metrogym.core.coordinates import to_position
from metrogym.primitives import Line, Network, Station, Train

CURRENT_DIR = Path(__file__).resolve().parent
SOLVER_PATH = CURRENT_DIR / "solver.py"
SOLVER_SPEC = spec_from_file_location(f"{CURRENT_DIR.parent.name}_{CURRENT_DIR.name}_solver", SOLVER_PATH)
if SOLVER_SPEC is None or SOLVER_SPEC.loader is None:
    raise ImportError(f"Cannot load solver module from {SOLVER_PATH}")
solver_module = module_from_spec(SOLVER_SPEC)
SOLVER_SPEC.loader.exec_module(solver_module)
solve_puzzle = solver_module.solve_puzzle

STATIONS = {
    "Depot": (70, 240),
    "Old Town": (150, 210),
    "Central": (250, 220),
    "University": (250, 80),
    "Museum": (360, 170),
    "Riverside": (450, 230),
    "Tech Park": (470, 100),
    "Airport": (620, 80),
    "South Gate": (250, 380),
    "Stadium": (360, 340),
    "Junction 7": (530, 320),
    "Harbour": (620, 250),
}
LINES = {
    "Red": ["Depot", "Old Town", "Central", "Riverside", "Harbour"],
    "Blue": ["University", "Central", "Tech Park", "Airport"],
    "Green": ["Central", "Museum", "Tech Park"],
    "Purple": ["Central", "South Gate", "Stadium", "Junction 7", "Harbour"],
    "Orange": ["Old Town", "South Gate", "Stadium", "Museum"],
    "Teal": ["Museum", "Riverside", "Junction 7", "Airport"],
}
TRAVEL_MINUTES = {
    frozenset({"Depot", "Old Town"}): 4,
    frozenset({"Old Town", "Central"}): 4,
    frozenset({"Central", "Riverside"}): 5,
    frozenset({"Riverside", "Harbour"}): 4,
    frozenset({"University", "Central"}): 3,
    frozenset({"Central", "Tech Park"}): 6,
    frozenset({"Tech Park", "Airport"}): 4,
    frozenset({"Central", "Museum"}): 2,
    frozenset({"Museum", "Tech Park"}): 2,
    frozenset({"Central", "South Gate"}): 5,
    frozenset({"South Gate", "Stadium"}): 2,
    frozenset({"Stadium", "Junction 7"}): 4,
    frozenset({"Junction 7", "Harbour"}): 3,
    frozenset({"Old Town", "South Gate"}): 3,
    frozenset({"Stadium", "Museum"}): 3,
    frozenset({"Museum", "Riverside"}): 3,
    frozenset({"Riverside", "Junction 7"}): 2,
    frozenset({"Junction 7", "Airport"}): 5,
    frozenset({"Harbour", "Airport"}): 11,
    frozenset({"University", "Museum"}): 5,
}
START = "Depot"
GOAL = "Airport"


class RouteReplaySolver(TrainAgent):
    """Animate the route returned by the Dijkstra solver."""

    def __init__(self, route: list[str], *, dwell_ticks: int = 2):
        self.route = route
        self.dwell_ticks = dwell_ticks
        self._checkpoints = [to_position(STATIONS[name]) for name in route]
        self.reset()

    def reset(self) -> None:
        self._remaining_hold = 0
        self._next_stop_index = 1

    def act(self, observation: TrainObservation):
        if self._remaining_hold > 0:
            self._remaining_hold -= 1
            return train.hold(reason=f"dwelling at {self.route[self._next_stop_index - 1]}")
        if self._next_stop_index >= len(self._checkpoints):
            return train.hold(reason=f"arrived at {self.route[-1]}")
        if observation.self.position == self._checkpoints[self._next_stop_index]:
            stop_name = self.route[self._next_stop_index]
            self._remaining_hold = self.dwell_ticks
            self._next_stop_index += 1
            return train.hold(reason=f"Dijkstra reached {stop_name}")
        return train.proceed_at(1.0, reason="following fastest route")


def build_system(*, tick_ms: int = 280, render_scale: int | float = 2) -> MetroSystem:
    """Build the Dijkstra world for puzzle 01.

    The puzzle inputs live in `world.py` and are passed into `solver.py`.
    Students only edit the route logic.
    """
    route, _total_minutes = solve_puzzle(TRAVEL_MINUTES, START, GOAL)
    solver = RouteReplaySolver(route)
    return MetroSystem(name="Puzzle Advanced 1: Fastest Route Dijkstra", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Red", Color.RED, [STATIONS[name] for name in LINES["Red"]]),
            Line("Blue", Color.BLUE, [STATIONS[name] for name in LINES["Blue"]]),
            Line("Green", Color.GREEN, [STATIONS[name] for name in LINES["Green"]]),
            Line("Purple", Color.PURPLE, [STATIONS[name] for name in LINES["Purple"]]),
            Line("Orange", Color(255, 140, 0), [STATIONS[name] for name in LINES["Orange"]]),
            Line("Teal", Color(0, 170, 170), [STATIONS[name] for name in LINES["Teal"]]),
            Line("Dijkstra Route", Color.HIGHLIGHT, [STATIONS[name] for name in route]),
            *(Station(name, position, radius=10 if name in {"Central", "Museum", "Tech Park", "Stadium", "Junction 7"} else 8) for name, position in STATIONS.items()),
        ]),
        Train("Dijkstra", line="Dijkstra Route", solver=solver, asset="metro_nose", speed=1),
    ])


def main() -> None:
    route, total_minutes = solve_puzzle(TRAVEL_MINUTES, START, GOAL)
    print("Fastest route:", " -> ".join(route))
    print("Journey time:", total_minutes, "minutes")
    build_system().fit().run()


if __name__ == "__main__":
    main()
