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
    "Depot": (80, 220),
    "Market": (200, 220),
    "Museum": (320, 220),
    "Garden": (440, 220),
    "Harbour": (560, 220),
    "College": (320, 100),
    "Arena": (320, 340),
}
GRAPH = {
    "Depot": ["Market"],
    "Market": ["Depot", "Museum", "College"],
    "Museum": ["Market", "Garden", "College", "Arena"],
    "Garden": ["Museum", "Harbour", "Arena", "College"],
    "Harbour": ["Garden"],
    "College": ["Market", "Museum", "Garden"],
    "Arena": ["Museum", "Garden"],
}
CLOSED_STATIONS = ["Museum"]
START = "Depot"
GOAL = "Harbour"


class RouteReplaySolver(TrainAgent):
    """Animate the diversion route returned by the BFS solver."""

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
            return train.hold(reason=f"BFS reached {stop_name}")
        return train.proceed_at(1.0, reason="following diversion found by BFS")


def build_system(*, tick_ms: int = 320, render_scale: int | float = 2) -> MetroSystem:
    """Build the world for the closed-station BFS challenge.

    The puzzle inputs live in `world.py` and are passed into `solver.py`.
    Students only edit the route logic.
    """
    route = solve_puzzle(GRAPH, CLOSED_STATIONS, START, GOAL)
    solver = RouteReplaySolver(route)
    return MetroSystem(name="Puzzle Medium 1: BFS With Closed Station", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Orange", Color(255, 140, 0), [STATIONS["Depot"], STATIONS["Market"], STATIONS["Museum"], STATIONS["Garden"], STATIONS["Harbour"]]),
            Line("Silver", Color(180, 180, 200), [STATIONS["College"], STATIONS["Museum"], STATIONS["Arena"]]),
            Line("Teal", Color(0, 170, 170), [STATIONS["Market"], STATIONS["College"]]),
            Line("Purple", Color.PURPLE, [STATIONS["Garden"], STATIONS["Arena"]]),
            Line("Bypass", Color.YELLOW, [STATIONS["College"], STATIONS["Garden"]]),
            Line("BFS Route", Color.HIGHLIGHT, [STATIONS[name] for name in route]),
            Station("Depot", STATIONS["Depot"]),
            Station("Market", STATIONS["Market"], radius=10),
            Station("Museum", STATIONS["Museum"], radius=10),
            Station("Garden", STATIONS["Garden"], radius=10),
            Station("Harbour", STATIONS["Harbour"]),
            Station("College", STATIONS["College"]),
            Station("Arena", STATIONS["Arena"]),
        ]),
        Train("BFS", line="BFS Route", solver=solver, asset="metro_nose", speed=1),
    ])


def main() -> None:
    route = solve_puzzle(GRAPH, CLOSED_STATIONS, START, GOAL)
    print("Closed station:", ", ".join(CLOSED_STATIONS))
    print("Diversion route:", " -> ".join(route))
    build_system().fit().run()


if __name__ == "__main__":
    main()
