from __future__ import annotations

"""Public station primitive for declarative world construction."""

from beartype import beartype

from metrogym.core.coordinates import PositionLike
from metrogym.templates.primitive import BaseMetroPrimitive
from metrogym.validation import validation_registry


@beartype
class Station(BaseMetroPrimitive):
    """Declare a named station marker on the network map.

    Stations are lightweight infrastructure primitives used to annotate the
    world, teach topology, and provide visual landmarks in examples.

    Args:
        name (str):
            Station name shown in the renderer.
        position (PositionLike):
            Station centre in world coordinates.
        radius (int, default=7):
            Marker radius used for rendering.

    Attributes:
        name (str):
            Station name.
        position (PositionLike):
            Declared station position.
        radius (int):
            Declared marker radius.

    Raises:
        ValueError:
            Raised through the validation registry when the station name is
            duplicated.
    """

    primitive_group = "network"
    network_only = True

    @beartype
    def __init__(self, name: str, position: PositionLike, radius: int = 7):
        self.name = name
        self.position = position
        self.radius = radius

    @beartype
    def transform(self, context: object) -> object:
        """Create the runtime station inside the simulator.

        Args:
            context (object):
                Build context receiving runtime objects.

        Returns:
            object:
                Updated build context.
        """
        registry = validation_registry()
        if self.name in context.station_names:
            registry.raise_issue(registry.primitive_issue("Station", "duplicate_name", path=f"Station[name={self.name}]", name=self.name))
        context.simulator.add_station(self.name, self.position, self.radius)
        context.station_names.add(self.name)
        return context
