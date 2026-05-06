from __future__ import annotations

from metrogym import Color, MetroSystem, SignalAgent, SignalObservation, TrainAgent, TrainObservation, distance_to_rule, signal, train
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train

STATIONS: dict[str, tuple[int, int]] = {
    "Paddington": (70, 180),
    "Baker St": (205, 145),
    "King's Cross": (375, 95),
    "Liverpool St": (650, 210),
    "Oxford Circus": (275, 245),
    "Holborn": (455, 245),
    "Bank": (595, 265),
    "Piccadilly": (300, 335),
    "Westminster": (335, 430),
    "Waterloo": (455, 465),
    "Victoria": (215, 465),
    "London Bridge": (625, 470),
    "Canada Water": (735, 420),
    "Acton Depot": (65, 505),
}

TFL_CENTRAL = Color(220, 36, 31)
TFL_PICCADILLY = Color(0, 25, 168)
TFL_CIRCLE = Color(255, 206, 0)
TFL_VICTORIA = Color(0, 152, 212)
TFL_BAKERLOO = Color(178, 99, 17)
TFL_JUBILEE = Color(160, 165, 169)
SERVICE_YELLOW = Color(255, 206, 0)


def s(name: str) -> tuple[int, int]:
    return STATIONS[name]


def shuttle(*names: str) -> list[tuple[int, int]]:
    points = [s(name) for name in names]
    return [*points, *reversed(points[1:-1]), points[0]]


def loop(*names: str) -> list[tuple[int, int]]:
    points = [s(name) for name in names]
    return [*points, points[0]]


class LondonInterlockingSolver(SignalAgent):
    def __init__(self, approach_distance: float = 45.0, release_distance: float = 80.0, red_hold_ticks: int = 4):
        self.dispatch = signal.priority_queue(
            approach_distance=approach_distance,
            release_distance=release_distance,
            red_hold_ticks=red_hold_ticks,
        )

    def reset(self) -> None:
        self.dispatch.reset()

    def act(self, observation: SignalObservation):
        return self.dispatch(observation)


class LondonTrainSolver(TrainAgent):
    def __init__(self):
        self.safety = train.all_of(
            train.respect_signals(approach_distance=45.0),
            train.avoid_collisions(min_distance=70.0),
        )
        self.approach_distance = 45.0

    def act(self, observation: TrainObservation):
        current_train = observation.self
        if observation.collision_events and current_train.id == "NRM":
            return train.proceed(reason="night response keeps moving")
        if observation.collision_events:
            return train.hold(reason="incident freeze")
        if self._blocked_by_signal(observation):
            return train.hold(reason="interlocking signal blocks entry")
        return self.safety(observation)

    def _blocked_by_signal(self, observation: TrainObservation) -> bool:
        current_train = observation.self
        for rule in observation.signals.ahead:
            if distance_to_rule(current_train, rule) > self.approach_distance:
                continue
            if current_train.next_position.distance(rule.end) <= self.approach_distance:
                continue
            if not rule.signal_green:
                return self._moving_toward_rule_start(current_train, rule)
            if rule.signal_granted_train_id is not None and rule.signal_granted_train_id != current_train.id:
                return self._moving_toward_rule_start(current_train, rule)
            if rule.signal_granted_line is not None and rule.signal_granted_line != current_train.line_name:
                return self._moving_toward_rule_start(current_train, rule)
        return False

    def _moving_toward_rule_start(self, current_train: object, rule: object) -> bool:
        current = current_train.position.distance(rule.start)
        next_distance = current_train.next_position.distance(rule.start)
        return next_distance < current or current <= 1.5


def build_system(*, tick_ms: int = 330, render_scale: int | float = 2) -> MetroSystem:
    train_solver = LondonTrainSolver()
    king_cross_interlock = LondonInterlockingSolver()
    liverpool_interlock = LondonInterlockingSolver()
    waterloo_interlock = LondonInterlockingSolver()
    interchanges = {"Baker St", "King's Cross", "Oxford Circus", "Holborn", "Bank", "Waterloo", "London Bridge"}
    stations = [Station(name, pos, radius=9 if name in interchanges else 6) for name, pos in STATIONS.items()]
    return MetroSystem(name="City Reproduction: London Underground", tick_ms=tick_ms, size=(800, 560), render_scale=render_scale).pipeline([
        Network([
            Line("Central", TFL_CENTRAL, shuttle("Oxford Circus", "Holborn", "Bank", "Liverpool St")),
            Line("Piccadilly", TFL_PICCADILLY, shuttle("King's Cross", "Holborn", "Piccadilly")),
            Line("Circle", TFL_CIRCLE, loop("Paddington", "Baker St", "King's Cross", "Liverpool St", "Westminster", "Victoria")),
            Line("Victoria", TFL_VICTORIA, shuttle("King's Cross", "Oxford Circus", "Victoria")),
            Line("Bakerloo", TFL_BAKERLOO, shuttle("Paddington", "Baker St", "Oxford Circus", "Piccadilly", "Waterloo")),
            Line("Jubilee", TFL_JUBILEE, shuttle("Baker St", "Westminster", "Waterloo", "London Bridge", "Canada Water")),
            Line("Night Response", SERVICE_YELLOW, shuttle("Acton Depot", "Victoria", "Waterloo", "Bank")),
            *stations,
        ]),
        Train("CEN", line="Central", solver=train_solver, asset="metro_nose"),
        Train("PIC", line="Piccadilly", solver=train_solver, asset="bullet_metro"),
        Train("CIR", line="Circle", solver=train_solver, asset="city_tram"),
        Train("VIC", line="Victoria", solver=train_solver, asset="metro_nose"),
        Train("BAK", line="Bakerloo", solver=train_solver, asset="city_tram"),
        Train("JUB", line="Jubilee", solver=train_solver, asset="bullet_metro"),
        Train("NRM", line="Night Response", solver=train_solver, asset="maintenance"),
        Signal("King's Cross Interlock", (395, 105), label="KX", controls=[ControlRule("Piccadilly", s("King's Cross"), s("Holborn")), ControlRule("Circle", s("Baker St"), s("King's Cross")), ControlRule("Victoria", s("King's Cross"), s("Oxford Circus"))], solver=king_cross_interlock),
        Signal("Liverpool Street Interlock", (655, 235), label="Liverpool", controls=[ControlRule("Central", s("Bank"), s("Liverpool St")), ControlRule("Circle", s("King's Cross"), s("Liverpool St"))], solver=liverpool_interlock),
        Signal("Waterloo Interlock", (470, 440), label="Waterloo", controls=[ControlRule("Jubilee", s("Westminster"), s("Waterloo")), ControlRule("Night Response", s("Victoria"), s("Waterloo"))], solver=waterloo_interlock),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
