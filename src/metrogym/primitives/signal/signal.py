from __future__ import annotations

"""Public signal primitive for declarative junction control."""

from collections.abc import Iterable

from beartype import beartype

from metrogym.core.coordinates import PositionLike, to_position
from metrogym.primitives.signal.control import path_contains
from metrogym.primitives.signal.extras.control_rule import ControlRule, ControlRuleLike
from metrogym.solvers import SolverLike
from metrogym.templates.primitive import BaseMetroPrimitive
from metrogym.validation import validation_registry


@beartype
class Signal(BaseMetroPrimitive):
    """Declare a traffic signal and its protected line segments.

    Signals can run on a simple internal timer or delegate decisions to a
    signal solver. Protected segments are described with :class:`ControlRule`
    values so that trains cannot enter conflicting sections while the signal is
    red or granted elsewhere.

    Args:
        id (str):
            Unique signal identifier.
        position (PositionLike):
            World-space position of the signal head.
        controls (ControlRuleLike | Iterable[ControlRuleLike] | None, default=None):
            One rule or many rules describing protected segments.
        initial_green (bool, default=True):
            Initial runtime state before any solver acts.
        period_ticks (int, default=5):
            Timer period used when no solver is attached.
        label (str | None, default=None):
            Optional short label shown near the signal.
        solver (SolverLike | None, default=None):
            Optional signal solver or signal agent.

    Attributes:
        id (str):
            Signal identifier.
        position (PositionLike):
            Declared signal position.
        controls (ControlRuleLike | Iterable[ControlRuleLike] | None):
            Raw control-rule declaration.
        initial_green (bool):
            Initial traffic-light state.
        period_ticks (int):
            Timer period for autonomous toggling.
        label (str | None):
            Optional signal label.
        solver (SolverLike | None):
            Optional solver.

    Raises:
        ValueError:
            Raised through the validation registry when the signal id is
            duplicated, a referenced line does not exist, or a control endpoint
            does not lie on the protected line path.
    """

    primitive_group = "control"

    @beartype
    def __init__(
        self,
        id: str,
        position: PositionLike,
        *,
        controls: ControlRuleLike | Iterable[ControlRuleLike] | None = None,
        initial_green: bool = True,
        period_ticks: int = 5,
        label: str | None = None,
        solver: SolverLike | None = None,
    ):
        self.id = id
        self.position = position
        self.controls = controls
        self.initial_green = initial_green
        self.period_ticks = period_ticks
        self.label = label
        self.solver = solver

    @beartype
    def transform(self, context: object) -> object:
        """Create the runtime signal and protect its configured segments.

        Args:
            context (object):
                Build context receiving runtime objects.

        Returns:
            object:
                Updated build context.
        """
        registry = validation_registry()
        if self.id in context.signal_ids:
            registry.raise_issue(registry.primitive_issue("Signal", "duplicate_id", path=f"Signal[id={self.id}]", id=self.id))
        signal = context.simulator.add_traffic_light(
            self.id,
            self.position,
            initial_green=self.initial_green,
            period_ticks=self.period_ticks,
            label=self.label,
            solver=self.solver,
        )
        context.signal_ids.add(self.id)
        for rule in self._normalised_controls():
            if rule.line not in context.line_names:
                registry.raise_issue(registry.cross_object_issue("signal_controls_known_line", path=f"Signal[id={self.id}].controls", id=self.id, line=rule.line))
            line = context.simulator.line(rule.line)
            start = to_position(rule.start)
            end = to_position(rule.end)
            if not path_contains(line.path, start) or not path_contains(line.path, end):
                registry.raise_issue(registry.cross_object_issue("signal_controls_on_path", path=f"Signal[id={self.id}].controls", id=self.id, line=rule.line))
            context.simulator.protect_segment(rule.line, rule.start, rule.end, signal, direction=rule.direction)
        return context

    def _normalised_controls(self) -> list[ControlRule]:
        if self.controls is None:
            return []
        if isinstance(self.controls, ControlRule) or _is_control_tuple(self.controls):
            values = [self.controls]
        else:
            values = list(self.controls)
        return [_to_rule(value) for value in values]


def _to_rule(value: ControlRuleLike) -> ControlRule:
    if isinstance(value, ControlRule):
        return value
    if len(value) == 3:
        line, start, end = value
        return ControlRule(line, start, end)
    line, start, end, direction = value
    return ControlRule(line, start, end, direction)


def _is_control_tuple(value: object) -> bool:
    return isinstance(value, tuple) and len(value) in {3, 4} and isinstance(value[0], str)
