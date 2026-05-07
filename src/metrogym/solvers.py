from __future__ import annotations

"""Public solver protocols, observations, and decision helpers.

This module defines MetroGYM's agent-facing API. Train and signal solvers do
not mutate runtime objects directly; instead, they inspect immutable world
snapshots and return typed decisions describing the next action to take.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, TypeAlias, runtime_checkable

from beartype import beartype

from metrogym.core.coordinates import Position
from metrogym.events import CollisionEvent


class TrainVerb(str, Enum):
    """Enumerate train actions understood by the runtime engine."""

    PROCEED = "proceed"
    HOLD = "hold"
    REVERSE = "reverse"


class SignalVerb(str, Enum):
    """Enumerate signal actions understood by the runtime engine."""

    AUTO = "auto"
    GRANT = "grant"
    DENY = "deny"
    LOCK_ALL = "lock_all"
    TOGGLE = "toggle"


@beartype
@dataclass(frozen=True)
class TrainDecision:
    """Describe the next action requested by a train solver.

    Args:
        verb (TrainVerb):
            Requested train action.
        reason (str | None, default=None):
            Optional human-readable explanation for logs or teaching output.
        target_speed (float | None, default=None):
            Optional target speed to ease toward.
        speed_delta (float | None, default=None):
            Optional relative speed adjustment.
    """

    verb: TrainVerb
    reason: str | None = None
    target_speed: float | None = None
    speed_delta: float | None = None


@beartype
@dataclass(frozen=True)
class SignalDecision:
    """Describe the next action requested by a signal solver.

    Args:
        verb (SignalVerb):
            Requested signal action.
        granted_line (str | None, default=None):
            Optional line currently granted through the signal.
        granted_train_id (str | None, default=None):
            Optional train currently granted through the signal.
        reason (str | None, default=None):
            Optional human-readable explanation for logs or teaching output.
    """

    verb: SignalVerb
    granted_line: str | None = None
    granted_train_id: str | None = None
    reason: str | None = None


SolverAction: TypeAlias = TrainDecision | SignalDecision


@beartype
@dataclass(frozen=True)
class TrainSnapshot:
    """Immutable runtime view of one train.

    Args:
        id (str):
            Train identifier.
        line_name (str):
            Name of the line the train belongs to.
        position (Position):
            Current train position.
        next_position (Position):
            Next path position if the train advances.
        stopped (bool):
            Whether the runtime currently considers the train stopped.
        wait_ticks (int):
            Number of ticks remaining in a forced wait.
        speed (float):
            Current speed.
        target_speed (float):
            Current target speed.
        default_speed (float):
            Baseline cruising speed.
        acceleration (float):
            Per-tick acceleration cap.
        deceleration (float):
            Per-tick deceleration cap.
        collision_count (int):
            Number of collisions recorded on this train so far.
    """

    id: str
    line_name: str
    position: Position
    next_position: Position
    stopped: bool
    wait_ticks: int
    speed: float
    target_speed: float
    default_speed: float
    acceleration: float
    deceleration: float
    collision_count: int


@beartype
@dataclass(frozen=True)
class SignalSnapshot:
    """Immutable runtime view of one signal.

    Args:
        id (str):
            Signal identifier.
        position (Position):
            Signal position.
        green (bool):
            Whether the light is currently green.
        granted_line (str | None):
            Line explicitly granted through the signal, if any.
        granted_train_id (str | None):
            Train explicitly granted through the signal, if any.
        period_ticks (int):
            Autonomous toggle period.
        ticks_since_change (int):
            Number of ticks since the last state change.
        label (str | None, default=None):
            Optional display label.
    """

    id: str
    position: Position
    green: bool
    granted_line: str | None
    granted_train_id: str | None
    period_ticks: int
    ticks_since_change: int
    label: str | None = None


@beartype
@dataclass(frozen=True)
class SignalRuleSnapshot:
    """Immutable view of one protected signal rule.

    Args:
        line_name (str):
            Protected line name.
        start (Position):
            First endpoint of the protected segment.
        end (Position):
            Second endpoint of the protected segment.
        signal_id (str):
            Controlling signal identifier.
        signal_green (bool):
            Whether the controlling signal is green.
        signal_granted_line (str | None):
            Line granted through the signal, if any.
        signal_granted_train_id (str | None):
            Train granted through the signal, if any.
        direction (str):
            Protected direction label.
    """

    line_name: str
    start: Position
    end: Position
    signal_id: str
    signal_green: bool
    signal_granted_line: str | None
    signal_granted_train_id: str | None
    direction: str


@beartype
@dataclass(frozen=True)
class WorldView:
    """Immutable snapshot of the whole observable world.

    World views are the entry point for custom agent logic. They contain all
    public runtime facts exposed to train and signal solvers at one tick.

    Args:
        tick (int):
            Current world tick.
        trains (dict[str, TrainSnapshot]):
            Train snapshots keyed by train id.
        signals (dict[str, SignalSnapshot]):
            Signal snapshots keyed by signal id.
        signal_rules (list[SignalRuleSnapshot]):
            Protected signal-rule snapshots.
        collision_events (tuple[CollisionEvent, ...]):
            Collision events recorded so far.
        emergency_stopped (bool):
            Whether the control system is emergency-stopped.
        focused_train_id (str | None, default=None):
            Default train focus for train observations.
        focused_signal_id (str | None, default=None):
            Default signal focus for signal observations.
    """

    tick: int
    trains: dict[str, TrainSnapshot]
    signals: dict[str, SignalSnapshot]
    signal_rules: list[SignalRuleSnapshot]
    collision_events: tuple[CollisionEvent, ...]
    emergency_stopped: bool
    focused_train_id: str | None = None
    focused_signal_id: str | None = None

    def observe_train(self, train_id: str | None = None) -> TrainObservation:
        """Create a train-centric observation from the world snapshot.

        Args:
            train_id (str | None, default=None):
                Train identifier to focus. If omitted, use the focused train id
                stored on the world view.

        Returns:
            TrainObservation:
                Train-centric observation wrapper.
        """
        return TrainObservation(world=self, train_id=_resolve_train_focus(self, train_id))

    def observe_signal(self, signal_id: str | None = None) -> SignalObservation:
        """Create a signal-centric observation from the world snapshot.

        Args:
            signal_id (str | None, default=None):
                Signal identifier to focus. If omitted, use the focused signal id
                stored on the world view.

        Returns:
            SignalObservation:
                Signal-centric observation wrapper.
        """
        return SignalObservation(world=self, signal_id=_resolve_signal_focus(self, signal_id))


@beartype
@dataclass(frozen=True)
class TrainObservation:
    """Train-focused view over a :class:`WorldView` snapshot.

    Args:
        world (WorldView):
            Source world snapshot.
        train_id (str):
            Focused train identifier.
    """

    world: WorldView
    train_id: str

    @property
    def self(self) -> TrainSnapshot:
        """Return the focused train snapshot."""
        return self.world.trains[self.train_id]

    @property
    def tick(self) -> int:
        """Return the current world tick."""
        return self.world.tick

    @property
    def trains(self) -> dict[str, TrainSnapshot]:
        """Return all train snapshots in the world."""
        return self.world.trains

    @property
    def all_signals(self) -> dict[str, SignalSnapshot]:
        """Return all signal snapshots in the world."""
        return self.world.signals

    @property
    def collision_events(self) -> tuple[CollisionEvent, ...]:
        """Return all recorded collision events."""
        return self.world.collision_events

    @property
    def emergency_stopped(self) -> bool:
        """Return whether the world is emergency-stopped."""
        return self.world.emergency_stopped

    @property
    def signals(self) -> TrainSignalView:
        """Return signal-oriented helpers for the focused train."""
        return TrainSignalView(self)

    @property
    def nearby_trains(self) -> list[TrainSnapshot]:
        """Return same-line peer trains ordered by proximity.

        Returns:
            list[TrainSnapshot]:
                Same-line trains sorted by their distance to the focused train.
        """
        current_train = self.self
        return sorted(
            [other for other in self.world.trains.values() if other.id != current_train.id and other.line_name == current_train.line_name],
            key=lambda other: min(current_train.position.distance(other.position), current_train.next_position.distance(other.position)),
        )


@beartype
@dataclass(frozen=True)
class TrainSignalView:
    """Convenience accessors for signals relevant to one train."""

    observation: TrainObservation

    @property
    def ahead(self) -> list[SignalRuleSnapshot]:
        """Return all signal rules on the focused train's line."""
        current_train = self.observation.self
        return [rule for rule in self.observation.world.signal_rules if rule.line_name == current_train.line_name]

    @property
    def next(self) -> SignalRuleSnapshot | None:
        """Return the nearest upcoming signal rule on the train's line."""
        current_train = self.observation.self
        rules = self.ahead
        if not rules:
            return None
        return min(rules, key=lambda rule: distance_to_rule(current_train, rule))


