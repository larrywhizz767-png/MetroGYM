from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, TypeAlias, runtime_checkable

from beartype import beartype

from metrogym.core.coordinates import Position
from metrogym.events import CollisionEvent


class TrainVerb(str, Enum):
    PROCEED = "proceed"
    HOLD = "hold"
    REVERSE = "reverse"


class SignalVerb(str, Enum):
    AUTO = "auto"
    GRANT = "grant"
    DENY = "deny"
    LOCK_ALL = "lock_all"
    TOGGLE = "toggle"


@beartype
@dataclass(frozen=True)
class TrainDecision:
    verb: TrainVerb
    reason: str | None = None
    target_speed: float | None = None
    speed_delta: float | None = None


@beartype
@dataclass(frozen=True)
class SignalDecision:
    verb: SignalVerb
    granted_line: str | None = None
    granted_train_id: str | None = None
    reason: str | None = None


SolverAction: TypeAlias = TrainDecision | SignalDecision


@beartype
@dataclass(frozen=True)
class TrainSnapshot:
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
    tick: int
    trains: dict[str, TrainSnapshot]
    signals: dict[str, SignalSnapshot]
    signal_rules: list[SignalRuleSnapshot]
    collision_events: tuple[CollisionEvent, ...]
    emergency_stopped: bool
    focused_train_id: str | None = None
    focused_signal_id: str | None = None

    def observe_train(self, train_id: str | None = None) -> TrainObservation:
        return TrainObservation(world=self, train_id=_resolve_train_focus(self, train_id))

    def observe_signal(self, signal_id: str | None = None) -> SignalObservation:
        return SignalObservation(world=self, signal_id=_resolve_signal_focus(self, signal_id))


@beartype
@dataclass(frozen=True)
class TrainObservation:
    world: WorldView
    train_id: str

    @property
    def self(self) -> TrainSnapshot:
        return self.world.trains[self.train_id]

    @property
    def tick(self) -> int:
        return self.world.tick

    @property
    def trains(self) -> dict[str, TrainSnapshot]:
        return self.world.trains

    @property
    def all_signals(self) -> dict[str, SignalSnapshot]:
        return self.world.signals

    @property
    def collision_events(self) -> tuple[CollisionEvent, ...]:
        return self.world.collision_events

    @property
    def emergency_stopped(self) -> bool:
        return self.world.emergency_stopped

    @property
    def signals(self) -> TrainSignalView:
        return TrainSignalView(self)

    @property
    def nearby_trains(self) -> list[TrainSnapshot]:
        current_train = self.self
        return sorted(
            [other for other in self.world.trains.values() if other.id != current_train.id and other.line_name == current_train.line_name],
            key=lambda other: min(current_train.position.distance(other.position), current_train.next_position.distance(other.position)),
        )


@beartype
@dataclass(frozen=True)
class TrainSignalView:
    observation: TrainObservation

    @property
    def ahead(self) -> list[SignalRuleSnapshot]:
        current_train = self.observation.self
        return [rule for rule in self.observation.world.signal_rules if rule.line_name == current_train.line_name]

    @property
    def next(self) -> SignalRuleSnapshot | None:
        current_train = self.observation.self
        rules = self.ahead
        if not rules:
            return None
        return min(rules, key=lambda rule: distance_to_rule(current_train, rule))


@beartype
@dataclass(frozen=True)
class SignalObservation:
    world: WorldView
    signal_id: str

    @property
    def self(self) -> SignalSnapshot:
        return self.world.signals[self.signal_id]

    @property
    def tick(self) -> int:
        return self.world.tick

    @property
    def trains(self) -> dict[str, TrainSnapshot]:
        return self.world.trains

    @property
    def all_signals(self) -> dict[str, SignalSnapshot]:
        return self.world.signals

    @property
    def collision_events(self) -> tuple[CollisionEvent, ...]:
        return self.world.collision_events

    @property
    def emergency_stopped(self) -> bool:
        return self.world.emergency_stopped

    @property
    def controlled_rules(self) -> list[SignalRuleSnapshot]:
        return [rule for rule in self.world.signal_rules if rule.signal_id == self.signal_id]

    @property
    def controlled_trains(self) -> list[TrainSnapshot]:
        return self.queue.ordered()

    @property
    def queue(self) -> SignalQueueView:
        return SignalQueueView(self)


