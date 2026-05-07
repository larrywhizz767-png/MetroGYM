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
    "West Depot": (60, 260),
    "Old Town": (150, 240),
    "Central": (250, 240),
    "Museum": (360, 200),
    "Harbour": (620, 260),
    "North Park": (250, 90),
    "Airport": (620, 90),
    "South Gate": (250, 390),
    "Tech Park": (470, 90),
    "Stadium": (360, 350),
    "Science Hub": (470, 350),
    "University": (360, 90),
    "Riverside": (470, 240),
    "Market": (150, 350),
}
LINES = {
    "Red": ["West Depot", "Old Town", "Central", "Museum", "Harbour"],
    "Blue": ["North Park", "Central", "University", "Tech Park", "Airport"],
    "Green": ["Central", "South Gate", "Stadium", "Science Hub", "Harbour"],
    "Purple": ["Museum", "University", "Airport"],
    "Gold": ["Old Town", "Market", "South Gate", "Science Hub"],
    "Silver": ["Museum", "Riverside", "Tech Park"],
    "Teal": ["Riverside", "Science Hub", "Airport"],
}
SEGMENT_MINUTES = {
    ("Red", frozenset({"West Depot", "Old Town"})): 3,
    ("Red", frozenset({"Old Town", "Central"})): 3,
    ("Red", frozenset({"Central", "Museum"})): 3,
    ("Red", frozenset({"Museum", "Harbour"})): 5,
    ("Blue", frozenset({"North Park", "Central"})): 3,
    ("Blue", frozenset({"Central", "University"})): 2,
    ("Blue", frozenset({"University", "Tech Park"})): 2,
    ("Blue", frozenset({"Tech Park", "Airport"})): 3,
    ("Green", frozenset({"Central", "South Gate"})): 2,
    ("Green", frozenset({"South Gate", "Stadium"})): 2,
    ("Green", frozenset({"Stadium", "Science Hub"})): 2,
    ("Green", frozenset({"Science Hub", "Harbour"})): 2,
    ("Purple", frozenset({"Museum", "University"})): 4,
    ("Purple", frozenset({"University", "Airport"})): 6,
    ("Gold", frozenset({"Old Town", "Market"})): 2,
    ("Gold", frozenset({"Market", "South Gate"})): 2,
    ("Gold", frozenset({"South Gate", "Science Hub"})): 3,
    ("Silver", frozenset({"Museum", "Riverside"})): 2,
    ("Silver", frozenset({"Riverside", "Tech Park"})): 2,
    ("Teal", frozenset({"Riverside", "Science Hub"})): 1,
    ("Teal", frozenset({"Science Hub", "Airport"})): 2,
}
TRANSFER_PENALTIES = {
    frozenset({"Red", "Blue"}): 7,
    frozenset({"Red", "Green"}): 8,
    frozenset({"Red", "Purple"}): 7,
    frozenset({"Red", "Silver"}): 2,
    frozenset({"Blue", "Purple"}): 6,
    frozenset({"Blue", "Silver"}): 1,
    frozenset({"Blue", "Teal"}): 8,
    frozenset({"Blue", "Green"}): 6,
    frozenset({"Green", "Gold"}): 2,
    frozenset({"Green", "Teal"}): 4,
    frozenset({"Purple", "Silver"}): 2,
    frozenset({"Silver", "Teal"}): 2,
    frozenset({"Gold", "Red"}): 5,
}
DEFAULT_TRANSFER_PENALTY = 9
START = "West Depot"
GOAL = "Airport"


class RouteReplaySolver(TrainAgent):
    """Animate the route returned by the transfer-aware Dijkstra solver."""

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
            return train.hold(reason=f"transfer-aware Dijkstra reached {stop_name}")
        return train.proceed_at(1.0, reason="following transfer-aware route")


def build_system(*, tick_ms: int = 260, render_scale: int | float = 2) -> MetroSystem:
    """Build the world for the transfer-aware Dijkstra challenge.

    The puzzle inputs live in `world.py` and are passed into `solver.py`.
    Students only edit the route logic.
    """
    route, _total_minutes, _line_route = solve_puzzle(
        LINES,
        SEGMENT_MINUTES,
        TRANSFER_PENALTIES,
        DEFAULT_TRANSFER_PENALTY,
        START,
        GOAL,
    )
    solver = RouteReplaySolver(route)
    return MetroSystem(name="Puzzle Advanced 2: Dijkstra With Transfers", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Dijkstra Route", Color.BACKGROUND, [STATIONS[name] for name in route]),
            Line("Red", Color.RED, [STATIONS[name] for name in LINES["Red"]]),
            Line("Blue", Color.BLUE, [STATIONS[name] for name in LINES["Blue"]]),
            Line("Green", Color.GREEN, [STATIONS[name] for name in LINES["Green"]]),
            Line("Purple", Color.PURPLE, [STATIONS[name] for name in LINES["Purple"]]),
            Line("Gold", Color.YELLOW, [STATIONS[name] for name in LINES["Gold"]]),
            Line("Silver", Color(180, 180, 200), [STATIONS[name] for name in LINES["Silver"]]),
            Line("Teal", Color(0, 170, 170), [STATIONS[name] for name in LINES["Teal"]]),
            *(Station(name, position, radius=10 if name in {"Central", "Museum", "University", "South Gate", "Science Hub", "Riverside", "Tech Park"} else 8) for name, position in STATIONS.items()),
        ]),
        Train("Dijkstra", line="Dijkstra Route", solver=solver, asset="metro_nose", speed=1),
    ])


def main() -> None:
    route, total_minutes, line_route = solve_puzzle(
        LINES,
        SEGMENT_MINUTES,
        TRANSFER_PENALTIES,
        DEFAULT_TRANSFER_PENALTY,
        START,
        GOAL,
    )
    print("Transfer-aware route:", " -> ".join(route))
    print("Lines used:", " -> ".join(line_route))
    print("Journey time with transfer penalties:", total_minutes, "minutes")
    build_system().fit().run()


if __name__ == "__main__":
    main()
