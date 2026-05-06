from __future__ import annotations

from collections.abc import Iterable

from beartype import beartype

from metrogym.primitives.line import Line
from metrogym.primitives.station import Station
from metrogym.templates.primitive import BaseMetroPrimitive
from metrogym.validation import validation_registry


@beartype
class Network(BaseMetroPrimitive):
    primitive_group = "network"

    @beartype
    def __init__(self, primitives: Iterable[Line | Station]):
        self.primitives = list(primitives)

    @beartype
    def transform(self, context: object) -> object:
        registry = validation_registry()
        context.network_count += 1
        if context.network_count > 1:
            registry.raise_issue(registry.primitive_issue("Network", "one_network_only", path="Network"))
        for primitive in self.primitives:
            if not isinstance(primitive, (Line, Station)):
                registry.raise_issue(registry.primitive_issue("Network", "allowed_child_types", path=f"Network.{type(primitive).__name__}"))
            primitive.fit_transform(context)
        return context
