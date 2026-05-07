from __future__ import annotations

"""Public line primitive for declarative world construction."""

from collections.abc import Sequence

from beartype import beartype

from metrogym.core.colors import ColorRGBA
from metrogym.core.coordinates import PositionLike
from metrogym.templates.primitive import BaseMetroPrimitive
from metrogym.validation import validation_registry


@beartype
class Line(BaseMetroPrimitive):
    """Declare a named metro line from colour and waypoints.

    A line is an infrastructure primitive that is built inside a
    :class:`~metrogym.primitives.network.Network`. During fitting, the declared
    waypoints are converted into a full runtime path that trains can follow.

    Args:
        name (str):
            Public name of the line.
        color (ColorRGBA):
            Colour used for rendering the line and, by default, for trains added
            to it.
        waypoints (Sequence[PositionLike]):
            Ordered anchor points describing the line geometry.

    Attributes:
        name (str):
            Line name.
        color (ColorRGBA):
            Declared line colour.
        waypoints (list[PositionLike]):
            Stored waypoint sequence.

    Raises:
        ValueError:
            Raised through the validation registry when the line name is
            duplicated.
    """

    primitive_group = "network"
    network_only = True

    @beartype
    def __init__(self, name: str, color: ColorRGBA, waypoints: Sequence[PositionLike]):
        self.name = name
        self.color = color
        self.waypoints = list(waypoints)

    @beartype
    def transform(self, context: object) -> object:
        """Create the runtime line inside the simulator.

        Args:
            context (object):
                Build context receiving runtime objects.

        Returns:
            object:
                Updated build context.
        """
        registry = validation_registry()
        if self.name in context.line_names:
            registry.raise_issue(registry.primitive_issue("Line", "duplicate_name", path=f"Line[name={self.name}]", name=self.name))
        context.simulator.add_line(self.name, self.color, self.waypoints)
        context.line_names.add(self.name)
        return context
