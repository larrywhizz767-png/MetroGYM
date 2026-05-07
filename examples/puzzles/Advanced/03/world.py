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
    "Canal": (320, 225),
    "Exchange": (390, 228),
    "Riverside": (460, 230),
    "University": (250, 80),
    "Innovation": (360, 80),
    "Tech Park": (470, 100),
    "Skyport": (550, 90),
    "Airport": (620, 80),
    "Museum": (360, 170),
    "Civic Centre": (420, 145),
    "South Gate": (250, 380),
    "Stadium": (360, 340),
    "Junction 7": (530, 320),
    "Harbour": (620, 250),
}
LINES = {
    "Red": ["Depot", "Old Town", "Central", "Canal", "Exchange", "Riverside", "Harbour"],
    "Blue": ["University", "Central", "Innovation", "Tech Park", "Skyport", "Airport"],
    "Green": ["Central", "Museum", "Civic Centre", "Tech Park"],
    "Purple": ["Central", "South Gate", "Stadium", "Junction 7", "Harbour"],
    "Orange": ["Old Town", "South Gate", "Stadium", "Museum"],
    "Teal": ["Museum", "Riverside", "Junction 7", "Airport"],
    "Silver": ["Stadium", "Riverside", "Airport"],
}
GRAPH = {
    "Depot": ["Old Town"],
    "Old Town": ["Depot", "Central", "South Gate"],
    "Central": ["Old Town", "Canal", "University", "Museum", "South Gate"],
    "Canal": ["Central", "Exchange"],
    "Exchange": ["Canal", "Riverside"],
    "Riverside": ["Exchange", "Harbour", "Museum", "Stadium", "Airport"],
    "University": ["Central", "Innovation"],
    "Innovation": ["University", "Tech Park"],
    "Tech Park": ["Innovation", "Skyport", "Civic Centre"],
    "Skyport": ["Tech Park", "Airport"],
    "Airport": ["Skyport", "Junction 7", "Riverside"],
    "Museum": ["Central", "Civic Centre", "Stadium", "Riverside"],
    "Civic Centre": ["Museum", "Tech Park"],
    "South Gate": ["Old Town", "Central", "Stadium"],
    "Stadium": ["South Gate", "Junction 7", "Museum", "Riverside"],
    "Junction 7": ["Stadium", "Harbour", "Airport"],
    "Harbour": ["Riverside", "Junction 7"],
}
START = "Depot"
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
        return train.proceed_at(1.0, reason="following fewest-stops route")


def build_system(*, tick_ms: int = 260, render_scale: int | float = 2) -> MetroSystem:
    """Build the world for the advanced fewest-stops challenge.

    The puzzle inputs live in `world.py` and are passed into `solver.py`.
    Students only edit the route logic.
    """
    route = solve_puzzle(GRAPH, START, GOAL)
    solver = RouteReplaySolver(route)
    return MetroSystem(name="Puzzle Advanced 3: Lowest Stops Variant", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("BFS Route", Color.BACKGROUND, [STATIONS[name] for name in route]),
            Line("Red", Color.RED, [STATIONS[name] for name in LINES["Red"]]),
            Line("Blue", Color.BLUE, [STATIONS[name] for name in LINES["Blue"]]),
            Line("Green", Color.GREEN, [STATIONS[name] for name in LINES["Green"]]),
            Line("Purple", Color.PURPLE, [STATIONS[name] for name in LINES["Purple"]]),
            Line("Orange", Color(255, 140, 0), [STATIONS[name] for name in LINES["Orange"]]),
            Line("Teal", Color(0, 170, 170), [STATIONS[name] for name in LINES["Teal"]]),
            Line("Silver", Color(180, 180, 200), [STATIONS[name] for name in LINES["Silver"]]),
            *(Station(name, position, radius=10 if name in {"Central", "Riverside", "Museum", "Tech Park", "South Gate", "Stadium"} else 8) for name, position in STATIONS.items()),
        ]),
        Train("BFS", line="BFS Route", solver=solver, asset="metro_nose", speed=1),
    ])


def main() -> None:
    route = solve_puzzle(GRAPH, START, GOAL)
    print("Fewest-stops route:", " -> ".join(route), f"({len(route) - 1} stops)")
    build_system().fit().run()


if __name__ == "__main__":
    main()
