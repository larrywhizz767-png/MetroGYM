from __future__ import annotations

from metrogym import Color, MetroSystem, SignalAgent, SignalObservation, TrainAgent, TrainObservation, signal, train
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train

RING_WAYPOINTS = [
    (180, 80),
    (300, 55),
    (430, 80),
    (530, 155),
    (565, 260),
    (530, 365),
    (430, 440),
    (300, 465),
    (180, 440),
    (80, 365),
    (45, 260),
    (80, 155),
    (180, 80),
]

INNER_CONNECTOR = [
    (300, 465),
    (300, 350),
    (300, 260),
    (300, 170),
    (300, 55),
    (300, 170),
    (300, 260),
    (300, 350),
    (300, 465),
]

CROSS_CONNECTOR = [
    (45, 260),
    (140, 260),
    (220, 260),
    (300, 260),
    (380, 260),
    (460, 260),
    (565, 260),
    (460, 260),
    (380, 260),
    (300, 260),
    (220, 260),
    (140, 260),
    (45, 260),
]


class CircularTrainSolver(TrainAgent):
    def __init__(self):
        self.guardrail = train.all_of(
            train.respect_signals(approach_distance=55.0),
            train.avoid_collisions(min_distance=70.0),
        )

    def act(self, observation: TrainObservation):
        if observation.emergency_stopped or observation.collision_events:
            return train.hold(reason="ring emergency")
        return self.guardrail(observation)


class CircleDispatchSolver(SignalAgent):
    def __init__(self, approach_distance: float = 70.0, release_distance: float = 95.0, red_hold_ticks: int = 3):
        self.dispatch = signal.priority_queue(
            approach_distance=approach_distance,
            release_distance=release_distance,
            red_hold_ticks=red_hold_ticks,
        )

    def reset(self) -> None:
        self.dispatch.reset()

    def act(self, observation: SignalObservation):
        return self.dispatch(observation)


def build_system(*, tick_ms: int = 240, render_scale: int | float = 2) -> MetroSystem:
    train_solver = CircularTrainSolver()
    west_dispatch = CircleDispatchSolver(approach_distance=65.0, release_distance=90.0, red_hold_ticks=3)
    east_dispatch = CircleDispatchSolver(approach_distance=65.0, release_distance=90.0, red_hold_ticks=3)
    return MetroSystem(name="Solver Advanced: Circular Ring Dispatch", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Outer Ring", Color.BLUE, RING_WAYPOINTS),
            Line("North-South Chord", Color.GREEN, INNER_CONNECTOR),
            Line("Cross-City Chord", Color.YELLOW, CROSS_CONNECTOR),
            Station("North Arc", (300, 55)),
            Station("North-East", (475, 120)),
            Station("East Arc", (565, 260), radius=10),
            Station("South-East", (475, 400)),
            Station("South Arc", (300, 465)),
            Station("South-West", (125, 400)),
            Station("West Arc", (45, 260), radius=10),
            Station("North-West", (125, 120)),
            Station("Grand Circle", (300, 260), radius=12),
        ]),
        Train("RING-1", line="Outer Ring", solver=train_solver, asset="metro_nose"),
        Train("RING-2", line="Outer Ring", start_at=33, solver=train_solver, asset="city_tram"),
        Train("RING-3", line="Outer Ring", start_at=66, solver=train_solver, asset="bullet_metro"),
        Train("NS", line="North-South Chord", solver=train_solver, asset="maintenance"),
        Train("XC", line="Cross-City Chord", solver=train_solver, asset="city_tram"),
        Signal(
            "West Arc Merge",
            (95, 230),
            label="W-ARC",
            controls=[
                ControlRule("Outer Ring", (45, 260), (80, 155)),
                ControlRule("Cross-City Chord", (140, 260), (45, 260)),
            ],
            solver=west_dispatch,
        ),
        Signal(
            "East Arc Merge",
            (520, 230),
            label="E-ARC",
            controls=[
                ControlRule("Outer Ring", (530, 155), (565, 260)),
                ControlRule("Cross-City Chord", (460, 260), (565, 260)),
            ],
            solver=east_dispatch,
        ),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