@beartype
@dataclass(frozen=True)
class SignalObservation:
    """Signal-focused view over a :class:`WorldView` snapshot.

    Args:
        world (WorldView):
            Source world snapshot.
        signal_id (str):
            Focused signal identifier.
    """

    world: WorldView
    signal_id: str

    @property
    def self(self) -> SignalSnapshot:
        """Return the focused signal snapshot."""
        return self.world.signals[self.signal_id]

    @property
    def tick(self) -> int:
        """Return the current world tick."""
        return self.world.tick

    @property
    def trains(self) -> dict[str, TrainSnapshot]:
        """Return all train snapshots in the world."""
        return self.world.trains

    @property
    def all_signals(self) -> dict[str, SignalSnapshot]:
        """Return all signal snapshots in the world."""
        return self.world.signals

    @property
    def collision_events(self) -> tuple[CollisionEvent, ...]:
        """Return all recorded collision events."""
        return self.world.collision_events

    @property
    def emergency_stopped(self) -> bool:
        """Return whether the world is emergency-stopped."""
        return self.world.emergency_stopped

    @property
    def controlled_rules(self) -> list[SignalRuleSnapshot]:
        """Return rules controlled by the focused signal."""
        return [rule for rule in self.world.signal_rules if rule.signal_id == self.signal_id]

    @property
    def controlled_trains(self) -> list[TrainSnapshot]:
        """Return approaching trains ordered by queue priority."""
        return self.queue.ordered()

    @property
    def queue(self) -> SignalQueueView:
        """Return queue-oriented helpers for the focused signal."""
        return SignalQueueView(self)


