from __future__ import annotations

import pygame
from beartype import beartype


@beartype
class KeyboardController:
    @beartype
    def __init__(self, simulator: object):
        self.simulator = simulator

    @beartype
    def handle_keydown(self, event: object) -> None:
        if not (event.mod & pygame.KMOD_CTRL):
            return
        if event.key == pygame.K_q:
            self.simulator.close()
        elif event.key == pygame.K_r:
            self.simulator.reset()
        elif event.key in {pygame.K_MINUS, pygame.K_KP_MINUS}:
            self.simulator.jump_percent(-0.05)
        elif event.key in {pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS}:
            self.simulator.jump_percent(0.05)
        elif event.key == pygame.K_d:
            self.simulator.animation_ratio += 0.5
        elif event.key == pygame.K_a:
            self.simulator.animation_ratio = max(0.5, self.simulator.animation_ratio - 0.5)
        elif event.key == pygame.K_h:
            self.simulator.toggle_help()
        elif event.key == pygame.K_l:
            self.simulator.toggle_log()
        elif event.key == pygame.K_m:
            self.simulator.toggle_ui_mode()