@beartype
@dataclass(frozen=True)
class SignalQueueView:
    observation: SignalObservation

    @property
    def trains(self) -> list[TrainSnapshot]:
        return self.ordered()

    @property
    def next_train(self) -> TrainSnapshot | None:
        ordered = self.ordered()
        return ordered[0] if ordered else None

    @property
    def has_conflict(self) -> bool:
        return len(self.ordered()) >= 2

    def ordered(self, *, approach_distance: float | None = None, moving_only: bool = False) -> list[TrainSnapshot]:
        rules = self.observation.controlled_rules
        controlled_lines = {rule.line_name for rule in rules}
        trains = [train for train in self.observation.world.trains.values() if train.line_name in controlled_lines]
        if moving_only:
            trains = [train for train in trains if train.position.distance(train.next_position) > 1.5]
        if approach_distance is not None:
            trains = [train for train in trains if self.distance_for(train) <= approach_distance]
        return sorted(trains, key=self.distance_for)

    def distance_for(self, train: TrainSnapshot) -> float:
        distances = [distance_to_rule(train, rule) for rule in self.observation.controlled_rules if rule.line_name == train.line_name]
        return min(distances) if distances else float("inf")


@runtime_checkable
class TrainSolver(Protocol):
    def __call__(self, observation: TrainObservation) -> TrainDecision:
        ...


@runtime_checkable
class SignalSolver(Protocol):
    def __call__(self, observation: SignalObservation) -> SignalDecision:
        ...


TrainPolicyLike: TypeAlias = TrainSolver
SignalPolicyLike: TypeAlias = SignalSolver
SolverLike: TypeAlias = TrainSolver | SignalSolver


@beartype
@dataclass
class TrainAgent:
    def reset(self) -> None:
        return None

    def observe(self, world: WorldView) -> TrainObservation:
        return world.observe_train()

    def act(self, observation: TrainObservation) -> TrainDecision:
        return train.proceed()

    def __call__(self, observation: TrainObservation) -> TrainDecision:
        return self.act(observation)


@beartype
@dataclass
class SignalAgent:
    def reset(self) -> None:
        return None

    def observe(self, world: WorldView) -> SignalObservation:
        return world.observe_signal()

    def act(self, observation: SignalObservation) -> SignalDecision:
        return signal.auto()

    def __call__(self, observation: SignalObservation) -> SignalDecision:
        return self.act(observation)


@beartype
@dataclass
class AlwaysRunSolver(TrainAgent):
    def act(self, observation: TrainObservation) -> TrainDecision:
        return train.proceed_at(observation.self.default_speed)


@beartype
@dataclass
class AlwaysStopSolver(TrainAgent):
    def act(self, observation: TrainObservation) -> TrainDecision:
        return train.hold()


@beartype
@dataclass
class PulseTrainSolver(TrainAgent):
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
    solvers: list[TrainPolicyLike] = field(default_factory=list)

    def act(self, observation: TrainObservation) -> TrainDecision:
        return _all_of_train_policies(self.solvers, observation)

    def reset(self) -> None:
        for policy in self.solvers:
            reset_solver_state(policy)


@beartype
@dataclass
class FixedSignalSolver(SignalAgent):
    green: bool

    def act(self, observation: SignalObservation) -> SignalDecision:
        return signal.grant() if self.green else signal.deny()


@beartype
@dataclass
class PulseSignalSolver(SignalAgent):
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
    policies: list[TrainPolicyLike] = field(default_factory=list)

    def act(self, observation: TrainObservation) -> TrainDecision:
        return _all_of_train_policies(self.policies, observation)

    def reset(self) -> None:
        for policy in self.policies:
            reset_solver_state(policy)


@beartype
@dataclass
class AnyOfTrainPolicies(TrainAgent):
    policies: list[TrainPolicyLike] = field(default_factory=list)

    def act(self, observation: TrainObservation) -> TrainDecision:
        return _any_of_train_policies(self.policies, observation)

    def reset(self) -> None:
        for policy in self.policies:
            reset_solver_state(policy)


