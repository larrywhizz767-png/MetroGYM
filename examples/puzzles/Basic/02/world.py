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
    "West": (80, 220),
    "Central": (280, 220),
    "East": (480, 220),
    "North": (280, 80),
    "South": (280, 360),
    "Airport": (600, 80),
}
GRAPH = {
    "West": ["Central"],
    "Central": ["West", "East", "North", "South", "Airport"],
    "East": ["Central"],
    "North": ["Central"],
    "South": ["Central"],
    "Airport": ["Central"],
}
START = "West"
GOAL = "Airport"


class RouteReplaySolver(TrainAgent):
    """Animate the route returned by the BFS solver."""

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
        return train.proceed_at(1.0, reason="following BFS route")


def build_system(*, tick_ms: int = 350, render_scale: int | float = 2) -> MetroSystem:
    """Build the world for the fewest-stops BFS puzzle.

    The puzzle data lives in `world.py` and is passed into `solver.py`.
    Students only need to work on the route logic.
    """
    route = solve_puzzle(GRAPH, START, GOAL)
    solver = RouteReplaySolver(route)
    return MetroSystem(name="Puzzle Basic 2: Fewest Stops BFS", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Red", Color.RED, [STATIONS["West"], STATIONS["Central"], STATIONS["East"]]),
            Line("Green", Color.GREEN, [STATIONS["North"], STATIONS["Central"], STATIONS["South"]]),
            Line("Blue", Color.BLUE, [STATIONS["Central"], STATIONS["Airport"]]),
            Line("BFS Route", Color.HIGHLIGHT, [STATIONS[name] for name in route]),
            Station("West", STATIONS["West"]),
            Station("Central", STATIONS["Central"], radius=10),
            Station("East", STATIONS["East"]),
            Station("North", STATIONS["North"]),
            Station("South", STATIONS["South"]),
            Station("Airport", STATIONS["Airport"]),
        ]),
        Train("BFS", line="BFS Route", solver=solver, asset="metro_nose", speed=1),
    ])


def main() -> None:
    route = solve_puzzle(GRAPH, START, GOAL)
    print("Fewest-stops route:", " -> ".join(route), f"({len(route) - 1} stops)")
    build_system().fit().run()


if __name__ == "__main__":
    main()
