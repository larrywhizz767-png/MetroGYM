from __future__ import annotations

from metrogym import Color, MetroSystem, TrainAgent, TrainObservation, signal, train
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train

JUNCTION = (340, 240)
NORTH_IN = (340, 70)
NORTH_OUT = (390, 70)
NORTH_EAST_IN = (520, 100)
NORTH_EAST_OUT = (555, 135)
EAST_IN = (610, 240)
EAST_OUT = (610, 290)
SOUTH_IN = (340, 410)
SOUTH_OUT = (290, 410)
SOUTH_WEST_IN = (160, 380)
SOUTH_WEST_OUT = (125, 345)
WEST_IN = (70, 240)
WEST_OUT = (70, 190)


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


def build_system(*, tick_ms: int = 240, render_scale: int | float = 2) -> MetroSystem:
    train_solver = EventReactiveTrainSolver()
    signal_solver = signal.priority_queue(approach_distance=85.0, release_distance=105.0, red_hold_ticks=3)
    return MetroSystem(name="Solver Advanced: Four Train Eight Path Queue", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("North to East", Color.BLUE, [NORTH_IN, JUNCTION, EAST_OUT, JUNCTION, NORTH_IN]),
            Line("West to South", Color.PURPLE, [WEST_IN, JUNCTION, SOUTH_OUT, JUNCTION, WEST_IN]),
            Line("South to North-East", Color.GREEN, [SOUTH_IN, JUNCTION, NORTH_EAST_OUT, JUNCTION, SOUTH_IN]),
            Line("East to South-West", Color.YELLOW, [EAST_IN, JUNCTION, SOUTH_WEST_OUT, JUNCTION, EAST_IN]),
            Station("North Approach", NORTH_IN),
            Station("North Exit", NORTH_OUT),
            Station("North-East Approach", NORTH_EAST_IN),
            Station("North-East Exit", NORTH_EAST_OUT),
            Station("East Approach", EAST_IN),
            Station("East Exit", EAST_OUT),
            Station("South Approach", SOUTH_IN),
            Station("South Exit", SOUTH_OUT),
            Station("South-West Approach", SOUTH_WEST_IN),
            Station("South-West Exit", SOUTH_WEST_OUT),
            Station("West Approach", WEST_IN),
            Station("West Exit", WEST_OUT),
            Station("Junction", JUNCTION, radius=10),
        ]),
        Train("N-E", line="North to East", solver=train_solver, asset="city_tram"),
        Train("W-S", line="West to South", solver=train_solver, asset="bullet_metro"),
        Train("S-NE", line="South to North-East", solver=train_solver, asset="metro_nose"),
        Train("E-SW", line="East to South-West", solver=train_solver, asset="maintenance"),
        Signal(
            "Eight-Path Queue",
            (365, 220),
            label="8P",
            controls=[
                ControlRule("North to East", NORTH_IN, JUNCTION),
                ControlRule("West to South", WEST_IN, JUNCTION),
                ControlRule("South to North-East", SOUTH_IN, JUNCTION),
                ControlRule("East to South-West", EAST_IN, JUNCTION),
            ],
            solver=signal_solver,
        ),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