@beartype
@dataclass(frozen=True)
class SignalQueueView:
    """Queue helpers for signals that arbitrate between approaching trains."""

    observation: SignalObservation

    @property
    def trains(self) -> list[TrainSnapshot]:
        """Return trains ordered by queue priority."""
        return self.ordered()

    @property
    def next_train(self) -> TrainSnapshot | None:
        """Return the next train in the queue, if any."""
        ordered = self.ordered()
        return ordered[0] if ordered else None

    @property
    def has_conflict(self) -> bool:
        """Return whether multiple trains are competing for the signal."""
        return len(self.ordered()) >= 2

    def ordered(self, *, approach_distance: float | None = None, moving_only: bool = False) -> list[TrainSnapshot]:
        """Return controlled trains ordered by distance to the signal.

        Args:
            approach_distance (float | None, default=None):
                Optional maximum distance to include.
            moving_only (bool, default=False):
                If ``True``, include only trains that are currently moving.

        Returns:
            list[TrainSnapshot]:
                Ordered queue of controlled trains.
        """
        rules = self.observation.controlled_rules
        controlled_lines = {rule.line_name for rule in rules}
        trains = [train for train in self.observation.world.trains.values() if train.line_name in controlled_lines]
        if moving_only:
            trains = [train for train in trains if train.position.distance(train.next_position) > 1.5]
        if approach_distance is not None:
            trains = [train for train in trains if self.distance_for(train) <= approach_distance]
        return sorted(trains, key=self.distance_for)

    def distance_for(self, train: TrainSnapshot) -> float:
        """Measure a train's distance to the controlled segment.

        Args:
            train (TrainSnapshot):
                Train to measure.

        Returns:
            float:
                Minimum distance from the train to any controlled rule on its
                line, or ``inf`` when no rule applies.
        """
        distances = [distance_to_rule(train, rule) for rule in self.observation.controlled_rules if rule.line_name == train.line_name]
        return min(distances) if distances else float("inf")


