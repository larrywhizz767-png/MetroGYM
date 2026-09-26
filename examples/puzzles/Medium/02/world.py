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
    "Stadium": (80, 180),
    "Junction": (220, 180),
    "Museum": (360, 180),
    "Harbour": (500, 180),
    "Hilltop": (220, 80),
    "Riverside": (360, 300),
    "Tech Park": (500, 300),
}
GRAPH = {
    "Stadium": ["Junction"],
    "Junction": ["Stadium", "Museum", "Hilltop", "Riverside"],
    "Museum": ["Junction", "Harbour", "Riverside"],
    "Harbour": ["Museum", "Tech Park"],
    "Hilltop": ["Junction"],
    "Riverside": ["Junction", "Museum", "Tech Park"],
    "Tech Park": ["Riverside", "Harbour"],
}
START = "Stadium"
TARGET = "Harbour"


class RouteReplaySolver(TrainAgent):
    """Animate the shortest path returned by the BFS solver."""

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
        return train.proceed_at(1.0, reason="following shortest path found by BFS")


def build_system(*, tick_ms: int = 320, render_scale: int | float = 2) -> MetroSystem:
    """Build the world for the breadth-first search challenge.

    The puzzle inputs live in `world.py` and are passed into `solver.py`.
    Students only edit the route logic.
    """
    route = solve_puzzle(GRAPH, START, TARGET)
    solver = RouteReplaySolver(route)
    return MetroSystem(name="Puzzle Medium 2: Breadth-First Search", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Red", Color.RED, [STATIONS["Stadium"], STATIONS["Junction"], STATIONS["Museum"], STATIONS["Harbour"]]),
            Line("Green", Color.GREEN, [STATIONS["Hilltop"], STATIONS["Junction"], STATIONS["Riverside"], STATIONS["Tech Park"]]),
            Line("Blue", Color.BLUE, [STATIONS["Museum"], STATIONS["Riverside"]]),
            Line("Gold", Color.YELLOW, [STATIONS["Harbour"], STATIONS["Tech Park"]]),
            Line("BFS Route", Color.HIGHLIGHT, [STATIONS[name] for name in route]),
            Station("Stadium", STATIONS["Stadium"]),
            Station("Junction", STATIONS["Junction"], radius=10),
            Station("Museum", STATIONS["Museum"], radius=10),
            Station("Harbour", STATIONS["Harbour"]),
            Station("Hilltop", STATIONS["Hilltop"]),
            Station("Riverside", STATIONS["Riverside"], radius=10),
            Station("Tech Park", STATIONS["Tech Park"]),
        ]),
        Train("BFS", line="BFS Route", solver=solver, asset="metro_nose", speed=1),
    ])


def main() -> None:
    route = solve_puzzle(GRAPH, START, TARGET)
    print("Target station:", TARGET)
    print("Shortest BFS path:", " -> ".join(route))
    build_system().fit().run()


if __name__ == "__main__":
    main()
