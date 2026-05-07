from __future__ import annotations

"""Public color helpers used throughout MetroGYM.

This module exposes :class:`ColorRGBA` for explicit RGBA values and a callable
``Color`` factory with a small built-in palette. The palette is meant to make
teaching examples concise while still allowing fully custom colours.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from beartype import beartype


@beartype
@dataclass(frozen=True)
class ColorRGBA:
    """Represent an RGBA colour with 8-bit channels.

    MetroGYM uses explicit colour objects instead of raw tuples so that examples
    remain readable and helper methods such as :meth:`darker` and
    :meth:`brighter` stay discoverable.

    Args:
        r (int):
            Red channel in the range ``0`` to ``255``.
        g (int):
            Green channel in the range ``0`` to ``255``.
        b (int):
            Blue channel in the range ``0`` to ``255``.
        a (int, default=255):
            Alpha channel in the range ``0`` to ``255``.

    Raises:
        ValueError:
            If any channel is outside the ``0..255`` range.

    Examples:
        !!! example "Create a custom colour"

            ```python
            from metrogym import ColorRGBA

            accent = ColorRGBA(80, 200, 255)
            ```
    """

    r: int
    g: int
    b: int
    a: int = 255

    def __post_init__(self) -> None:
        """Validate channel bounds after dataclass construction."""
        for value in (self.r, self.g, self.b, self.a):
            if not 0 <= value <= 255:
                raise ValueError("colour channels must be in the range 0..255")

    def darker(self) -> "ColorRGBA":
        """Return a darker version of the colour.

        Returns:
            ColorRGBA:
                A copy scaled down to roughly 70% brightness.
        """
        return self.scale(0.70)

    def brighter(self) -> "ColorRGBA":
        """Return a brighter version of the colour.

        Returns:
            ColorRGBA:
                A copy scaled up while clamping channels to ``255``.
        """
        return ColorRGBA(
            min(255, int(self.r / 0.70)),
            min(255, int(self.g / 0.70)),
            min(255, int(self.b / 0.70)),
            self.a,
        )

    def scale(self, factor: float) -> "ColorRGBA":
        """Scale the RGB channels by a multiplier.

        Args:
            factor (float):
                Brightness multiplier applied to the red, green, and blue
                channels.

        Returns:
            ColorRGBA:
                A new colour with scaled RGB channels and unchanged alpha.
        """
        return ColorRGBA(
            max(0, min(255, int(self.r * factor))),
            max(0, min(255, int(self.g * factor))),
            max(0, min(255, int(self.b * factor))),
            self.a,
        )

    def getRed(self) -> int:
        """Return the red channel.

        Returns:
            int:
                The red channel value.
        """
        return self.r

    def getGreen(self) -> int:
        """Return the green channel.

        Returns:
            int:
                The green channel value.
        """
        return self.g

    def getBlue(self) -> int:
        """Return the blue channel.

        Returns:
            int:
                The blue channel value.
        """
        return self.b

    def pygame(self) -> tuple[int, int, int, int]:
        """Convert the colour to a pygame-friendly tuple.

        Returns:
            tuple[int, int, int, int]:
                ``(r, g, b, a)``.
        """
        return self.r, self.g, self.b, self.a


@beartype
class _ColorFactory:
    """Callable palette and colour factory for concise public examples.

    The exported ``Color`` object is an instance of this class. Users can either
    reference named palette entries such as ``Color.BLUE`` or call ``Color(...)``
    to build a custom :class:`ColorRGBA`.
    """

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
        """Create a colour from channels or a sequence.

        Args:
            r (int | Sequence[int]):
                Either the red channel or a sequence containing three or four
                integer channels.
            g (int | None, default=None):
                Green channel when passing channels separately.
            b (int | None, default=None):
                Blue channel when passing channels separately.
            a (int | None, default=None):
                Optional alpha channel when passing channels separately.

        Returns:
            ColorRGBA:
                The resulting colour object.

        Raises:
            ValueError:
                If the input does not contain exactly three RGB channels or four
                RGBA channels.
        """
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
        """Return a darker copy of a colour.

        Args:
            color (ColorRGBA):
                Colour to darken.

        Returns:
            ColorRGBA:
                Darkened colour.
        """
        return color.darker()


Color = _ColorFactory()
