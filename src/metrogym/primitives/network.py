from __future__ import annotations

"""Public network aggregator primitive for MetroGYM pipelines."""

from collections.abc import Iterable

from beartype import beartype

from metrogym.primitives.line import Line
from metrogym.primitives.station import Station
from metrogym.templates.primitive import BaseMetroPrimitive
from metrogym.validation import validation_registry


@beartype
class Network(BaseMetroPrimitive):
    """Group infrastructure primitives into the required network stage.

    A MetroGYM world must contain exactly one ``Network`` primitive. It acts as
    the container for all infrastructure declarations, currently limited to
    :class:`Line` and :class:`Station` primitives.

    Args:
        primitives (Iterable[Line | Station]):
            Infrastructure primitives to build as part of the world layout.

    Attributes:
        primitives (list[Line | Station]):
            Stored infrastructure primitives in declaration order.

    Raises:
        ValueError:
            Raised through the validation registry when multiple networks are
            declared or when a child primitive is not a line or station.

    Examples:
        !!! example "Build a network"

            ```python
            from metrogym import Color
            from metrogym.primitives import Line, Network, Station

            network = Network([
                Line("Loop", Color.BLUE, [(120, 120), (420, 120), (420, 300), (120, 300), (120, 120)]),
                Station("Central", (120, 120)),
                Station("East", (420, 120)),
            ])
            ```
    """

    primitive_group = "network"

    @beartype
    def __init__(self, primitives: Iterable[Line | Station]):
        self.primitives = list(primitives)

    @beartype
    def transform(self, context: object) -> object:
        """Apply every child primitive to the shared build context.

        Args:
            context (object):
                Build context being materialised during ``fit``.

        Returns:
            object:
                Updated build context.
        """
        registry = validation_registry()
        context.network_count += 1
        if context.network_count > 1:
            registry.raise_issue(registry.primitive_issue("Network", "one_network_only", path="Network"))
        for primitive in self.primitives:
            if not isinstance(primitive, (Line, Station)):
                registry.raise_issue(registry.primitive_issue("Network", "allowed_child_types", path=f"Network.{type(primitive).__name__}"))
            primitive.fit_transform(context)
        return context
