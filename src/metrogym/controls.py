from __future__ import annotations

from dataclasses import dataclass

from beartype import beartype

from metrogym.core.coordinates import Direction, Position, PositionLike, to_position
from metrogym.events import CollisionEvent
from metrogym.primitives.signal.control import is_entering_segment


@beartype
@dataclass(frozen=True)
class SignalRule:
    line_name: str
    start: Position
    end: Position
    light: object
    direction: Direction = "both"

    @beartype
    def blocks(self, train: object, current: Position, next_position: Position) -> bool:
        if train.line_name != self.line_name:
            return False
        if self.light.green:
            granted_train_id = getattr(self.light, "granted_train_id", None)
            if granted_train_id is not None:
                return train.id != granted_train_id
            granted_line = getattr(self.light, "granted_line", None)
            if granted_line is None or granted_line == self.line_name:
                return False
        if self.direction in {"forward", "both"} and is_entering_segment(self.start, self.end, current, next_position):
            return True
        if self.direction in {"reverse", "both"} and is_entering_segment(self.end, self.start, current, next_position):
            return True
        return False


@beartype
class ControlSystem:
    @beartype
    def __init__(self, lights: dict[str, object], *, stop_all_on_collision: bool = False):
        self._lights = lights
        self.stop_all_on_collision = stop_all_on_collision
        self.emergency_stopped = False
        self.collision_events: list[CollisionEvent] = []
        self.rules: list[SignalRule] = []

    @beartype
    def protect_segment(
        self,
        line: str | object,
        start: PositionLike,
        end: PositionLike,
        light: str | object,
        *,
        direction: Direction = "both",
    ) -> SignalRule:
        line_name = line.name if hasattr(line, "name") else line
        signal = self._lights[light] if isinstance(light, str) else light
        signal.control = self
        rule = SignalRule(line_name, to_position(start), to_position(end), signal, direction)
        self.rules.append(rule)
        return rule

    @beartype
    def can_enter(self, train: object, current: Position, next_position: Position) -> bool:
        if self.emergency_stopped:
            return False
        return not any(rule.blocks(train, current, next_position) for rule in self.rules)

    @beartype
    def record_collision(self, event: CollisionEvent) -> None:
        self.collision_events.append(event)
        if self.stop_all_on_collision:
            self.emergency_stopped = True

    def reset_emergency_stop(self) -> None:
        self.emergency_stopped = False

    @beartype
    def reset(self, *, clear_events: bool = True) -> None:
        self.emergency_stopped = False
        if clear_events:
            self.collision_events.clear()