@runtime_checkable
class TrainSolver(Protocol):
    """Protocol implemented by callables that return train decisions."""

    def __call__(self, observation: TrainObservation) -> TrainDecision:
        ...


@runtime_checkable
class SignalSolver(Protocol):
    """Protocol implemented by callables that return signal decisions."""

    def __call__(self, observation: SignalObservation) -> SignalDecision:
        ...


TrainPolicyLike: TypeAlias = TrainSolver
SignalPolicyLike: TypeAlias = SignalSolver
SolverLike: TypeAlias = TrainSolver | SignalSolver


@beartype
@dataclass
class TrainAgent:
    """Base class for custom train agents.

    Subclass :class:`TrainAgent` and override :meth:`act` to build reusable
    teaching agents that can inspect typed observations and return typed
    decisions.
    """

    def reset(self) -> None:
        """Reset any internal agent state."""
        return None

    def observe(self, world: WorldView) -> TrainObservation:
        """Create a train observation from a world snapshot.

        Args:
            world (WorldView):
                World snapshot to inspect.

        Returns:
            TrainObservation:
                Train-centric observation.
        """
        return world.observe_train()

    def act(self, observation: TrainObservation) -> TrainDecision:
        """Compute the next train action.

        Args:
            observation (TrainObservation):
                Train-centric world observation.

        Returns:
            TrainDecision:
                Decision to apply for the next tick.
        """
        return train.proceed()

    def __call__(self, observation: TrainObservation) -> TrainDecision:
        """Delegate callable use to :meth:`act`."""
        return self.act(observation)


@beartype
@dataclass
class SignalAgent:
    """Base class for custom signal agents."""

    def reset(self) -> None:
        """Reset any internal agent state."""
        return None

    def observe(self, world: WorldView) -> SignalObservation:
        """Create a signal observation from a world snapshot."""
        return world.observe_signal()

    def act(self, observation: SignalObservation) -> SignalDecision:
        """Compute the next signal action."""
        return signal.auto()

    def __call__(self, observation: SignalObservation) -> SignalDecision:
        """Delegate callable use to :meth:`act`."""
        return self.act(observation)


@beartype
@dataclass
class AlwaysRunSolver(TrainAgent):
    """Train agent that always proceeds at default speed."""

    def act(self, observation: TrainObservation) -> TrainDecision:
        return train.proceed_at(observation.self.default_speed)


@beartype
@dataclass
class AlwaysStopSolver(TrainAgent):
    """Train agent that always holds position."""

    def act(self, observation: TrainObservation) -> TrainDecision:
        return train.hold()


@beartype
@dataclass
class PulseTrainSolver(TrainAgent):
    """Train agent that alternates between running and holding.

    Args:
        run_ticks (int, default=2):
            Number of ticks spent running.
        stop_ticks (int, default=2):
            Number of ticks spent holding.
    """

    run_ticks: int = 2
    stop_ticks: int = 2

    def act(self, observation: TrainObservation) -> TrainDecision:
        cycle = max(1, self.run_ticks + self.stop_ticks)
        if observation.tick % cycle < self.run_ticks:
            return train.proceed_at(observation.self.default_speed)
        return train.hold()


@beartype
@dataclass
class RedSignalStopSolver(TrainAgent):
    """Train agent that stops when a red signal is close ahead.

    Args:
        approach_distance (float, default=90.0):
            Distance threshold used to consider an upcoming signal.
    """

    approach_distance: float = 90.0

    def act(self, observation: TrainObservation) -> TrainDecision:
        current_train = observation.self
        for rule in observation.signals.ahead:
            if distance_to_rule(current_train, rule) > self.approach_distance:
                continue
            if not rule.signal_green:
                return train.hold(reason="red signal ahead")
            if rule.signal_granted_train_id is not None and rule.signal_granted_train_id != current_train.id:
                return train.hold(reason="signal granted to another train")
            if rule.signal_granted_line is not None and rule.signal_granted_line != current_train.line_name:
                return train.hold(reason="signal granted to another line")
        return train.proceed_at(current_train.default_speed)


