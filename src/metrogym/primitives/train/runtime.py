from __future__ import annotations

from collections.abc import Iterable, Sequence

from beartype import beartype

from metrogym.core.colors import ColorRGBA
from metrogym.core.constants import TRAIN_COLLISION_RADIUS
from metrogym.core.coordinates import Position, PositionLike, to_positions
from metrogym.core.train_assets import DEFAULT_TRAIN_ASSET, TrainAssetName, validate_train_asset_name
from metrogym.events import CollisionEvent


@beartype
class RuntimeTrain:
    @beartype
    def __init__(
        self,
        id: str,
        line_name: str,
        path: Sequence[PositionLike],
        color: ColorRGBA,
        control: object | None = None,
        asset: TrainAssetName | str = DEFAULT_TRAIN_ASSET,
    ):
        if not path:
            raise ValueError("Train path must not be empty.")
        self.id = id
        self.line_name = line_name
        self.path = to_positions(path)
        self.color = color
        self.control = control
        self.asset = validate_train_asset_name(asset)
        self._position = self.path[0]
        self._path_index = 0
        self._peers: list[RuntimeTrain] = []
        self._stopped = False
        self._wait_ticks = 0
        self.collision_events: list[CollisionEvent] = []

    @property
    def stopped(self) -> bool:
        return self._stopped

    @property
    def position(self) -> Position:
        return self._position

    @beartype
    def set_peers(self, peers: Iterable["RuntimeTrain"]) -> None:
        self._peers = list(peers)

    def reset(self) -> None:
        self._position = self.path[0]
        self._path_index = 0
        self._stopped = False
        self._wait_ticks = 0
        self.collision_events.clear()

    def update(self) -> None:
        if self.control is not None and self.control.emergency_stopped:
            self._stopped = True
            return

        if self._wait_ticks > 0:
            self._wait_ticks -= 1
            self._stopped = self._wait_ticks > 0
            return

        next_index = (self._path_index + 1) % len(self.path)
        next_point = self.path[next_index]

        if self.control is not None and not self.control.can_enter(self, self._position, next_point):
            self._stopped = True
            return

        for peer in self._peers:
            if peer is self:
                continue
            if next_point.distance(peer.position) < TRAIN_COLLISION_RADIUS:
                self._stopped = False
                self._wait_ticks = 2
                event = CollisionEvent(self.id, peer.id, next_point)
                self.collision_events.append(event)
                if self.control is not None:
                    self.control.record_collision(event)
                print(f"[COLLISION] {self.id} near {peer.id} at {next_point.pygame()}")
                return

        self._stopped = False
        self._position = next_point
        self._path_index = next_index

    def draw(self, surface: object, *args: object, **kwargs: object) -> None:
        renderer = kwargs.get("renderer")
        if renderer is None:
            raise ValueError("Train.draw requires renderer=...")
        renderer.draw_train(surface, self, *args)

    def __repr__(self) -> str:
        return f"Train(id={self.id!r}, line={self.line_name!r}, pos={self.position.pygame()})"


Train = RuntimeTrain
