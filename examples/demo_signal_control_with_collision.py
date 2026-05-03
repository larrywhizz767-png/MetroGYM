from __future__ import annotations

import threading
import time

from metrogym import Color, MetroSystem
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train


def build_system() -> MetroSystem:
    return MetroSystem(name="Signal Control + Intentional Collision", tick_ms=350, render_scale=1).pipeline([
        Network([
            Line("Controlled Lead", Color.BLUE.darker(), [(220, 180), (420, 180), (560, 260), (420, 340), (220, 340), (220, 180)]),
            Line("Controlled", Color.BLUE, [(140, 180), (420, 180), (560, 260), (420, 340), (140, 340), (140, 180)]),
            Line("Uncontrolled Crossing", Color.RED, [(140, 320), (140, 180), (140, 320)]),
            Station("Gate", (140, 180), radius=9),
            Station("Clearview", (420, 180), radius=9),
            Station("Crossing", (140, 260), radius=7),
            Station("Depot", (140, 320), radius=7),
        ]),
        Train("M1", line="Controlled Lead"),
        Train("M2", line="Controlled"),
        Train("M3", line="Uncontrolled Crossing"),
        Signal(
            "TL-Controlled",
            (140, 140),
            initial_green=False,
            period_ticks=999,
            label="Main signal",
            controls=ControlRule("Controlled", (140, 180), (420, 180)),
        ),
    ])


def main() -> None:
    system = build_system().fit()
    sim = system.simulator
    light = sim.light("TL-Controlled")

    def release_when_clear() -> None:
        while not sim.control.emergency_stopped:
            if sim.train("M1").position.x >= 420:
                time.sleep(0.8)
                light.set_state(green=True)
                print("[CONTROL] M1 reached Clearview; TL-Controlled is now green for M2")
                return
            time.sleep(0.1)

    threading.Thread(target=release_when_clear, daemon=True).start()
    system.run()


if __name__ == "__main__":
    main()
