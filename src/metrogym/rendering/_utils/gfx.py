from __future__ import annotations

import math
from collections.abc import Sequence
from pathlib import Path

import pygame
import pygame.gfxdraw
from beartype import beartype

from metrogym.core.colors import ColorRGBA
from metrogym.core.coordinates import Position
from metrogym.rendering.primitives.metrogym_renderer.extras.assets import ROOBERT_BOLD, ROOBERT_MEDIUM, ROOBERT_REGULAR, ROOBERT_SEMIBOLD


@beartype
def font(path: Path, size: int) -> object:
    if path.exists():
        return pygame.font.Font(path, size)
    return pygame.font.Font(None, size)


@beartype
def scale_value(value: int | float, scale: int | float) -> int:
    return max(1, int(round(value * scale)))


@beartype
def scale_position(position: Position, scale: int | float) -> tuple[int, int]:
    return scale_value(position.x, scale), scale_value(position.y, scale)


@beartype
def rgba(color: ColorRGBA | tuple[int, int, int] | tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    if isinstance(color, ColorRGBA):
        return color.pygame()
    if len(color) == 3:
        return color[0], color[1], color[2], 255
    return color


@beartype
def filled_circle(surface: object, center: Position, radius: int, color: ColorRGBA) -> None:
    colour = rgba(color)
    pygame.gfxdraw.aacircle(surface, center.x, center.y, radius, colour)
    pygame.gfxdraw.filled_circle(surface, center.x, center.y, radius, colour)


@beartype
def outline_circle(surface: object, center: Position, radius: int, color: ColorRGBA | tuple[int, int, int], width: int = 1) -> None:
    colour = rgba(color)
    for offset in range(width):
        pygame.gfxdraw.aacircle(surface, center.x, center.y, max(1, radius - offset), colour)


@beartype
def filled_rect(surface: object, rect: object, color: ColorRGBA | tuple[int, int, int] | tuple[int, int, int, int]) -> None:
    pygame.gfxdraw.box(surface, rect, rgba(color))


@beartype
def line(surface: object, start: Position, end: Position, color: ColorRGBA | tuple[int, int, int] | tuple[int, int, int, int], width: int = 1) -> None:
    colour = rgba(color)
    if width <= 1:
        pygame.gfxdraw.line(surface, start.x, start.y, end.x, end.y, colour)
        return
    dx = end.x - start.x
    dy = end.y - start.y
    length = math.hypot(dx, dy)
    if length == 0:
        filled_circle(surface, start, max(1, width // 2), ColorRGBA(colour[0], colour[1], colour[2], colour[3]))
        return
    nx = -dy / length * width / 2
    ny = dx / length * width / 2
    points = [
        (round(start.x + nx), round(start.y + ny)),
        (round(end.x + nx), round(end.y + ny)),
        (round(end.x - nx), round(end.y - ny)),
        (round(start.x - nx), round(start.y - ny)),
    ]
    pygame.gfxdraw.aapolygon(surface, points, colour)
    pygame.gfxdraw.filled_polygon(surface, points, colour)


@beartype
def polyline(surface: object, points: Sequence[Position], color: ColorRGBA | tuple[int, int, int] | tuple[int, int, int, int], width: int) -> None:
    for start, end in zip(points, points[1:]):
        line(surface, start, end, color, width)


@beartype
def filled_rounded_rect(surface: object, rect: object, radius: int, color: ColorRGBA | tuple[int, int, int]) -> None:
    rgba_color = rgba(color)
    filled_rect(surface, rect, rgba_color)


@beartype
def outline_rect(surface: object, rect: object, color: ColorRGBA | tuple[int, int, int], width: int) -> None:
    for offset in range(width):
        inset = rect.inflate(-2 * offset, -2 * offset)
        line(surface, Position(inset.left, inset.top), Position(inset.right, inset.top), color, 1)
        line(surface, Position(inset.right, inset.top), Position(inset.right, inset.bottom), color, 1)
        line(surface, Position(inset.right, inset.bottom), Position(inset.left, inset.bottom), color, 1)
        line(surface, Position(inset.left, inset.bottom), Position(inset.left, inset.top), color, 1)
