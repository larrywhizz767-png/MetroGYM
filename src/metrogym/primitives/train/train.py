from __future__ import annotations

from beartype import beartype

from metrogym.core.colors import ColorRGBA
from metrogym.core.train_assets import DEFAULT_TRAIN_ASSET, TrainAssetName, validate_train_asset_name
from metrogym.templates.primitive import BaseMetroPrimitive


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
    ):
        self.id = id
        self.line = line
        self.color = color
        self.start_at = start_at
        self.peer_with_line = peer_with_line
        self.asset = validate_train_asset_name(asset)

    @beartype
    def transform(self, context: object) -> object:
        if self.id in context.train_ids:
            raise ValueError(f"Duplicate train id: {self.id}")
        if self.line not in context.line_names:
            raise ValueError(f"Train {self.id!r} references unknown line {self.line!r}")
        context.simulator.add_train(self.id, self.line, color=self.color, start_at=self.start_at, asset=self.asset)
        context.train_ids.add(self.id)
        context.train_lines[self.id] = self.line
        if self.peer_with_line:
            context.auto_peer_trains.setdefault(self.line, []).append(self.id)
        return context
