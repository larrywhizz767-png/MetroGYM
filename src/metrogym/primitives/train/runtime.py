from __future__ import annotations

from collections.abc import Iterable, Sequence

from beartype import beartype

from metrogym.core.colors import ColorRGBA
from metrogym.core.constants import TRAIN_COLLISION_RADIUS
from metrogym.core.coordinates import Position, PositionLike, to_positions
from metrogym.core.train_assets import DEFAULT_TRAIN_ASSET, TrainAssetName, validate_train_asset_name
from metrogym.events import CollisionEvent
from metrogym.solvers import TrainAgent, TrainDecision, TrainVerb, reset_solver_state


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
        solver: object | None = None,
        speed: int = 1,
    ):
        if not path:
            raise ValueError("Train path must not be empty.")
        self.id = id
        self.line_name = line_name
        self.path = to_positions(path)
        self.color = color
        self.control = control
        self.asset = validate_train_asset_name(asset)
        self.solver = solver
        self.default_speed = max(0.0, float(speed))
        self.speed = self.default_speed
        self.target_speed = self.default_speed
        self.acceleration = 0.25
        self.deceleration = 0.35
        self._position = self.path[0]
        self._path_index = 0
        self._peers: list[RuntimeTrain] = []
        self._ignored_peer_ids: set[str] = set()
        self._active = True
        self._stopped = False
        self._wait_ticks = 0
        self.collision_events: list[CollisionEvent] = []

    @property
    def active(self) -> bool:
        return self._active

    @property
    def stopped(self) -> bool:
        return self._stopped

    @property
    def position(self) -> Position:
        return self._position

    @property
    def next_position(self) -> Position:
        next_index = (self._path_index + 1) % len(self.path)
        return self.path[next_index]

    @property
    def wait_ticks(self) -> int:
        return self._wait_ticks

    @beartype
    def set_peers(self, peers: Iterable["RuntimeTrain"]) -> None:
        self._peers = list(peers)

    @beartype
    def ignore_peers(self, peer_ids: Iterable[str]) -> None:
        self._ignored_peer_ids.update(peer_ids)

    def clear_ignored_peers(self) -> None:
        self._ignored_peer_ids.clear()

    def deactivate(self) -> None:
        self._active = False
        self._stopped = True
        self.speed = 0.0
        self.target_speed = 0.0

    def activate(self) -> None:
        self._active = True

    def reset(self) -> None:
        self._active = True
        self._position = self.path[0]
        self._path_index = 0
        self._stopped = False
        self._wait_ticks = 0
        self.speed = self.default_speed
        self.target_speed = self.default_speed
        self.collision_events.clear()
        self.clear_ignored_peers()
        reset_solver_state(self.solver)

    def update(self) -> None:
        if not self._active:
            self._stopped = True
            return
        if self.control is not None and self.control.emergency_stopped:
            self._stopped = True
            return

        if self._wait_ticks > 0:
            self._wait_ticks -= 1
            self._stopped = self._wait_ticks > 0
            return

        decision = self._solver_action()
        if decision.verb == TrainVerb.HOLD:
            self.target_speed = 0.0
            self._apply_speed_easing()
            self._stopped = self.speed <= 0.01
            return

        self._apply_speed_target(decision)
        self._apply_speed_easing()
        steps = int(self.speed)
        if steps <= 0:
            self._stopped = True
            return
        for _ in range(steps):
            if not self._advance_once(reverse=decision.verb == TrainVerb.REVERSE):
                return

    def _solver_action(self) -> TrainDecision:
        if self.solver is None or self.control is None or not hasattr(self.control, "simulator"):
            return TrainDecision(TrainVerb.PROCEED, target_speed=self.default_speed)
        if not isinstance(self.solver, TrainAgent):
            raise TypeError(f"Train solver {self.solver!r} must inherit from TrainAgent.")
        world = self.control.simulator.world_view(train_id=self.id)
        return self.solver(world.observe_train(self.id))

    def _apply_speed_target(self, decision: TrainDecision) -> None:
        if decision.target_speed is not None:
            self.target_speed = decision.target_speed
        elif decision.speed_delta is not None:
            self.target_speed = max(0.0, self.target_speed + decision.speed_delta)
        else:
            self.target_speed = self.default_speed

    def _apply_speed_easing(self) -> None:
        if self.speed < self.target_speed:
            self.speed = min(self.target_speed, self.speed + self.acceleration)
        elif self.speed > self.target_speed:
            self.speed = max(self.target_speed, self.speed - self.deceleration)

    def _advance_once(self, *, reverse: bool = False) -> bool:
        next_index = (self._path_index - 1 if reverse else self._path_index + 1) % len(self.path)
        next_point = self.path[next_index]

        if self.control is not None and not self.control.can_enter(self, self._position, next_point):
            self._stopped = True
            return False

        for peer in self._peers:
            if peer is self or not peer.active or peer.id in self._ignored_peer_ids:
                continue
            if next_point.distance(peer.position) < TRAIN_COLLISION_RADIUS:
                self._stopped = False
                self._wait_ticks = 2
                event = CollisionEvent(self.id, peer.id, next_point)
                self.collision_events.append(event)
                if self.control is not None:
                    self.control.record_collision(event)
                print(f"[COLLISION] {self.id} near {peer.id} at {next_point.pygame()}")
                return False

        self._stopped = False
        self._position = next_point
        self._path_index = next_index
        return True

    def draw(self, surface: object, *args: object, **kwargs: object) -> None:
        if not self._active:
            return
        renderer = kwargs.get("renderer")
        if renderer is None:
            raise ValueError("Train.draw requires renderer=...")
        renderer.draw_train(surface, self, *args)

    def __repr__(self) -> str:
        return f"Train(id={self.id!r}, line={self.line_name!r}, pos={self.position.pygame()})"


Train = RuntimeTrain