@beartype
@dataclass
class PriorityQueueSignalSolver(SignalAgent):
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
    def proceed(self, reason: str | None = None, *, target_speed: float | None = None) -> TrainDecision:
        return TrainDecision(TrainVerb.PROCEED, reason=reason, target_speed=_coerce_speed(target_speed))

    def hold(self, reason: str | None = None) -> TrainDecision:
        return TrainDecision(TrainVerb.HOLD, reason=reason)

    def reverse(self, reason: str | None = None, *, target_speed: float | None = None) -> TrainDecision:
        return TrainDecision(TrainVerb.REVERSE, reason=reason, target_speed=_coerce_speed(target_speed))

    def coast(self, reason: str | None = None) -> TrainDecision:
        return self.proceed(reason=reason)

    def set_speed(self, speed: int | float, reason: str | None = None) -> TrainDecision:
        return TrainDecision(TrainVerb.PROCEED, reason=reason, target_speed=_coerce_speed(speed))

    def proceed_at(self, speed: int | float, reason: str | None = None) -> TrainDecision:
        return TrainDecision(TrainVerb.PROCEED, reason=reason, target_speed=_coerce_speed(speed))

    def reverse_at(self, speed: int | float, reason: str | None = None) -> TrainDecision:
        return TrainDecision(TrainVerb.REVERSE, reason=reason, target_speed=_coerce_speed(speed))

    def accelerate_to(self, speed: int | float, reason: str | None = None) -> TrainDecision:
        return TrainDecision(TrainVerb.PROCEED, reason=reason, target_speed=_coerce_speed(speed))

    def brake_to(self, speed: int | float, reason: str | None = None) -> TrainDecision:
        return TrainDecision(TrainVerb.PROCEED, reason=reason, target_speed=_coerce_speed(speed))

    def change_speed_by(self, delta: int | float, reason: str | None = None) -> TrainDecision:
        return TrainDecision(TrainVerb.PROCEED, reason=reason, speed_delta=float(delta))

    def speed_up(self, delta: int | float = 0.5, reason: str | None = None) -> TrainDecision:
        return self.change_speed_by(abs(float(delta)), reason=reason)

    def slow_down(self, delta: int | float = 0.5, reason: str | None = None) -> TrainDecision:
        return self.change_speed_by(-abs(float(delta)), reason=reason)

    def always_proceed(self) -> TrainAgent:
        return AlwaysRunSolver()

    def always_hold(self) -> TrainAgent:
        return AlwaysStopSolver()

    def pulse(self, *, run_ticks: int = 2, hold_ticks: int = 2) -> TrainAgent:
        return PulseTrainSolver(run_ticks=run_ticks, stop_ticks=hold_ticks)

    def respect_signals(self, *, approach_distance: float = 90.0) -> TrainAgent:
        return RedSignalStopSolver(approach_distance=approach_distance)

    def avoid_collisions(self, *, min_distance: float = 45.0) -> TrainAgent:
        return CollisionAwareSolver(min_distance=min_distance)

    def all_of(self, *policies: TrainPolicyLike) -> TrainAgent:
        return AllOfTrainPolicies(list(policies))

    def any_of(self, *policies: TrainPolicyLike) -> TrainAgent:
        return AnyOfTrainPolicies(list(policies))


@beartype
@dataclass(frozen=True)
class _SignalNamespace:
    def auto(self, reason: str | None = None) -> SignalDecision:
        return SignalDecision(SignalVerb.AUTO, reason=reason)

    def grant(
        self,
        target: TrainSnapshot | None = None,
        *,
        line: str | None = None,
        train_id: str | None = None,
        reason: str | None = None,
    ) -> SignalDecision:
        granted_train_id = train_id
        granted_line = line
        if target is not None:
            granted_train_id = target.id if train_id is None else train_id
            granted_line = target.line_name if line is None else line
        return SignalDecision(SignalVerb.GRANT, granted_line=granted_line, granted_train_id=granted_train_id, reason=reason)

    def deny(self, reason: str | None = None) -> SignalDecision:
        return SignalDecision(SignalVerb.DENY, reason=reason)

    def lock_all(self, reason: str | None = None) -> SignalDecision:
        return SignalDecision(SignalVerb.LOCK_ALL, reason=reason)

    def toggle(self, reason: str | None = None) -> SignalDecision:
        return SignalDecision(SignalVerb.TOGGLE, reason=reason)

    def always_grant(self) -> SignalAgent:
        return FixedSignalSolver(green=True)

    def always_deny(self) -> SignalAgent:
        return FixedSignalSolver(green=False)

    def pulse(self, *, green_ticks: int = 4, red_ticks: int = 4) -> SignalAgent:
        return PulseSignalSolver(green_ticks=green_ticks, red_ticks=red_ticks)

    def priority_queue(
        self,
        *,
        approach_distance: float = 75.0,
        release_distance: float = 95.0,
        red_hold_ticks: int = 3,
        priority: Callable[[TrainSnapshot, SignalObservation], object] | None = None,
    ) -> SignalAgent:
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
    if solver is None:
        return
    reset = getattr(solver, "reset", None)
    if callable(reset):
        reset()


@beartype
def distance_to_rule(current_train: TrainSnapshot, rule: SignalRuleSnapshot) -> float:
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
