from __future__ import annotations

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
