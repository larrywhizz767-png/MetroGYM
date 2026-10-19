from __future__ import annotations

from importlib.metadata import version
from pathlib import Path

import pygame

import metrogym
from metrogym import Color, MetroSystem, load_signal_asset_surface, load_train_asset_surface, signal, train
from metrogym.core.constants import ROOBERT_BOLD, ROOBERT_MEDIUM, ROOBERT_REGULAR, ROOBERT_SEMIBOLD
from metrogym.core.signal_assets import SIGNAL_ASSET_SCALES, SIGNAL_ASSET_STATES
from metrogym.core.train_assets import TRAIN_ASSET_NAMES, TRAIN_ASSET_SCALES
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train
from metrogym.rendering.primitives.metrogym_renderer.runtime import RuntimeMetroGYMRenderer


def main() -> None:
    checkout_source = Path(__file__).resolve().parents[1] / "src"
    installed_module = Path(metrogym.__file__).resolve()
    if installed_module.is_relative_to(checkout_source):
        raise RuntimeError("Smoke check imported the checkout instead of the installed distribution.")

    system = MetroSystem(name="Distribution smoke check", render_scale=1).pipeline([
        Network([
            Line("Loop", Color.BLUE, [(120, 120), (560, 120), (560, 360), (120, 360), (120, 120)]),
            Station("West", (120, 120)),
        ]),
        Train("A", line="Loop", solver=train.always_proceed(), asset="metro_nose"),
        Signal(
            "Gate",
            (560, 85),
            controls=ControlRule("Loop", (560, 120), (560, 360)),
            solver=signal.pulse(green_ticks=5, red_ticks=3),
        ),
    ]).fit()
    simulator = system.simulator
    if simulator is None:
        raise RuntimeError("fit() did not create a simulator.")
    initial_position = simulator.train("A").position
    system.step(3)
    assert simulator.tick_count == 3
    assert simulator.train("A").position != initial_position

    pygame.display.init()
    pygame.font.init()
    try:
        surface = pygame.display.set_mode(simulator.panel.window_size.pygame())
        for name in TRAIN_ASSET_NAMES:
            for scale in TRAIN_ASSET_SCALES:
                assert load_train_asset_surface(name, scale=scale).get_width() > 0
        for state in SIGNAL_ASSET_STATES:
            for scale in SIGNAL_ASSET_SCALES:
                assert load_signal_asset_surface(state, scale=scale).get_width() > 0
        for font_path in (ROOBERT_REGULAR, ROOBERT_MEDIUM, ROOBERT_SEMIBOLD, ROOBERT_BOLD):
            assert font_path.is_file(), f"Missing bundled font: {font_path}"
            assert pygame.font.Font(str(font_path), 12).render("MetroGYM", True, "white").get_width() > 0
        simulator.panel.draw(surface, RuntimeMetroGYMRenderer(1), ui_mode="full")
        system.reset()
        assert simulator.tick_count == 0
        assert simulator.train("A").position == initial_position
    finally:
        pygame.quit()
    print(f"MetroGYM {version('metrogym')}: installed distribution passed ({installed_module}).")


if __name__ == "__main__":
    main()