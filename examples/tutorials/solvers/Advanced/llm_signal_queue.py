from __future__ import annotations

from metrogym import Color, MetroSystem, TrainAgent, TrainObservation, train
from metrogym.primitives import ControlRule, LLMSignalQueueHandler, Line, Network, Station, Train

JUNCTION = (340, 240)
NORTH_IN = (340, 70)
NORTH_OUT = (390, 70)
EAST_IN = (610, 240)
EAST_OUT = (610, 290)
SOUTH_IN = (340, 410)
SOUTH_OUT = (290, 410)
WEST_IN = (70, 240)
WEST_OUT = (70, 190)


class QueueAwareTrainSolver(TrainAgent):
    def __init__(self):
        self.guardrail = train.all_of(
            train.respect_signals(approach_distance=95.0),
            train.avoid_collisions(min_distance=60.0),
        )

    def act(self, observation: TrainObservation):
        if observation.emergency_stopped or observation.collision_events:
            return train.hold(reason="system emergency")
        return self.guardrail(observation)


def build_system(
    *,
    tick_ms: int = 240,
    render_scale: int | float = 2,
    model: str = "gpt-4o-mini",
    decision_prompt: str = "Prioritise the nearest approaching train first for fair handling.",
    include_signal_state: bool = True,
    include_queue_candidates: bool = True,
    include_world_state: bool = False,
) -> MetroSystem:
    train_solver = QueueAwareTrainSolver()
    return MetroSystem(name="Solver Advanced: LLM Signal Queue", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("North to East", Color.BLUE, [NORTH_IN, JUNCTION, EAST_OUT, JUNCTION, NORTH_IN]),
            Line("West to South", Color.PURPLE, [WEST_IN, JUNCTION, SOUTH_OUT, JUNCTION, WEST_IN]),
            Line("South to East", Color.GREEN, [SOUTH_IN, JUNCTION, EAST_OUT, JUNCTION, SOUTH_IN]),
            Station("North Approach", NORTH_IN),
            Station("North Exit", NORTH_OUT),
            Station("East Approach", EAST_IN),
            Station("East Exit", EAST_OUT),
            Station("South Approach", SOUTH_IN),
            Station("South Exit", SOUTH_OUT),
            Station("West Approach", WEST_IN),
            Station("West Exit", WEST_OUT),
            Station("Junction", JUNCTION, radius=10),
        ]),
        Train("N-E", line="North to East", solver=train_solver, asset="city_tram"),
        Train("W-S", line="West to South", solver=train_solver, asset="bullet_metro"),
        Train("S-E", line="South to East", solver=train_solver, asset="metro_nose"),
        LLMSignalQueueHandler(
            "LLM Queue Post",
            (365, 220),
            label="LLM",
            model=model,
            decision_prompt=decision_prompt,
            include_signal_state=include_signal_state,
            include_queue_candidates=include_queue_candidates,
            include_world_state=include_world_state,
            approach_distance=95.0,
            release_distance=120.0,
            red_hold_ticks=3,
            controls=[
                ControlRule("North to East", NORTH_IN, JUNCTION),
                ControlRule("West to South", WEST_IN, JUNCTION),
                ControlRule("South to East", SOUTH_IN, JUNCTION),
            ],
        ),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