@beartype
@dataclass
class CollisionAwareSolver(TrainAgent):
    """Train agent that keeps a minimum gap to same-line peers.

    Args:
        min_distance (float, default=45.0):
            Minimum allowed distance to a peer train.
    """

    min_distance: float = 45.0

    def act(self, observation: TrainObservation) -> TrainDecision:
        current_train = observation.self
        for other in observation.nearby_trains:
            if current_train.position.distance(other.position) < self.min_distance:
                return train.hold(reason=f"too close to {other.id}")
            if current_train.next_position.distance(other.position) < self.min_distance:
                return train.hold(reason=f"would close gap with {other.id}")
        return train.proceed_at(current_train.default_speed)


@beartype
@dataclass
class CompositeTrainSolver(TrainAgent):
    """Train agent that combines several train policies with all-of logic.

    Args:
        solvers (list[TrainPolicyLike], default_factory=list):
            Policies evaluated together.
    """

    solvers: list[TrainPolicyLike] = field(default_factory=list)

    def act(self, observation: TrainObservation) -> TrainDecision:
        return _all_of_train_policies(self.solvers, observation)

    def reset(self) -> None:
        for policy in self.solvers:
            reset_solver_state(policy)


@beartype
@dataclass
class FixedSignalSolver(SignalAgent):
    """Signal agent that stays permanently green or permanently red.

    Args:
        green (bool):
            Whether the signal should always grant passage.
    """

    green: bool

    def act(self, observation: SignalObservation) -> SignalDecision:
        return signal.grant() if self.green else signal.deny()


@beartype
@dataclass
class PulseSignalSolver(SignalAgent):
    """Signal agent that alternates between green and red phases.

    Args:
        green_ticks (int, default=4):
            Number of green ticks per cycle.
        red_ticks (int, default=4):
            Number of red ticks per cycle.
    """

    green_ticks: int = 4
    red_ticks: int = 4

    def act(self, observation: SignalObservation) -> SignalDecision:
        cycle = max(1, self.green_ticks + self.red_ticks)
        if observation.tick % cycle < self.green_ticks:
            return signal.grant()
        return signal.deny()


@beartype
@dataclass
class AllOfTrainPolicies(TrainAgent):
    """Train agent that requires all child policies to allow movement.

    Args:
        policies (list[TrainPolicyLike], default_factory=list):
            Policies combined with all-of semantics.
    """

    policies: list[TrainPolicyLike] = field(default_factory=list)

    def act(self, observation: TrainObservation) -> TrainDecision:
        return _all_of_train_policies(self.policies, observation)

    def reset(self) -> None:
        for policy in self.policies:
            reset_solver_state(policy)


@beartype
@dataclass
class AnyOfTrainPolicies(TrainAgent):
    """Train agent that proceeds if any child policy allows it.

    Args:
        policies (list[TrainPolicyLike], default_factory=list):
            Policies combined with any-of semantics.
    """

    policies: list[TrainPolicyLike] = field(default_factory=list)

    def act(self, observation: TrainObservation) -> TrainDecision:
        return _any_of_train_policies(self.policies, observation)

    def reset(self) -> None:
        for policy in self.policies:
            reset_solver_state(policy)


