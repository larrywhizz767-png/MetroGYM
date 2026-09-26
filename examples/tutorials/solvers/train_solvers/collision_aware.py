from __future__ import annotations

from metrogym import Color, MetroSystem, TrainAgent, TrainObservation, train
from metrogym.primitives import Line, Network, Station, Train


class DelayedCollisionSolver(TrainAgent):
    def __init__(self, release_tick: int = 10, min_distance: float = 80.0):
        self.release_tick = release_tick
        self.collision_guard = train.avoid_collisions(min_distance=min_distance)

    def act(self, observation: TrainObservation):
        if observation.self.id == "LEAD" and observation.tick < self.release_tick:
            return train.hold(reason="holding lead train")
        return self.collision_guard(observation)


def build_system(*, tick_ms: int = 300, render_scale: int | float = 2) -> MetroSystem:
    return MetroSystem(name="Solver Medium: Collision Aware", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Shared Loop", Color.RED, [(100, 140), (560, 140), (560, 360), (100, 360), (100, 140)]),
            Station("West", (100, 140)),
            Station("East", (560, 140)),
            Station("South", (560, 360)),
            Station("Depot", (100, 360)),
        ]),
        Train("LEAD", line="Shared Loop", start_at=8, solver=DelayedCollisionSolver(), asset="metro_nose", speed=1),
        Train("FOLLOW", line="Shared Loop", solver=train.avoid_collisions(min_distance=80.0), asset="maintenance", speed=2),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
