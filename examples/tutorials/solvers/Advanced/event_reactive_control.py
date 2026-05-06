from __future__ import annotations

from metrogym import Color, MetroSystem, SignalAgent, SignalObservation, TrainAgent, TrainObservation, signal, train
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train

JUNCTION = (340, 240)
NORTH = (340, 80)
EAST = (580, 240)
SOUTH = (340, 400)
WEST = (100, 240)


class EventReactiveTrainSolver(TrainAgent):
    def __init__(self):
        self.guardrail = train.all_of(
            train.respect_signals(),
            train.avoid_collisions(min_distance=60.0),
        )

    def act(self, observation: TrainObservation):
        if observation.emergency_stopped or observation.collision_events:
            return train.hold(reason="system emergency")
        return self.guardrail(observation)


class JunctionQueueSolver(SignalAgent):
    def __init__(self, approach_distance: float = 75.0, release_distance: float = 95.0, red_hold_ticks: int = 3):
        self.dispatch = signal.priority_queue(
            approach_distance=approach_distance,
            release_distance=release_distance,
            red_hold_ticks=red_hold_ticks,
        )

    def reset(self) -> None:
        self.dispatch.reset()

    def act(self, observation: SignalObservation):
        return self.dispatch(observation)


def build_system(*, tick_ms: int = 260, render_scale: int | float = 2) -> MetroSystem:
    train_solver = EventReactiveTrainSolver()
    signal_solver = JunctionQueueSolver()
    return MetroSystem(name="Solver Advanced: Event Reactive Control", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("North-East", Color.BLUE, [NORTH, JUNCTION, EAST, JUNCTION, NORTH]),
            Line("West-South", Color.PURPLE, [WEST, JUNCTION, SOUTH, JUNCTION, WEST]),
            Station("North", NORTH),
            Station("East", EAST),
            Station("South", SOUTH),
            Station("West", WEST),
            Station("Junction", JUNCTION, radius=10),
        ]),
        Train("B-1", line="North-East", solver=train_solver, asset="city_tram"),
        Train("B-2", line="West-South", solver=train_solver, asset="bullet_metro"),
        Signal(
            "Junction Queue",
            (365, 220),
            label="QUEUE",
            controls=[
                ControlRule("North-East", NORTH, JUNCTION),
                ControlRule("West-South", WEST, JUNCTION),
            ],
            solver=signal_solver,
        ),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