@beartype
@dataclass
class PriorityQueueSignalSolver(SignalAgent):
    """Signal agent that queues approaching trains through one conflict zone.

    Args:
        approach_distance (float, default=75.0):
            Maximum distance for a train to join the queue.
        release_distance (float, default=95.0):
            Distance after which the active train releases the grant.
        red_hold_ticks (int, default=3):
            Number of all-red ticks used to clear the junction.
        priority (Callable[[TrainSnapshot, SignalObservation], object] | None, default=None):
            Optional sorting key for queued trains.
        queue (list[str], default_factory=list):
            Internal queued train ids.
        active_train_id (str | None, default=None):
            Currently granted train id.
        phase (str, default="open"):
            Internal queue-management phase.
        red_since (int, default=0):
            Tick when the all-red phase started.
    """

    approach_distance: float = 75.0
    release_distance: float = 95.0
    red_hold_ticks: int = 3
    priority: Callable[[TrainSnapshot, SignalObservation], object] | None = None
    queue: list[str] = field(default_factory=list)
    active_train_id: str | None = None
    phase: str = "open"
    red_since: int = 0

    def reset(self) -> None:
        self.queue.clear()
        self.active_train_id = None
        self.phase = "open"
        self.red_since = 0

    def act(self, observation: SignalObservation) -> SignalDecision:
        approaching = self._approaching_trains(observation)
        for next_train in approaching:
            if next_train.id != self.active_train_id and next_train.id not in self.queue:
                self.queue.append(next_train.id)
        if self.active_train_id is not None:
            active_train = observation.trains[self.active_train_id]
            if observation.queue.distance_for(active_train) > self.release_distance:
                self.active_train_id = None
                self.phase = "open"
        if self.phase == "open" and len(approaching) >= 2:
            active_ids = {next_train.id for next_train in approaching}
            self.queue = [train_id for train_id in self.queue if train_id in active_ids]
            self.phase = "all_red"
            self.red_since = observation.tick
            return signal.lock_all(reason="multiple trains approaching junction")
        if self.phase == "all_red":
            if observation.tick - self.red_since < self.red_hold_ticks:
                return signal.lock_all(reason="clearing junction")
            if self.active_train_id is None and self.queue:
                self.active_train_id = self.queue.pop(0)
            self.phase = "grant"
        if self.phase == "grant" and self.active_train_id is not None:
            return signal.grant(train_id=self.active_train_id)
        return signal.grant()

    def _approaching_trains(self, observation: SignalObservation) -> list[TrainSnapshot]:
        trains = observation.queue.ordered(approach_distance=self.approach_distance, moving_only=True)
        if self.priority is None:
            return trains
        return sorted(trains, key=lambda next_train: self.priority(next_train, observation))


