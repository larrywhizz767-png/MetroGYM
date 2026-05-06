from __future__ import annotations

from metrogym import Color, MetroSystem, SignalObservation, signal, train
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train


def build_system(*, tick_ms: int = 350, render_scale: int | float = 2) -> MetroSystem:
    return MetroSystem(name="Solver Medium: Pulse Train", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Pulse Loop", Color.GREEN, [(120, 180), (560, 180), (560, 340), (120, 340), (120, 180)]),
            Station("Start", (120, 180)),
            Station("East", (560, 180)),
            Station("South", (560, 340)),
            Station("West", (120, 340)),
        ]),
        Train("PULSE", line="Pulse Loop", solver=train.pulse(run_ticks=3, hold_ticks=2), asset="city_tram"),
        Train("CAREFUL", line="Pulse Loop", start_at=50, solver=train.respect_signals(), asset="metro_nose"),
        Signal(
            "PULSE-GATE",
            (560, 210),
            label="Gate",
            controls=ControlRule("Pulse Loop", (560, 180), (560, 340)),
            solver=lambda obs: signal.deny() if _is_red_phase(obs) else signal.grant(),
        ),
    ])


def _is_red_phase(observation: SignalObservation) -> bool:
    return observation.tick % 8 in {4, 5, 6, 7}


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
