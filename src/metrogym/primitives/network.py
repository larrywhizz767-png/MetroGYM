from __future__ import annotations

from collections.abc import Iterable

from beartype import beartype

from metrogym.primitives.line import Line
from metrogym.primitives.station import Station
from metrogym.templates.primitive import BaseMetroPrimitive


@beartype
class Network(BaseMetroPrimitive):
    primitive_group = "network"

    @beartype
    def __init__(self, primitives: Iterable[Line | Station]):
        self.primitives = list(primitives)

    @beartype
    def transform(self, context: object) -> object:
        context.network_count += 1
        if context.network_count > 1:
            raise ValueError("MetroSystem requires exactly one Network")
        for primitive in self.primitives:
            if not isinstance(primitive, (Line, Station)):
                raise ValueError("Network may only contain Line and Station primitives")
            primitive.fit_transform(context)
        return context