@beartype
@dataclass(frozen=True)
class _TrainNamespace:
    """Convenience namespace for constructing train decisions and policies."""

    def proceed(self, reason: str | None = None, *, target_speed: float | None = None) -> TrainDecision:
        """Request that the train proceeds.

        Args:
            reason (str | None, default=None):
                Optional explanatory label.
            target_speed (float | None, default=None):
                Optional target speed.

        Returns:
            TrainDecision:
                Proceed decision.
        """
        return TrainDecision(TrainVerb.PROCEED, reason=reason, target_speed=_coerce_speed(target_speed))

    def hold(self, reason: str | None = None) -> TrainDecision:
        """Request that the train holds position."""
        return TrainDecision(TrainVerb.HOLD, reason=reason)

    def reverse(self, reason: str | None = None, *, target_speed: float | None = None) -> TrainDecision:
        """Request that the train reverses direction."""
        return TrainDecision(TrainVerb.REVERSE, reason=reason, target_speed=_coerce_speed(target_speed))

    def coast(self, reason: str | None = None) -> TrainDecision:
        """Alias for :meth:`proceed`."""
        return self.proceed(reason=reason)

    def set_speed(self, speed: int | float, reason: str | None = None) -> TrainDecision:
        """Proceed while easing toward an explicit target speed."""
        return TrainDecision(TrainVerb.PROCEED, reason=reason, target_speed=_coerce_speed(speed))

    def proceed_at(self, speed: int | float, reason: str | None = None) -> TrainDecision:
        """Proceed while easing toward the given speed."""
        return TrainDecision(TrainVerb.PROCEED, reason=reason, target_speed=_coerce_speed(speed))

    def reverse_at(self, speed: int | float, reason: str | None = None) -> TrainDecision:
        """Reverse while easing toward the given speed."""
        return TrainDecision(TrainVerb.REVERSE, reason=reason, target_speed=_coerce_speed(speed))

    def accelerate_to(self, speed: int | float, reason: str | None = None) -> TrainDecision:
        """Proceed while accelerating toward a target speed."""
        return TrainDecision(TrainVerb.PROCEED, reason=reason, target_speed=_coerce_speed(speed))

    def brake_to(self, speed: int | float, reason: str | None = None) -> TrainDecision:
        """Proceed while braking toward a lower speed."""
        return TrainDecision(TrainVerb.PROCEED, reason=reason, target_speed=_coerce_speed(speed))

    def change_speed_by(self, delta: int | float, reason: str | None = None) -> TrainDecision:
        """Proceed while adjusting target speed by a signed delta."""
        return TrainDecision(TrainVerb.PROCEED, reason=reason, speed_delta=float(delta))

    def speed_up(self, delta: int | float = 0.5, reason: str | None = None) -> TrainDecision:
        """Increase target speed by a positive delta."""
        return self.change_speed_by(abs(float(delta)), reason=reason)

    def slow_down(self, delta: int | float = 0.5, reason: str | None = None) -> TrainDecision:
        """Decrease target speed by a positive delta."""
        return self.change_speed_by(-abs(float(delta)), reason=reason)

    def always_proceed(self) -> TrainAgent:
        """Return a train agent that always proceeds."""
        return AlwaysRunSolver()

    def always_hold(self) -> TrainAgent:
        """Return a train agent that always holds."""
        return AlwaysStopSolver()

    def pulse(self, *, run_ticks: int = 2, hold_ticks: int = 2) -> TrainAgent:
        """Return a pulsing run-hold train agent."""
        return PulseTrainSolver(run_ticks=run_ticks, stop_ticks=hold_ticks)

    def respect_signals(self, *, approach_distance: float = 90.0) -> TrainAgent:
        """Return a train agent that respects upcoming signals."""
        return RedSignalStopSolver(approach_distance=approach_distance)

    def avoid_collisions(self, *, min_distance: float = 45.0) -> TrainAgent:
        """Return a train agent that keeps space to same-line peers."""
        return CollisionAwareSolver(min_distance=min_distance)

    def all_of(self, *policies: TrainPolicyLike) -> TrainAgent:
        """Combine train policies with all-of semantics."""
        return AllOfTrainPolicies(list(policies))

    def any_of(self, *policies: TrainPolicyLike) -> TrainAgent:
        """Combine train policies with any-of semantics."""
        return AnyOfTrainPolicies(list(policies))


@beartype
@dataclass(frozen=True)
class _SignalNamespace:
    """Convenience namespace for constructing signal decisions and policies."""

    def auto(self, reason: str | None = None) -> SignalDecision:
        """Delegate to the signal's built-in autonomous behaviour."""
        return SignalDecision(SignalVerb.AUTO, reason=reason)

    def grant(
        self,
        target: TrainSnapshot | None = None,
        *,
        line: str | None = None,
        train_id: str | None = None,
        reason: str | None = None,
    ) -> SignalDecision:
        """Grant passage to a line or train.

        Args:
            target (TrainSnapshot | None, default=None):
                Optional train snapshot used to infer the line and train id.
            line (str | None, default=None):
                Explicit line to grant.
            train_id (str | None, default=None):
                Explicit train id to grant.
            reason (str | None, default=None):
                Optional explanatory label.

        Returns:
            SignalDecision:
                Grant decision.
        """
        granted_train_id = train_id
        granted_line = line
        if target is not None:
            granted_train_id = target.id if train_id is None else train_id
            granted_line = target.line_name if line is None else line
        return SignalDecision(SignalVerb.GRANT, granted_line=granted_line, granted_train_id=granted_train_id, reason=reason)

    def deny(self, reason: str | None = None) -> SignalDecision:
        """Force the signal to red."""
        return SignalDecision(SignalVerb.DENY, reason=reason)

    def lock_all(self, reason: str | None = None) -> SignalDecision:
        """Force the signal to deny all trains temporarily."""
        return SignalDecision(SignalVerb.LOCK_ALL, reason=reason)

    def toggle(self, reason: str | None = None) -> SignalDecision:
        """Toggle the current light state."""
        return SignalDecision(SignalVerb.TOGGLE, reason=reason)

    def always_grant(self) -> SignalAgent:
        """Return a signal agent that always grants passage."""
        return FixedSignalSolver(green=True)

    def always_deny(self) -> SignalAgent:
        """Return a signal agent that always denies passage."""
        return FixedSignalSolver(green=False)

    def pulse(self, *, green_ticks: int = 4, red_ticks: int = 4) -> SignalAgent:
        """Return a pulsing green-red signal agent."""
        return PulseSignalSolver(green_ticks=green_ticks, red_ticks=red_ticks)

    def priority_queue(
        self,
        *,
        approach_distance: float = 75.0,
        release_distance: float = 95.0,
        red_hold_ticks: int = 3,
        priority: Callable[[TrainSnapshot, SignalObservation], object] | None = None,
    ) -> SignalAgent:
        """Return a queued-junction signal agent."""
        return PriorityQueueSignalSolver(
            approach_distance=approach_distance,
            release_distance=release_distance,
            red_hold_ticks=red_hold_ticks,
            priority=priority,
        )


