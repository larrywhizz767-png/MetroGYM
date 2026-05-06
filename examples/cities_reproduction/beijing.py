from __future__ import annotations

from metrogym import Color, MetroSystem, SignalAgent, SignalObservation, TrainAgent, TrainObservation, distance_to_rule, signal, train
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train

STATIONS: dict[str, tuple[int, int]] = {
    "Pingguoyuan": (80, 350),
    "Fuxingmen": (270, 350),
    "Tiananmen": (430, 350),
    "Jianguomen": (590, 350),
    "Beijing Railway": (760, 350),
    "Xizhimen": (330, 260),
    "Dongzhimen": (560, 260),
    "Beijing South": (430, 470),
    "Xuanwumen": (330, 405),
    "Qianmen": (500, 405),
    "Yuanmingyuan Park": (205, 135),
    "Line 3 East": (340, 135),
    "Line 3 South": (340, 285),
    "Line 4 North": (460, 95),
    "Line 4 South": (500, 500),
    "Line 5 North": (610, 165),
    "Line 5 South": (610, 510),
    "Line 6 West": (250, 420),
    "Line 6 East": (820, 420),
    "Line 7 West": (245, 505),
    "Line 7 East": (800, 505),
    "Line 8 North": (560, 155),
    "Line 8 South": (560, 585),
    "Airport City": (720, 250),
    "Airport Terminal": (870, 140),
}

BEIJING_RED = Color(202, 52, 53)
BEIJING_BLUE = Color(0, 92, 180)
BEIJING_TEAL = Color(40, 145, 144)
BEIJING_CYAN = Color(30, 194, 196)
BEIJING_GREEN = Color(0, 165, 45)
BEIJING_MAGENTA = Color(198, 48, 197)
BEIJING_ORANGE = Color(255, 141, 31)
BEIJING_TAN = Color(220, 177, 100)
SERVICE_YELLOW = Color(255, 211, 0)


def s(name: str) -> tuple[int, int]:
    return STATIONS[name]


def shuttle(*names: str) -> list[tuple[int, int]]:
    points = [s(name) for name in names]
    return [*points, *reversed(points[1:-1]), points[0]]


class BeijingInterchangeSolver(SignalAgent):
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


class BeijingTrainSolver(TrainAgent):
    def __init__(self):
        self.safety = train.all_of(
            train.respect_signals(approach_distance=45.0),
            train.avoid_collisions(min_distance=65.0),
        )
        self.approach_distance = 45.0

    def act(self, observation: TrainObservation):
        current_train = observation.self
        if observation.collision_events and current_train.id == "MOW":
            return train.proceed(reason="maintenance continues during incidents")
        if observation.collision_events:
            return train.hold(reason="network collision response")
        if self._blocked_by_signal(observation):
            return train.hold(reason="interchange signal blocks entry")
        return self.safety(observation)

    def _blocked_by_signal(self, observation: TrainObservation) -> bool:
        current_train = observation.self
        for rule in observation.signals.ahead:
            if distance_to_rule(current_train, rule) > self.approach_distance:
                continue
            if current_train.next_position.distance(rule.end) <= self.approach_distance:
                continue
            if not rule.signal_green:
                return self._moving_toward_start(current_train, rule)
            if rule.signal_granted_train_id is not None and rule.signal_granted_train_id != current_train.id:
                return self._moving_toward_start(current_train, rule)
            if rule.signal_granted_line is not None and rule.signal_granted_line != current_train.line_name:
                return self._moving_toward_start(current_train, rule)
        return False

    def _moving_toward_start(self, current_train: object, rule: object) -> bool:
        return current_train.next_position.distance(rule.start) < current_train.position.distance(rule.start) or current_train.position.distance(rule.start) <= 1.5


