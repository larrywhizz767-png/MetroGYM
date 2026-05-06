from __future__ import annotations

from beartype import beartype

from metrogym.core.colors import ColorRGBA
from metrogym.core.train_assets import DEFAULT_TRAIN_ASSET, TrainAssetName, validate_train_asset_name
from metrogym.solvers import SolverLike
from metrogym.templates.primitive import BaseMetroPrimitive
from metrogym.validation import validation_registry


@beartype
class Train(BaseMetroPrimitive):
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
