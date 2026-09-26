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
    "Airport": (80, 220),
    "Central": (160, 220),
    "Depot": (240, 220),
    "Garden": (320, 220),
    "Museum": (400, 220),
    "School": (480, 220),
    "Stadium": (560, 220),
    "West": (640, 220),
}
ORDERED_STATION_DATA = ["Airport", "Central", "Depot", "Garden", "Museum", "School", "Stadium", "West"]
TARGET = "Museum"


class SearchReplaySolver(TrainAgent):
    """Animate the stations inspected by the binary search."""

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
            return train.hold(reason=f"binary search checked {stop_name}")
        return train.proceed_at(1.0, reason="following binary-search checks")


def build_system(*, tick_ms: int = 350, render_scale: int | float = 2) -> MetroSystem:
    """Build the teaching world for the binary-search puzzle.

    The sorted data lives in `world.py` and is passed into `solver.py`.
    Students only need to work on the search logic.
    """
    inspected_stations = solve_puzzle(ORDERED_STATION_DATA, TARGET)
    solver = SearchReplaySolver(inspected_stations)
    return MetroSystem(name="Puzzle Basic 2: Binary Search", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Ordered Station Data", Color.BLUE, [STATIONS[name] for name in ORDERED_STATION_DATA]),
            Line("Search Checks", Color.HIGHLIGHT, [STATIONS[name] for name in inspected_stations]),
            *(Station(name, STATIONS[name]) for name in ORDERED_STATION_DATA),
        ]),
        Train("Search", line="Search Checks", solver=solver, asset="metro_nose", speed=1),
    ])


def main() -> None:
    inspected_stations = solve_puzzle(ORDERED_STATION_DATA, TARGET)
    print("Binary search checks:", " -> ".join(inspected_stations))
    build_system().fit().run()


if __name__ == "__main__":
    main()
