from __future__ import annotations

import threading
from collections.abc import Iterable, Sequence
from typing import Protocol

import pygame
from beartype import beartype

from metrogym.controls import ControlSystem, SignalRule
from metrogym.core import ColorRGBA, Direction, PositionLike, TrainAssetName, UIMode, next_ui_mode, ui_mode_label, validate_ui_mode
from metrogym.primitives.line.extras.path import build_path
from metrogym.primitives.line.runtime import RuntimeLine
from metrogym.primitives.signal.runtime import RuntimeTrafficLight
from metrogym.primitives.station.runtime import RuntimeStation
from metrogym.primitives.train.runtime import RuntimeTrain
from metrogym.rendering._utils.keyboard import KeyboardController
from metrogym.rendering.panel import SimulationPanel
from metrogym.rendering.primitives.metrogym_renderer.runtime import RuntimeMetroGYMRenderer


class RuntimeObject(Protocol):
    def update(self) -> None:
        ...

    def reset(self) -> None:
        ...

    def draw(self, surface: object, *args: object, **kwargs: object) -> None:
        ...


@beartype
class RuntimeSimulator:
    @beartype
    def __init__(
        self,
        *,
        title: str = "Metro Gymulation",
        tick_ms: int = 500,
        size: PositionLike = (700, 520),
        verbose: bool = False,
        stop_all_on_collision: bool = False,
        render_scale: int | float = 2.0,
    ):
        self._panel = SimulationPanel(size, float(render_scale))
        self._title = title
        self._tick_ms = tick_ms
        self.animation_ratio = 1.0
        self._lines: dict[str, RuntimeLine] = {}
        self._trains: dict[str, RuntimeTrain] = {}
        self._lights: dict[str, RuntimeTrafficLight] = {}
        self.control = ControlSystem(self._lights, stop_all_on_collision=stop_all_on_collision)
        self._stations: list[RuntimeStation] = []
        self._closed = threading.Event()
        self._verbose = verbose
        self._screen: object | None = None
        self._show_help = False
        self.ui_mode: UIMode = "minimal"
        self._keyboard = KeyboardController(self)

    @beartype
    def add_line(self, name: str, color: ColorRGBA, waypoints: Sequence[PositionLike]) -> RuntimeLine:
        path = build_path(waypoints)
        self._panel.add_track_line(path, color, name)
        line = RuntimeLine(name=name, color=color, path=path)
        self._lines[name] = line
        return line

    @beartype
    def add_train(
        self,
        id: str,
        line: str | RuntimeLine,
        path_or_line: RuntimeLine | None = None,
        *,
        color: ColorRGBA | None = None,
        start_at: int | float = 0,
        midpoint: bool = False,
        asset: TrainAssetName | str = "metro_nose",
    ) -> RuntimeTrain:
        selected_line = line if isinstance(line, RuntimeLine) else self._lines[line]
        start_percent = 50 if midpoint and start_at == 0 else float(start_at)
        if not 0 <= start_percent <= 100:
            raise ValueError("start_at must be a percentage in the range 0..100")
        path = _rotate_path(selected_line.path, start_percent)
        train = RuntimeTrain(id, selected_line.name, path, color if color is not None else selected_line.color, self.control, asset)
        self._panel.add_object(train)
        self._trains[id] = train
        return train

    @beartype
    def link_peers(self, train_ids: Iterable[str]) -> None:
        peers = [self._trains[train_id] for train_id in train_ids]
        for train in peers:
            train.set_peers(peers)

    @beartype
    def add_traffic_light(
        self,
        id: str,
        position: PositionLike,
        *,
        initial_green: bool = True,
        period_ticks: int = 5,
        label: str | None = None,
    ) -> RuntimeTrafficLight:
        light = RuntimeTrafficLight(id, position, initial_green, period_ticks, label)
        self._panel.add_object(light)
        self._lights[id] = light
        return light

    @beartype
    def protect_segment(
        self,
        line: str | RuntimeLine,
        start: PositionLike,
        end: PositionLike,
        light: str | RuntimeTrafficLight,
        *,
        direction: Direction = "both",
    ) -> SignalRule:
        return self.control.protect_segment(line, start, end, light, direction=direction)

    @beartype
    def add_station(self, name: str, position: PositionLike, radius: int = 7) -> RuntimeStation:
        station = RuntimeStation(name, position, radius)
        self._panel.add_station(station)
        self._stations.append(station)
        return station

    @property
    def panel(self) -> SimulationPanel:
        return self._panel

    @beartype
    def train(self, id: str) -> RuntimeTrain:
        return self._trains[id]

    @beartype
    def line(self, name: str) -> RuntimeLine:
        return self._lines[name]

    @beartype
    def light(self, id: str) -> RuntimeTrafficLight:
        return self._lights[id]

    def tick(self) -> None:
        self._panel.tick()

    def reset(self) -> None:
        self.control.reset(clear_events=True)
        self._panel.reset()

    @beartype
    def seek_to_tick(self, target_tick: int) -> None:
        target = max(0, int(target_tick))
        self.reset()
        for _ in range(target):
            self.tick()

    @beartype
    def jump_percent(self, percent: int | float) -> None:
        current = self._panel.tick_count
        delta = max(1, round(max(1, current) * abs(percent)))
        target = current + delta if percent >= 0 else current - delta
        self.seek_to_tick(target)

    def toggle_help(self) -> None:
        self._show_help = not self._show_help

    def toggle_ui_mode(self) -> None:
        self.ui_mode = next_ui_mode(self.ui_mode)

    @beartype
    def set_ui_mode(self, mode: UIMode | str) -> None:
        self.ui_mode = validate_ui_mode(mode)

    @beartype
    def show(self, *, block: bool = True) -> None:
        if not block:
            thread = threading.Thread(target=self._run_loop, daemon=True)
            thread.start()
            return
        self._run_loop()

    def _run_loop(self) -> None:
        pygame.init()
        pygame.display.set_caption(self._title)
        self._screen = pygame.display.set_mode(self._panel.window_size.pygame())
        renderer = RuntimeMetroGYMRenderer(self._panel.render_scale)
        clock = pygame.time.Clock()
        last_tick = pygame.time.get_ticks()
        try:
            while not self._closed.is_set():
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.close()
                    elif event.type == pygame.KEYDOWN:
                        self._handle_keydown(event)
                now = pygame.time.get_ticks()
                tick_interval = max(1, self._tick_ms / self.animation_ratio)
                while now - last_tick >= tick_interval:
                    self.tick()
                    last_tick += tick_interval
                self._panel.draw(self._screen, renderer, ui_mode=self.ui_mode)
                renderer.draw_speed_ratio(self._screen, self._panel.window_size, self.animation_ratio)
                renderer.draw_ui_mode(self._screen, self._panel.window_size, ui_mode_label(self.ui_mode))
                renderer.draw_help_prompt(self._screen, self._panel.window_size)
                if self._show_help:
                    renderer.draw_help_overlay(self._screen, self._panel.window_size)
                pygame.display.flip()
                clock.tick(60)
        finally:
            pygame.quit()

    @beartype
    def _handle_keydown(self, event: object) -> None:
        self._keyboard.handle_keydown(event)

    def close(self) -> None:
        self._closed.set()


def _rotate_path(path: list[object], start_at: float) -> list[object]:
    if not path or start_at == 0:
        return path
    index = round((start_at / 100) * len(path)) % len(path)
    return [*path[index:], *path[:index]]