train = _TrainNamespace()
signal = _SignalNamespace()


@beartype
def reset_solver_state(solver: object | None) -> None:
    """Reset a solver if it exposes a callable ``reset`` method.

    Args:
        solver (object | None):
            Solver or agent to reset.
    """
    if solver is None:
        return
    reset = getattr(solver, "reset", None)
    if callable(reset):
        reset()


@beartype
def distance_to_rule(current_train: TrainSnapshot, rule: SignalRuleSnapshot) -> float:
    """Measure a train's distance to a protected rule segment.

    Args:
        current_train (TrainSnapshot):
            Train being measured.
        rule (SignalRuleSnapshot):
            Signal rule to measure against.

    Returns:
        float:
            Minimum distance from the train's current or next position to the
            protected rule endpoints.
    """
    return min(
        current_train.position.distance(rule.start),
        current_train.next_position.distance(rule.start),
        current_train.position.distance(rule.end),
        current_train.next_position.distance(rule.end),
    )


@beartype
def _coerce_speed(speed: int | float | None) -> float | None:
    if speed is None:
        return None
    return max(0.0, float(speed))


def _resolve_train_focus(world: WorldView, train_id: str | None = None) -> str:
    if train_id is not None:
        return train_id
    if world.focused_train_id is not None:
        return world.focused_train_id
    if len(world.trains) == 1:
        return next(iter(world.trains))
    raise ValueError("Train observation requires a focused train_id when multiple trains are present.")


def _resolve_signal_focus(world: WorldView, signal_id: str | None = None) -> str:
    if signal_id is not None:
        return signal_id
    if world.focused_signal_id is not None:
        return world.focused_signal_id
    if len(world.signals) == 1:
        return next(iter(world.signals))
    raise ValueError("Signal observation requires a focused signal_id when multiple signals are present.")


def _all_of_train_policies(policies: list[TrainPolicyLike], observation: TrainObservation) -> TrainDecision:
    saw_reverse = False
    target_speed: float | None = None
    speed_delta = 0.0
    has_speed_delta = False
    for policy in policies:
        decision = policy(observation)
        if decision.verb == TrainVerb.HOLD:
            return decision
        if decision.verb == TrainVerb.REVERSE:
            saw_reverse = True
        if decision.target_speed is not None:
            target_speed = decision.target_speed
        if decision.speed_delta is not None:
            speed_delta += decision.speed_delta
            has_speed_delta = True
    return TrainDecision(
        TrainVerb.REVERSE if saw_reverse else TrainVerb.PROCEED,
        target_speed=target_speed,
        speed_delta=speed_delta if has_speed_delta else None,
    )


def _any_of_train_policies(policies: list[TrainPolicyLike], observation: TrainObservation) -> TrainDecision:
    saw_reverse = False
    for policy in policies:
        decision = policy(observation)
        if decision.verb == TrainVerb.PROCEED:
            return decision
        if decision.verb == TrainVerb.REVERSE:
            saw_reverse = True
    if saw_reverse:
        return train.reverse()
    return train.hold()
