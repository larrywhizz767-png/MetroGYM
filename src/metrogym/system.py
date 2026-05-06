from __future__ import annotations

from collections.abc import Iterable

from beartype import beartype

from metrogym.context import MetroContext
from metrogym.core.constants import DEFAULT_PRIMITIVE_GROUP_ORDER, PRIMITIVE_GROUP_ORDER
from metrogym.core.coordinates import PositionLike
from metrogym.primitives import Line, Network, Station
from metrogym.rendering.primitives import MetroGYMRenderer
from metrogym.runtimes import RuntimeSimulator
from metrogym.templates.primitive import BaseMetroPrimitive
from metrogym.validation import validation_registry


@beartype
class MetroSystem:
    @beartype
    def __init__(
        self,
        name: str = "Metro Gymulation",
        *,
        tick_ms: int = 500,
        size: PositionLike = (700, 520),
        verbose: bool = False,
        stop_all_on_collision: bool = False,
        render_scale: int | float = 2.0,
    ):
        self.name = name
        self.tick_ms = tick_ms
        self.size = size
        self.verbose = verbose
        self.stop_all_on_collision = stop_all_on_collision
        self.render_scale = render_scale
        self.steps: list[tuple[str, BaseMetroPrimitive]] = []
        self.context: MetroContext | None = None
        self.simulator: RuntimeSimulator | None = None

    @beartype
    def pipeline(self, steps: Iterable[BaseMetroPrimitive | tuple[str, BaseMetroPrimitive]]) -> "MetroSystem":
        self.steps = []
        for index, step in enumerate(steps):
            if isinstance(step, tuple):
                name, primitive = step
            else:
                primitive = step
                name = _default_step_name(primitive, index)
            self.steps.append((name, primitive))
        return self

    def fit(self) -> "MetroSystem":
        self._validate_pipeline_shape()
        render_scale = self._resolved_render_scale()
        simulator = RuntimeSimulator(
            title=self.name,
            tick_ms=self.tick_ms,
            size=self.size,
            verbose=self.verbose,
            stop_all_on_collision=self.stop_all_on_collision,
            render_scale=render_scale,
        )
        context = MetroContext(simulator=simulator)
        for _name, primitive in self._ordered_steps():
            primitive.fit_transform(context)
        self._validate(context)
        self._auto_link_peers(context)
        self.context = context
        self.simulator = simulator
        return self

    @beartype
    def run(self, *, block: bool = True) -> None:
        if self.simulator is None:
            self.fit()
        self.simulator.show(block=block)

    @beartype
    def step(self, n: int = 1) -> "MetroSystem":
        if self.simulator is None:
            self.fit()
        for _ in range(max(0, n)):
            self.simulator.tick()
        return self

    def reset(self) -> "MetroSystem":
        if self.simulator is None:
            self.fit()
        self.simulator.reset()
        return self

    @beartype
    def get_params(self, deep: bool = True) -> dict[str, object]:
        params: dict[str, object] = {
            "name": self.name,
            "tick_ms": self.tick_ms,
            "size": self.size,
            "verbose": self.verbose,
            "stop_all_on_collision": self.stop_all_on_collision,
            "render_scale": self.render_scale,
        }
        if deep:
            for name, primitive in self.steps:
                params[name] = primitive
                for key, value in primitive.get_params(deep=True).items():
                    params[f"{name}__{key}"] = value
        return params

    @beartype
    def set_params(self, **params: object) -> "MetroSystem":
        registry = validation_registry()
        step_map = dict(self.steps)
        for key, value in params.items():
            if "__" in key:
                step_name, param_name = key.split("__", 1)
                if step_name not in step_map:
                    registry.raise_issue(registry.system_issue("unknown_pipeline_step", path=f"MetroSystem.steps[{step_name}]", step_name=step_name))
                step_map[step_name].set_params(**{param_name: value})
            elif hasattr(self, key):
                setattr(self, key, value)
            else:
                registry.raise_issue(registry.system_issue("invalid_system_param", path=f"MetroSystem.{key}", param=key))
        return self

    def _ordered_steps(self) -> list[tuple[str, BaseMetroPrimitive]]:
        return sorted(
            self.steps,
            key=lambda item: PRIMITIVE_GROUP_ORDER.get(item[1].primitive_group, DEFAULT_PRIMITIVE_GROUP_ORDER),
        )

    def _resolved_render_scale(self) -> float:
        scale = self.render_scale
        for _name, primitive in self.steps:
            if isinstance(primitive, MetroGYMRenderer) and primitive.scale is not None:
                scale = primitive.scale
        return float(scale)

    def _validate_pipeline_shape(self) -> None:
        registry = validation_registry()
        networks = [primitive for _name, primitive in self.steps if isinstance(primitive, Network)]
        if len(networks) != 1:
            registry.raise_issue(registry.system_issue("exactly_one_network", path="MetroSystem.pipeline"))
        for _name, primitive in self.steps:
            if isinstance(primitive, (Line, Station)):
                registry.raise_issue(registry.system_issue("network_only_primitives", path=f"MetroSystem.pipeline.{type(primitive).__name__}"))

    def _validate(self, context: MetroContext) -> None:
        registry = validation_registry()
        if context.network_count != 1:
            registry.raise_issue(registry.system_issue("exactly_one_network", path="MetroContext.network_count"))
        if not context.line_names:
            registry.raise_issue(registry.system_issue("at_least_one_line", path="MetroContext.line_names"))
        if not context.station_names:
            registry.raise_issue(registry.system_issue("at_least_one_station", path="MetroContext.station_names"))
        if not context.train_ids:
            registry.raise_issue(registry.system_issue("at_least_one_train", path="MetroContext.train_ids"))

    def _auto_link_peers(self, context: MetroContext) -> None:
        for train_ids in context.auto_peer_trains.values():
            if train_ids:
                context.simulator.link_peers(train_ids)


def _default_step_name(primitive: BaseMetroPrimitive, index: int) -> str:
    label = getattr(primitive, "name", None) or getattr(primitive, "id", None)
    if label is None:
        label = type(primitive).__name__.lower()
    return f"{index}_{label}".replace(" ", "_")
