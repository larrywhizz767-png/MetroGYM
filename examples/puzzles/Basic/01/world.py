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
    "Depot": (100, 220),
    "School": (220, 220),
    "Library": (340, 220),
    "Museum": (460, 220),
    "Harbour": (580, 220),
}
LINE_ORDER = ["Depot", "School", "Library", "Museum", "Harbour"]
START = "Depot"
GOAL = "Museum"


class RouteReplaySolver(TrainAgent):
    """Animate the route returned by the solver.

    The world passes in a station-by-station route and this class moves the
    train through that answer.
    """

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
            return train.hold(reason=f"reached {stop_name}")
        return train.proceed_at(1.0, reason="following single-line route")


def build_system(*, tick_ms: int = 400, render_scale: int | float = 2) -> MetroSystem:
    """Build the teaching world for puzzle 01.

    The puzzle inputs live here in `world.py`, while `solver.py` only contains
    the route-finding logic students edit.
    """
    route = solve_puzzle(LINE_ORDER, START, GOAL)
    solver = RouteReplaySolver(route)
    return MetroSystem(name="Puzzle Basic 1: Single Line Route", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("School Shuttle", Color.BLUE, [STATIONS[name] for name in LINE_ORDER]),
            Line("Solved Route", Color.HIGHLIGHT, [STATIONS[name] for name in route]),
            *(Station(name, STATIONS[name]) for name in LINE_ORDER),
        ]),
        Train("Route", line="Solved Route", solver=solver, asset="metro_nose", speed=1),
    ])


def main() -> None:
    route = solve_puzzle(LINE_ORDER, START, GOAL)
    print("Single-line route:", " -> ".join(route))
    build_system().fit().run()


if __name__ == "__main__":
    main()
