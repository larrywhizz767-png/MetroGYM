from __future__ import annotations

from metrogym import Color, MetroSystem, SignalAgent, SignalObservation, TrainAgent, TrainObservation, signal, train
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train

STATIONS: dict[str, tuple[int, int]] = {
    "Times Sq": (305, 190),
    "Grand Central": (415, 190),
    "Union Sq": (395, 300),
    "Brooklyn Br": (430, 405),
    "Wall St": (430, 465),
    "Columbus Circle": (235, 120),
    "Penn Station": (290, 245),
    "W 4 St": (310, 330),
    "Jay St": (470, 470),
    "Atlantic Av": (560, 420),
    "Court Sq": (530, 180),
    "Queensboro": (500, 115),
    "Jackson Hts": (640, 110),
    "Fulton St": (420, 440),
    "Yard": (650, 500),
}

NYC_RED = Color(238, 53, 46)
NYC_GREEN = Color(0, 147, 60)
NYC_BLUE = Color(0, 57, 166)
NYC_ORANGE = Color(255, 99, 25)
NYC_PURPLE = Color(185, 51, 173)
NYC_GREY = Color(167, 169, 172)
NYC_YELLOW = Color(255, 211, 0)


def s(name: str) -> tuple[int, int]:
    return STATIONS[name]


def shuttle(*names: str) -> list[tuple[int, int]]:
    points = [s(name) for name in names]
    return [*points, *reversed(points[1:-1]), points[0]]


def loop(*names: str) -> list[tuple[int, int]]:
    points = [s(name) for name in names]
    return [*points, points[0]]


class BoroughDispatchSolver(SignalAgent):
    def __init__(self, approach_distance: float = 55.0, release_distance: float = 90.0, red_hold_ticks: int = 4):
        self.dispatch = signal.priority_queue(
            approach_distance=approach_distance,
            release_distance=release_distance,
            red_hold_ticks=red_hold_ticks,
        )

    def reset(self) -> None:
        self.dispatch.reset()

    def act(self, observation: SignalObservation):
        return self.dispatch(observation)


class NYCMaintenanceSolver(TrainAgent):
    def __init__(self):
        self.safety = train.all_of(
            train.respect_signals(approach_distance=55.0),
            train.avoid_collisions(min_distance=70.0),
        )

    def act(self, observation: TrainObservation):
        current_train = observation.self
        if observation.collision_events and current_train.id == "MOW":
            return train.proceed(reason="maintenance keeps moving toward incidents")
        if observation.collision_events:
            return train.hold(reason="network collision response")
        return self.safety(observation)


def build_system(*, tick_ms: int = 320, render_scale: int | float = 2) -> MetroSystem:
    interchanges = {"Times Sq", "Grand Central", "Union Sq", "Fulton St", "Jay St", "Atlantic Av"}
    stations = [Station(name, pos, radius=9 if name in interchanges else 6) for name, pos in STATIONS.items()]
    train_solver = NYCMaintenanceSolver()
    court_dispatch = BoroughDispatchSolver(approach_distance=35.0, release_distance=75.0)
    atlantic_dispatch = BoroughDispatchSolver(approach_distance=40.0, release_distance=80.0)
    w4_dispatch = BoroughDispatchSolver(approach_distance=50.0, release_distance=85.0)
    return MetroSystem(name="City Reproduction: NYC Subway", tick_ms=tick_ms, size=(720, 540), render_scale=render_scale).pipeline([
        Network([
            Line("1/2/3 Broadway", NYC_RED, shuttle("Columbus Circle", "Times Sq", "Penn Station", "W 4 St", "Fulton St", "Wall St")),
            Line("4/5/6 Lexington", NYC_GREEN, shuttle("Grand Central", "Union Sq", "Brooklyn Br", "Wall St")),
            Line("A/C/E 8 Avenue", NYC_BLUE, shuttle("Columbus Circle", "Penn Station", "W 4 St", "Jay St")),
            Line("B/D/F/M 6 Avenue", NYC_ORANGE, shuttle("Times Sq", "W 4 St", "Jay St", "Atlantic Av")),
            Line("7 Flushing", NYC_PURPLE, shuttle("Times Sq", "Grand Central", "Court Sq", "Queensboro", "Jackson Hts")),
            Line("G Crosstown", NYC_GREY, loop("Court Sq", "Jay St", "Atlantic Av", "Union Sq")),
            Line("Maintenance of Way", NYC_YELLOW, shuttle("Yard", "Atlantic Av", "Jay St", "Fulton St")),
            *stations,
        ]),
        Train("123", line="1/2/3 Broadway", solver=train_solver, asset="metro_nose"),
        Train("456", line="4/5/6 Lexington", solver=train_solver, asset="bullet_metro"),
        Train("ACE", line="A/C/E 8 Avenue", solver=train_solver, asset="city_tram"),
        Train("BDFM", line="B/D/F/M 6 Avenue", solver=train_solver, asset="metro_nose"),
        Train("7", line="7 Flushing", solver=train_solver, asset="bullet_metro"),
        Train("G", line="G Crosstown", solver=train_solver, asset="city_tram"),
        Train("MOW", line="Maintenance of Way", solver=train_solver, asset="maintenance"),
        Signal("Court Sq Dispatch", (555, 170), label="Court", controls=[ControlRule("7 Flushing", s("Grand Central"), s("Court Sq")), ControlRule("G Crosstown", s("Court Sq"), s("Jay St"))], solver=court_dispatch),
        Signal("Atlantic Av Dispatch", (585, 445), label="Atlantic", controls=[ControlRule("B/D/F/M 6 Avenue", s("Jay St"), s("Atlantic Av")), ControlRule("G Crosstown", s("Jay St"), s("Atlantic Av")), ControlRule("Maintenance of Way", s("Yard"), s("Atlantic Av"))], solver=atlantic_dispatch),
        Signal("W 4 St Dispatch", (275, 315), label="W4", controls=[ControlRule("1/2/3 Broadway", s("Penn Station"), s("W 4 St")), ControlRule("A/C/E 8 Avenue", s("Penn Station"), s("W 4 St")), ControlRule("B/D/F/M 6 Avenue", s("Times Sq"), s("W 4 St"))], solver=w4_dispatch),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
