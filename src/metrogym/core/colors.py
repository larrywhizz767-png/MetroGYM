from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from beartype import beartype


@beartype
@dataclass(frozen=True)
class ColorRGBA:
    r: int
    g: int
    b: int
    a: int = 255

    def __post_init__(self) -> None:
        for value in (self.r, self.g, self.b, self.a):
            if not 0 <= value <= 255:
                raise ValueError("colour channels must be in the range 0..255")

    def darker(self) -> "ColorRGBA":
        return self.scale(0.70)

    def brighter(self) -> "ColorRGBA":
        return ColorRGBA(
            min(255, int(self.r / 0.70)),
            min(255, int(self.g / 0.70)),
            min(255, int(self.b / 0.70)),
            self.a,
        )

    def scale(self, factor: float) -> "ColorRGBA":
        return ColorRGBA(
            max(0, min(255, int(self.r * factor))),
            max(0, min(255, int(self.g * factor))),
            max(0, min(255, int(self.b * factor))),
            self.a,
        )

    def getRed(self) -> int:
        return self.r

    def getGreen(self) -> int:
        return self.g

    def getBlue(self) -> int:
        return self.b

    def pygame(self) -> tuple[int, int, int, int]:
        return self.r, self.g, self.b, self.a


@beartype
class _ColorFactory:
    RED = ColorRGBA(220, 36, 31)
    BLUE = ColorRGBA(0, 114, 198)
    GREEN = ColorRGBA(0, 160, 90)
    YELLOW = ColorRGBA(255, 206, 0)
    PURPLE = ColorRGBA(120, 80, 180)
    BACKGROUND = ColorRGBA(22, 28, 42)
    GRID_LINE = ColorRGBA(45, 56, 80)
    STATION_FILL = ColorRGBA(235, 240, 245)
    STATION_BORDER = ColorRGBA(30, 35, 45)
    STATION_LABEL = ColorRGBA(230, 235, 245)
    PANEL_BG = ColorRGBA(12, 17, 28)
    STATUS_TEXT = ColorRGBA(220, 230, 245)
    HIGHLIGHT = ColorRGBA(255, 215, 0)

    @beartype
    def __call__(self, r: int | Sequence[int], g: int | None = None, b: int | None = None, a: int | None = None) -> ColorRGBA:
        if g is None:
            values = list(r)  # type: ignore[arg-type]
            if len(values) == 3:
                return ColorRGBA(int(values[0]), int(values[1]), int(values[2]))
            if len(values) == 4:
                return ColorRGBA(int(values[0]), int(values[1]), int(values[2]), int(values[3]))
            raise ValueError("Color expects (r, g, b) or (r, g, b, a)")
        if b is None:
            raise ValueError("Color expects r, g and b channels")
        if a is None:
            return ColorRGBA(int(r), int(g), int(b))  # type: ignore[arg-type]
        return ColorRGBA(int(r), int(g), int(b), int(a))  # type: ignore[arg-type]

    @beartype
    def darker(self, color: ColorRGBA) -> ColorRGBA:
        return color.darker()


Color = _ColorFactory()
