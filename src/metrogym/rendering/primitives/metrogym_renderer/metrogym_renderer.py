from __future__ import annotations

from beartype import beartype

from metrogym.templates.primitive import BaseMetroPrimitive


@beartype
class MetroGYMRenderer(BaseMetroPrimitive):
    primitive_group = "rendering"

    @beartype
    def __init__(self, *, scale: int | float | None = None):
        self.scale = scale

    @beartype
    def transform(self, context: object) -> object:
        return context
