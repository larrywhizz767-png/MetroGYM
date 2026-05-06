from __future__ import annotations

from metrogym import Color, MetroSystem, TrainAgent, TrainObservation, train
from metrogym.primitives import Line, Network, Station, Train


class CommuterRampSolver(TrainAgent):
    def act(self, observation: TrainObservation):
        current_train = observation.self
        if current_train.id == "SPRINTER" and observation.tick < 10:
            return train.accelerate_to(4.0, reason="opening sprint")
        if current_train.id == "SPRINTER" and observation.tick < 22:
            return train.coast(reason="cruise phase")
        if current_train.id == "SPRINTER":
            return train.brake_to(1.0, reason="approaching terminal")
        if observation.tick < 12:
            return train.accelerate_to(2.5, reason="building commuter pace")
        return train.brake_to(1.0, reason="settling to local speed")


def build_system(*, tick_ms: int = 220, render_scale: int | float = 2) -> MetroSystem:
    solver = CommuterRampSolver()
    return MetroSystem(name="Solver Advanced: Speed Ramp Commuter", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Commuter Loop", Color.BLUE, [(90, 160), (300, 110), (540, 160), (590, 300), (430, 420), (210, 420), (70, 300), (90, 160)]),
            Station("Depot", (90, 160)),
            Station("North Bend", (300, 110)),
            Station("East Hub", (540, 160)),
            Station("South Arc", (430, 420)),
            Station("West Arc", (210, 420)),
        ]),
        Train("SPRINTER", line="Commuter Loop", solver=solver, asset="bullet_metro", speed=1),
        Train("LOCAL", line="Commuter Loop", start_at=50, solver=solver, asset="city_tram", speed=1),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
