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
            Station name used to identify the station.
        position (PositionLike):
            Station centre in world coordinates.
        radius (int, default=7):
            Marker radius used for rendering.
        label (str | None, default=None):
            Optional short label shown in the renderer.

    Attributes:
        name (str):
            Station name.
        position (PositionLike):
            Declared station position.
        radius (int):
            Declared marker radius.
        label (str | None):
            Optional short display label.

    Raises:
        ValueError:
            Raised through the validation registry when the station name is
            duplicated.

    Examples:
        !!! example "Highlight the `Station(...)` entries in the pipeline"

            ```python hl_lines="7-8"
            from metrogym import Color, MetroSystem, train
            from metrogym.primitives import Line, Network, Station, Train

            system = MetroSystem(name="Station Demo").pipeline([
                Network([
                    Line("Loop", Color.BLUE, [(120, 120), (420, 120), (420, 320), (120, 320), (120, 120)]),
                    Station("Origin", (120, 120)),
                    Station("East", (420, 120)),
                ]),
                Train("A", line="Loop", solver=train.always_hold()),
            ])
            ```
    """

    primitive_group = "network"
    network_only = True

    @beartype
    def __init__(self, name: str, position: PositionLike, radius: int = 7, label: str | None = None):
        self.name = name
        self.position = position
        self.radius = radius
        self.label = label

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
        context.simulator.add_station(self.name, self.position, self.radius, self.label)
        context.station_names.add(self.name)
        return context
