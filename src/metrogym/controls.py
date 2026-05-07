from __future__ import annotations

"""Public signal-control coordination for runtime worlds."""

from dataclasses import dataclass

from beartype import beartype

from metrogym.core.coordinates import Direction, Position, PositionLike, to_position
from metrogym.events import CollisionEvent
from metrogym.primitives.signal.control import is_entering_segment


@beartype
@dataclass(frozen=True)
class SignalRule:
    """Protect a line segment behind a traffic light.

    Args:
        line_name (str):
            Name of the protected line.
        start (Position):
            First endpoint of the protected segment.
        end (Position):
            Second endpoint of the protected segment.
        light (object):
            Runtime traffic light governing the segment.
        direction (Direction, default=\"both\"):
            Travel direction that the rule applies to.
    """

    line_name: str
    start: Position
    end: Position
    light: object
    direction: Direction = "both"

    @beartype
    def blocks(self, train: object, current: Position, next_position: Position) -> bool:
        """Return whether the rule blocks a train from entering its segment.

        Args:
            train (object):
                Runtime train being checked.
            current (Position):
                Train position before movement.
            next_position (Position):
                Candidate next position.

        Returns:
            bool:
                ``True`` when the train should be blocked.
        """
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
    """Coordinate signals, protected segments, and emergency-stop state.

    ``ControlSystem`` is the runtime authority that knows which line segments are
    currently protected, whether trains may enter them, and whether the world is
    in an emergency-stop state after collisions.

    Args:
        lights (dict[str, object]):
            Mapping of traffic-light identifiers to runtime light objects.
        stop_all_on_collision (bool, default=False):
            If ``True``, any recorded collision activates an emergency stop.

    Attributes:
        emergency_stopped (bool):
            Whether the network is currently emergency-stopped.
        collision_events (list[CollisionEvent]):
            Recorded collision history for the current run.
        rules (list[SignalRule]):
            Protected line-segment rules.
    """

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
        """Create a protection rule for a line segment.

        Args:
            line (str | object):
                Line name or runtime line object.
            start (PositionLike):
                Start of the protected segment.
            end (PositionLike):
                End of the protected segment.
            light (str | object):
                Light identifier or runtime light object.
            direction (Direction, default=\"both\"):
                Travel direction to protect.

        Returns:
            SignalRule:
                The created protection rule.
        """
        line_name = line.name if hasattr(line, "name") else line
        signal = self._lights[light] if isinstance(light, str) else light
        signal.control = self
        rule = SignalRule(line_name, to_position(start), to_position(end), signal, direction)
        self.rules.append(rule)
        return rule

    @beartype
    def can_enter(self, train: object, current: Position, next_position: Position) -> bool:
        """Return whether a train may enter its next segment.

        Args:
            train (object):
                Runtime train being checked.
            current (Position):
                Current train position.
            next_position (Position):
                Candidate next position.

        Returns:
            bool:
                ``True`` when entry is permitted.
        """
        if self.emergency_stopped:
            return False
        return not any(rule.blocks(train, current, next_position) for rule in self.rules)

    @beartype
    def record_collision(self, event: CollisionEvent) -> None:
        """Record a collision and update emergency-stop state if configured.

        Args:
            event (CollisionEvent):
                Collision event to record.
        """
        self.collision_events.append(event)
        if self.stop_all_on_collision:
            self.emergency_stopped = True

    def reset_emergency_stop(self) -> None:
        """Clear the emergency-stop flag without removing collision history."""
        self.emergency_stopped = False

    @beartype
    def reset(self, *, clear_events: bool = True) -> None:
        """Reset emergency-stop state and optionally clear collisions.

        Args:
            clear_events (bool, default=True):
                If ``True``, clear recorded collision events.
        """
        self.emergency_stopped = False
        if clear_events:
            self.collision_events.clear()
