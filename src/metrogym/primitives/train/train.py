from __future__ import annotations

"""Public train primitive for declarative rolling-stock setup."""

from beartype import beartype

from metrogym.core.colors import ColorRGBA
from metrogym.core.train_assets import DEFAULT_TRAIN_ASSET, TrainAssetName, validate_train_asset_name
from metrogym.solvers import SolverLike
from metrogym.templates.primitive import BaseMetroPrimitive
from metrogym.validation import validation_registry


@beartype
class Train(BaseMetroPrimitive):
    """Declare a train that runs on a named line.

    The train primitive connects declarative world construction with agent-based
    control. It chooses a line, optional visual asset, optional solver, and
    starting offset along the line path.

    Args:
        id (str):
            Unique train identifier.
        line (str):
            Name of the line the train belongs to.
        color (ColorRGBA | None, default=None):
            Optional override for the line colour.
        start_at (int | float, default=0):
            Percentage along the line path where the train starts.
        peer_with_line (bool, default=True):
            If ``True``, auto-link this train with same-line peers for collision
            checks.
        asset (TrainAssetName | str, default=DEFAULT_TRAIN_ASSET):
            Train sprite asset name. Supported values are ``"metro_nose"``,
            ``"maintenance"``, ``"city_tram"``, and ``"bullet_metro"``.
        solver (SolverLike | None, default=None):
            Optional train solver or train agent.
        speed (int | float, default=1):
            Default runtime speed in path steps per tick.

    Attributes:
        id (str):
            Train identifier.
        line (str):
            Referenced line name.
        color (ColorRGBA | None):
            Optional colour override.
        start_at (int | float):
            Starting offset percentage.
        peer_with_line (bool):
            Whether to auto-link line peers.
        asset (TrainAssetName):
            Validated train asset name.
        solver (SolverLike | None):
            Optional solver.
        speed (int | float):
            Declared default speed.

    Raises:
        ValueError:
            Raised through the validation registry when the train id is
            duplicated, the line is unknown, or speed is negative.

    Examples:
        Add a train as its own top-level pipeline step after the network.

        ```python hl_lines="9"
        from metrogym import Color, MetroSystem, train
        from metrogym.primitives import Line, Network, Station, Train

        system = MetroSystem(name="Train Demo").pipeline([
            Network([
                Line("Loop", Color.BLUE, [(120, 120), (420, 120), (420, 320), (120, 320), (120, 120)]),
                Station("Origin", (120, 120)),
            ]),
            Train("A", line="Loop", solver=train.always_proceed()),
        ])
        ```
    """

    primitive_group = "rolling_stock"

    @beartype
    def __init__(
        self,
        id: str,
        line: str,
        *,
        color: ColorRGBA | None = None,
        start_at: int | float = 0,
        peer_with_line: bool = True,
        asset: TrainAssetName | str = DEFAULT_TRAIN_ASSET,
        solver: SolverLike | None = None,
        speed: int | float = 1,
    ):
        self.id = id
        self.line = line
        self.color = color
        self.start_at = start_at
        self.peer_with_line = peer_with_line
        self.asset = validate_train_asset_name(asset)
        self.solver = solver
        self.speed = speed

    @beartype
    def transform(self, context: object) -> object:
        """Create the runtime train inside the simulator.

        Args:
            context (object):
                Build context receiving runtime objects.

        Returns:
            object:
                Updated build context.
        """
        registry = validation_registry()
        if self.id in context.train_ids:
            registry.raise_issue(registry.primitive_issue("Train", "duplicate_id", path=f"Train[id={self.id}]", id=self.id))
        if self.line not in context.line_names:
            registry.raise_issue(registry.primitive_issue("Train", "unknown_line", path=f"Train[id={self.id}].line", id=self.id, line=self.line))
        if float(self.speed) < 0:
            registry.raise_issue(registry.cross_object_issue("speed_profile_valid", path=f"Train[id={self.id}].speed", id=self.id, detail="speed must be non-negative"))
        context.simulator.add_train(self.id, self.line, color=self.color, start_at=self.start_at, asset=self.asset, solver=self.solver, speed=self.speed)
        context.train_ids.add(self.id)
        context.train_lines[self.id] = self.line
        if self.peer_with_line:
            context.auto_peer_trains.setdefault(self.line, []).append(self.id)
        return context