def build_system(*, tick_ms: int = 320, render_scale: int | float = 2) -> MetroSystem:
    train_solver = BeijingTrainSolver()
    xizhimen_solver = BeijingInterchangeSolver(approach_distance=42.0, release_distance=75.0)
    jianguomen_solver = BeijingInterchangeSolver(approach_distance=45.0, release_distance=80.0)
    south_solver = BeijingInterchangeSolver(approach_distance=40.0, release_distance=75.0)
    interchanges = {"Fuxingmen", "Jianguomen", "Xizhimen", "Dongzhimen", "Beijing South", "Xuanwumen", "Qianmen", "Beijing Railway"}
    stations = [Station(name, pos, radius=9 if name in interchanges else 6) for name, pos in STATIONS.items()]
    return MetroSystem(name="City Reproduction: Beijing Subway Minimal", tick_ms=tick_ms, size=(940, 640), render_scale=render_scale).pipeline([
        Network([
            Line("Line 1", BEIJING_RED, shuttle("Pingguoyuan", "Fuxingmen", "Tiananmen", "Jianguomen", "Beijing Railway")),
            Line("Line 2", BEIJING_BLUE, [s("Xizhimen"), s("Dongzhimen"), s("Beijing Railway"), s("Beijing South"), s("Xizhimen")]),
            Line("Line 3 West", BEIJING_CYAN, shuttle("Yuanmingyuan Park", "Line 3 East", "Line 3 South", "Fuxingmen")),
            Line("Line 3 Airport", BEIJING_CYAN, shuttle("Beijing Railway", "Airport City", "Airport Terminal")),
            Line("Line 4", BEIJING_TEAL, shuttle("Line 4 North", "Xizhimen", "Fuxingmen", "Line 4 South")),
            Line("Line 5", BEIJING_MAGENTA, shuttle("Line 5 North", "Qianmen", "Line 5 South")),
            Line("Line 6", BEIJING_ORANGE, shuttle("Line 6 West", "Xuanwumen", "Qianmen", "Line 6 East")),
            Line("Line 7", BEIJING_TAN, shuttle("Line 7 West", "Beijing South", "Line 7 East")),
            Line("Line 8", BEIJING_GREEN, shuttle("Line 8 North", "Qianmen", "Line 8 South")),
            Line("Maintenance Ring", SERVICE_YELLOW, shuttle("Beijing South", "Qianmen", "Jianguomen", "Xizhimen")),
            *stations,
        ]),
        Train("L1", line="Line 1", solver=train_solver, asset="metro_nose"),
        Train("L2", line="Line 2", solver=train_solver, asset="bullet_metro"),
        Train("L4", line="Line 4", solver=train_solver, asset="city_tram"),
        Train("L5", line="Line 5", solver=train_solver, asset="metro_nose"),
        Train("L6", line="Line 6", solver=train_solver, asset="bullet_metro"),
        Train("L8", line="Line 8", solver=train_solver, asset="city_tram"),
        Train("MOW", line="Maintenance Ring", solver=train_solver, asset="maintenance"),
        Signal("Xizhimen Interlock", (360, 245), label="XZH", controls=[ControlRule("Line 2", s("Xizhimen"), s("Dongzhimen")), ControlRule("Line 4", s("Line 4 North"), s("Xizhimen")), ControlRule("Maintenance Ring", s("Jianguomen"), s("Xizhimen"))], solver=xizhimen_solver),
        Signal("Jianguomen Interlock", (615, 330), label="JGM", controls=[ControlRule("Line 1", s("Tiananmen"), s("Jianguomen")), ControlRule("Line 2", s("Dongzhimen"), s("Beijing Railway")), ControlRule("Maintenance Ring", s("Qianmen"), s("Jianguomen"))], solver=jianguomen_solver),
        Signal("Beijing South Interlock", (455, 505), label="South", controls=[ControlRule("Line 2", s("Beijing Railway"), s("Beijing South")), ControlRule("Line 7", s("Line 7 West"), s("Beijing South")), ControlRule("Maintenance Ring", s("Beijing South"), s("Qianmen"))], solver=south_solver),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
