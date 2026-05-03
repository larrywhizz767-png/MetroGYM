from __future__ import annotations

from collections.abc import Sequence

import pygame
from beartype import beartype

from metrogym.core.colors import Color
from metrogym.core.coordinates import Position
from metrogym.core.signal_assets import load_signal_asset_surface, signal_asset
from metrogym.core.train_assets import load_train_asset_surface, train_asset
from metrogym.core.ui_modes import UIMode
from metrogym.primitives.signal.runtime import RuntimeTrafficLight
from metrogym.primitives.station.runtime import RuntimeStation
from metrogym.primitives.train.runtime import RuntimeTrain
from metrogym.rendering._utils import gfx
from metrogym.rendering.primitives.metrogym_renderer.extras.constants import GRID_STEP, HELP_OVERLAY_ROWS


@beartype
class RuntimeMetroGYMRenderer:
    @beartype
    def __init__(self, scale: int | float):
        self.scale = float(scale)
        self.fonts = {
            "line": gfx.font(gfx.ROOBERT_SEMIBOLD, gfx.scale_value(10, self.scale)),
            "station": gfx.font(gfx.ROOBERT_SEMIBOLD, gfx.scale_value(9, self.scale)),
            "train": gfx.font(gfx.ROOBERT_BOLD, gfx.scale_value(8, self.scale)),
            "light_label": gfx.font(gfx.ROOBERT_SEMIBOLD, gfx.scale_value(9, self.scale)),
            "light_small": gfx.font(gfx.ROOBERT_REGULAR, gfx.scale_value(7, self.scale)),
            "hud": gfx.font(gfx.ROOBERT_BOLD, gfx.scale_value(12, self.scale)),
            "legend": gfx.font(gfx.ROOBERT_MEDIUM, gfx.scale_value(10, self.scale)),
        }

    @beartype
    def draw_panel(self, surface: object, panel: object, *, ui_mode: UIMode = "minimal") -> None:
        width, height = panel.window_size.pygame()
        self.draw_background(surface, width, height)
        self.draw_grid(surface, width, height)
        track_alpha = 64 if ui_mode == "dynamic" else 255
        object_alpha = 64 if ui_mode == "static" else 255
        show_train_labels = ui_mode in {"full", "dynamic", "static"}
        show_signal_details = ui_mode in {"full", "dynamic", "static"}
        for track_line in panel.track_lines:
            self.draw_track(surface, track_line, alpha=track_alpha)
        for station in panel.stations:
            self.draw_station(surface, station)
        for obj in panel.objects:
            if isinstance(obj, RuntimeTrain):
                self.draw_train(surface, obj, alpha=object_alpha, show_label=show_train_labels)
            elif isinstance(obj, RuntimeTrafficLight):
                self.draw_traffic_light(surface, obj, alpha=object_alpha, show_details=show_signal_details)
        self.draw_hud(surface, panel.track_lines, panel.tick_count, width, height)

    @beartype
    def draw_background(self, surface: object, width: int, height: int) -> None:
        surface.fill(Color.BACKGROUND.pygame())

    @beartype
    def draw_grid(self, surface: object, width: int, height: int) -> None:
        step = gfx.scale_value(GRID_STEP, self.scale)
        for x in range(0, width, step):
            gfx.line(surface, Position(x, 0), Position(x, height), Color.GRID_LINE, gfx.scale_value(1, self.scale))
        for y in range(0, height, step):
            gfx.line(surface, Position(0, y), Position(width, y), Color.GRID_LINE, gfx.scale_value(1, self.scale))

    @beartype
    def draw_track(self, surface: object, track_line: object, *, alpha: int = 255) -> None:
        if len(track_line.path) < 2:
            return
        points = [Position(*gfx.scale_position(point, self.scale)) for point in track_line.path]
        base_alpha = max(0, min(255, alpha))
        highlight_alpha = max(0, min(100, round(100 * base_alpha / 255)))
        dark = track_line.color.darker().darker()
        mid = track_line.color.darker()
        gfx.polyline(surface, points, (dark.r, dark.g, dark.b, base_alpha), gfx.scale_value(6, self.scale))
        gfx.polyline(surface, points, (mid.r, mid.g, mid.b, base_alpha), gfx.scale_value(3, self.scale))
        gfx.polyline(surface, points, (track_line.color.r, track_line.color.g, track_line.color.b, highlight_alpha), gfx.scale_value(1.5, self.scale))

    @beartype
    def draw_station(self, surface: object, station: RuntimeStation) -> None:
        center = Position(*gfx.scale_position(station.position, self.scale))
        radius = gfx.scale_value(station.radius, self.scale)
        gfx.filled_circle(surface, center, radius, Color.STATION_BORDER)
        gfx.filled_circle(surface, center, max(1, radius - gfx.scale_value(3, self.scale)), Color.STATION_FILL)
        label = self.fonts["station"].render(station.name, True, Color.STATION_LABEL.pygame())
        surface.blit(label, label.get_rect(center=(center.x, center.y + radius + gfx.scale_value(10, self.scale))))

    @beartype
    def draw_train(self, surface: object, train: RuntimeTrain, *, alpha: int = 255, show_label: bool = True) -> None:
        x, y = gfx.scale_position(train.position, self.scale)
        asset = train_asset(train.asset)
        sprite = _with_alpha(load_train_asset_surface(train.asset, scale=self.scale), alpha)
        rect = sprite.get_rect(center=(x, y))
        if train.stopped:
            glow_padding = gfx.scale_value(3, self.scale)
            glow = rect.inflate(glow_padding * 2, glow_padding * 2)
            gfx.outline_rect(surface, glow, Color.YELLOW, gfx.scale_value(2, self.scale))
        surface.blit(sprite, rect)
        if show_label:
            label = self.fonts["train"].render(train.line_name, True, (255, 255, 255))
            surface.blit(label, label.get_rect(center=(x, y + gfx.scale_value(asset.height // 2 + 7, self.scale))))

    @beartype
    def draw_traffic_light(self, surface: object, light: RuntimeTrafficLight, *, alpha: int = 255, show_details: bool = True) -> None:
        x, y = gfx.scale_position(light.position, self.scale)
        state = "go" if light.green else "stop"
        asset = signal_asset(state)
        sprite = _with_alpha(load_signal_asset_surface(state, scale=self.scale), alpha)
        rect = sprite.get_rect(center=(x, y))
        surface.blit(sprite, rect)
        if show_details and light.label is not None:
            text = self.fonts["light_label"].render(light.label, True, (210, 210, 210))
            surface.blit(text, (rect.right + gfx.scale_value(4, self.scale), rect.centery - gfx.scale_value(5, self.scale)))
        if show_details:
            counter = self.fonts["light_small"].render(f"{light.ticks_since_change}/{light.period_ticks}", True, (200, 200, 200))
            surface.blit(counter, counter.get_rect(center=(x, y - gfx.scale_value(asset.height // 2 + 7, self.scale))))

    @beartype
    def draw_hud(self, surface: object, lines: Sequence[object], tick_count: int, width: int, height: int) -> None:
        bar_height = gfx.scale_value(28, self.scale)
        bar_y = height - bar_height
        overlay = pygame.Surface((width, bar_height), pygame.SRCALPHA)
        overlay.fill((10, 14, 25, 200))
        surface.blit(overlay, (0, bar_y))
        gfx.line(surface, Position(0, bar_y), Position(width, bar_y), (60, 80, 110), gfx.scale_value(1, self.scale))
        tick = self.fonts["hud"].render(f"TICK  {tick_count:04d}", True, Color.STATUS_TEXT.pygame())
        surface.blit(tick, (gfx.scale_value(8, self.scale), bar_y + gfx.scale_value(8, self.scale)))
        legend_x = gfx.scale_value(130, self.scale)
        for line in lines:
            gfx.filled_rect(surface, pygame.Rect(legend_x, bar_y + gfx.scale_value(9, self.scale), gfx.scale_value(16, self.scale), gfx.scale_value(8, self.scale)), line.color)
            label = self.fonts["legend"].render(line.name, True, Color.STATUS_TEXT.pygame())
            surface.blit(label, (legend_x + gfx.scale_value(20, self.scale), bar_y + gfx.scale_value(7, self.scale)))
            legend_x += label.get_width() + gfx.scale_value(34, self.scale)

    @beartype
    def draw_speed_ratio(self, surface: object, size: Position, animation_ratio: int | float) -> None:
        text = self.fonts["legend"].render(f"Speed {animation_ratio:.1f}x", True, Color.HIGHLIGHT.pygame())
        self._draw_top_right_badge(surface, size, text, gfx.scale_value(10, self.scale))

    @beartype
    def draw_ui_mode(self, surface: object, size: Position, mode_label: str) -> None:
        text = self.fonts["legend"].render(f"Mode {mode_label}", True, Color.STATUS_TEXT.pygame())
        self._draw_top_right_badge(surface, size, text, gfx.scale_value(44, self.scale))

    @beartype
    def _draw_top_right_badge(self, surface: object, size: Position, text: object, top: int) -> None:
        padding_x = gfx.scale_value(10, self.scale)
        padding_y = gfx.scale_value(6, self.scale)
        rect = pygame.Rect(
            size.x - text.get_width() - padding_x * 2 - gfx.scale_value(10, self.scale),
            top,
            text.get_width() + padding_x * 2,
            text.get_height() + padding_y * 2,
        )
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel.fill((10, 14, 25, 170))
        surface.blit(panel, rect.topleft)
        gfx.outline_rect(surface, rect, (80, 105, 145), gfx.scale_value(1, self.scale))
        surface.blit(text, (rect.x + padding_x, rect.y + padding_y))

    @beartype
    def draw_help_prompt(self, surface: object, size: Position) -> None:
        text = self.fonts["legend"].render("Ctrl+H help", True, Color.STATUS_TEXT.pygame())
        padding_x = gfx.scale_value(10, self.scale)
        padding_y = gfx.scale_value(6, self.scale)
        rect = pygame.Rect(
            size.x - text.get_width() - padding_x * 2 - gfx.scale_value(10, self.scale),
            size.y - text.get_height() - padding_y * 2 - gfx.scale_value(38, self.scale),
            text.get_width() + padding_x * 2,
            text.get_height() + padding_y * 2,
        )
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel.fill((10, 14, 25, 170))
        surface.blit(panel, rect.topleft)
        gfx.outline_rect(surface, rect, (80, 105, 145), gfx.scale_value(1, self.scale))
        surface.blit(text, (rect.x + padding_x, rect.y + padding_y))

    @beartype
    def draw_help_overlay(self, surface: object, size: Position) -> None:
        width = gfx.scale_value(380, self.scale)
        row_h = gfx.scale_value(24, self.scale)
        height = gfx.scale_value(28, self.scale) + row_h * (len(HELP_OVERLAY_ROWS) - 1) + gfx.scale_value(24, self.scale)
        rect = pygame.Rect((size.x - width) // 2, (size.y - height) // 2, width, height)
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel.fill((10, 14, 25, 220))
        surface.blit(panel, rect.topleft)
        gfx.outline_rect(surface, rect, (120, 150, 200), gfx.scale_value(1, self.scale))
        title = self.fonts["hud"].render(HELP_OVERLAY_ROWS[0], True, Color.HIGHLIGHT.pygame())
        surface.blit(title, (rect.x + gfx.scale_value(18, self.scale), rect.y + gfx.scale_value(16, self.scale)))
        y = rect.y + gfx.scale_value(50, self.scale)
        for line in HELP_OVERLAY_ROWS[1:]:
            rendered = self.fonts["legend"].render(line, True, Color.STATUS_TEXT.pygame())
            surface.blit(rendered, (rect.x + gfx.scale_value(18, self.scale), y))
            y += row_h


def _with_alpha(surface: object, alpha: int) -> object:
    alpha = max(0, min(255, alpha))
    if alpha >= 255:
        return surface
    copy = surface.copy()
    copy.set_alpha(alpha)
    return copy
