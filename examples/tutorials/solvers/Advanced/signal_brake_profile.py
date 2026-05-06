from __future__ import annotations

from metrogym import Color, MetroSystem, SignalAgent, SignalObservation, TrainAgent, TrainObservation, signal, train
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train


class BrakeProfileTrainSolver(TrainAgent):
    def act(self, observation: TrainObservation):
        next_signal = observation.signals.next
        current_train = observation.self
        if next_signal is None:
            return train.accelerate_to(4.0, reason="open track")
        distance = min(
            current_train.position.distance(next_signal.start),
            current_train.next_position.distance(next_signal.start),
        )
        if not next_signal.signal_green:
            if distance < 70:
                return train.brake_to(0.0, reason="final braking zone")
            if distance < 140:
                return train.brake_to(1.0, reason="approach control")
            return train.brake_to(2.0, reason="signal caution")
        if distance < 120:
            return train.accelerate_to(2.5, reason="cleared through green signal")
        return train.accelerate_to(4.0, reason="mainline acceleration")


class GatePulseSolver(SignalAgent):
    def act(self, observation: SignalObservation):
        if observation.tick % 18 < 8:
            return signal.deny(reason="timed red window")
        return signal.grant(reason="timed release")


def build_system(*, tick_ms: int = 220, render_scale: int | float = 2) -> MetroSystem:
    train_solver = BrakeProfileTrainSolver()
    signal_solver = GatePulseSolver()
    return MetroSystem(name="Solver Advanced: Signal Brake Profile", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Brake Test", Color.GREEN, [(70, 240), (220, 240), (360, 200), (520, 200), (610, 240), (520, 280), (360, 280), (220, 240), (70, 240)]),
            Station("Depot", (70, 240)),
            Station("Approach", (220, 240)),
            Station("Signal Gate", (360, 200), radius=10),
            Station("East Curve", (520, 200)),
            Station("Return", (610, 240)),
        ]),
        Train("TEST-1", line="Brake Test", solver=train_solver, asset="metro_nose", speed=1),
        Signal(
            "Brake Gate",
            (390, 170),
            label="B-GATE",
            controls=ControlRule("Brake Test", (220, 240), (360, 200)),
            solver=signal_solver,
        ),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
