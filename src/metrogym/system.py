from __future__ import annotations

"""Public pipeline facade for building and running MetroGYM worlds.

This module exposes ``MetroSystem``, the main entry point used by readers of
MetroGYM. The class intentionally mirrors the high-level feel of a
scikit-learn-style pipeline: users declare primitives, call ``fit()``, and then
run or step the resulting world.
"""

from collections.abc import Iterable
from pathlib import Path
import pickle
from typing import ClassVar

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
    """Build, validate, run, and persist a complete metro world.

    ``MetroSystem`` is the main public facade of MetroGYM. You compose a world by
    passing declarative primitives into ``pipeline()``, materialise runtime
    state with ``fit()``, and then either visualise the world with ``run()`` or
    advance it headlessly with ``step()``.

    Args:
        name (str, default="Metro Gymulation"):
            Title shown on the simulation window.
        tick_ms (int, default=500):
            Duration of one simulation tick in milliseconds.
        size (PositionLike, default=(700, 520)):
            Logical canvas size of the world before renderer scaling.
        verbose (bool, default=False):
            Enables verbose runtime behaviour for components that support it.
        stop_all_on_collision (bool, default=False):
            If ``True``, any collision triggers an emergency stop for the whole
            control system.
        render_scale (int | float, default=2.0):
            Base rendering scale used when no renderer primitive overrides it.

    Attributes:
        steps (list[tuple[str, BaseMetroPrimitive]]):
            Named pipeline steps in user-provided order.
        context (MetroContext | None):
            Build context populated after ``fit()``.
        simulator (RuntimeSimulator | None):
            Runtime simulator created during ``fit()``.

    Notes:
        ``save()`` and ``load()`` persist the declarative pipeline and system
        configuration, not the transient fitted runtime state. Loading always
        returns an unfitted system that can be re-run, stepped, or extended with
        more primitives before calling ``fit()`` again.

    Examples:
        !!! example "Create and run a small world"

            ```python
            from metrogym import Color, MetroSystem, train
            from metrogym.primitives import Line, Network, Station, Train

            system = MetroSystem(name="Starter").pipeline([
                Network([
                    Line("Loop", Color.BLUE, [(120, 120), (400, 120), (400, 280), (120, 280), (120, 120)]),
                    Station("Central", (120, 120)),
                    Station("East", (400, 120)),
                ]),
                Train("A", line="Loop", solver=train.always_proceed()),
            ])

            system.fit().run()
            ```
    """

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

    SERIALIZATION_VERSION: ClassVar[int] = 1

    @beartype
    def pipeline(self, steps: Iterable[BaseMetroPrimitive | tuple[str, BaseMetroPrimitive]]) -> "MetroSystem":
        """Register the declarative primitives that define the world.

        Args:
            steps (Iterable[BaseMetroPrimitive | tuple[str, BaseMetroPrimitive]]):
                Primitives or ``(name, primitive)`` pairs. Unnamed primitives are
                assigned a stable generated step name.

        Returns:
            MetroSystem:
                The same system instance, allowing chained construction.
        """
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
        """Validate the pipeline and build runtime state.

        The fit step creates a ``RuntimeSimulator``, sorts primitives by
        primitive group, applies every primitive to a fresh ``MetroContext``,
        validates the resulting world, and auto-links same-line peer trains when
        requested.

        Returns:
            MetroSystem:
                The fitted system.

        Raises:
            ValueError:
                Raised through the validation registry when the pipeline shape or
                built world violates MetroGYM rules.
        """
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
        """Open the pygame visualisation loop.

        Args:
            block (bool, default=True):
                If ``True``, run the window loop in the current thread. If
                ``False``, spawn the loop in a background thread.
        """
        if self.simulator is None:
            self.fit()
        self.simulator.show(block=block)

    @beartype
    def step(self, n: int = 1) -> "MetroSystem":
        """Advance the fitted world headlessly by a fixed number of ticks.

        Args:
            n (int, default=1):
                Number of ticks to execute. Negative values are clamped to zero.

        Returns:
            MetroSystem:
                The same fitted system after the requested steps.
        """
        if self.simulator is None:
            self.fit()
        for _ in range(max(0, n)):
            self.simulator.tick()
        return self

    def reset(self) -> "MetroSystem":
        """Reset the runtime world back to tick zero.

        Returns:
            MetroSystem:
                The same system instance after resetting the simulator.
        """
        if self.simulator is None:
            self.fit()
        self.simulator.reset()
        return self

    @beartype
    def save(self, file_path: str | Path) -> Path:
        """Persist the declarative system configuration to a pickle file.

        The saved payload contains only public system configuration and pipeline
        primitives. Runtime-only state produced by ``fit()``, such as the active
        simulator, current tick, or built context, is intentionally excluded.

        Args:
            file_path (str | Path):
                Destination ``.pkl`` path.

        Returns:
            Path:
                Resolved path written to disk.

        Raises:
            ValueError:
                If the target path does not end with ``.pkl`` or ``.pickle``.
            TypeError:
                If the pipeline contains objects that Python's ``pickle`` module
                cannot serialise.
        """
        resolved_path = Path(file_path).expanduser().resolve()
        if resolved_path.suffix not in {".pkl", ".pickle"}:
            raise ValueError("MetroSystem.save() expects a '.pkl' or '.pickle' file path.")
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        payload = self._serialization_payload()
        try:
            with resolved_path.open("wb") as output_file:
                pickle.dump(payload, output_file, protocol=pickle.HIGHEST_PROTOCOL)
        except OSError as exc:
            raise ValueError(f"MetroSystem.save() could not write to {resolved_path}.") from exc
        except (pickle.PickleError, AttributeError, TypeError) as exc:
            raise TypeError(
                "MetroSystem.save() could not serialise the pipeline. "
                "Ensure every primitive and solver is pickle-compatible."
            ) from exc
        return resolved_path

    @classmethod
    @beartype
    def load(cls, file_path: str | Path) -> "MetroSystem":
        """Load a previously saved declarative system configuration.

        Args:
            file_path (str | Path):
                Path previously written by ``save()``.

        Returns:
            MetroSystem:
                Unfitted system rebuilt from the saved declarative pipeline.

        Raises:
            ValueError:
                If the file does not contain a supported MetroGYM payload.
        """
        resolved_path = Path(file_path).expanduser().resolve()
        try:
            with resolved_path.open("rb") as input_file:
                payload = pickle.load(input_file)
        except (pickle.PickleError, EOFError, AttributeError, ValueError) as exc:
            raise ValueError(f"MetroSystem.load() could not read a MetroGYM pipeline from {resolved_path}.") from exc
        return cls._from_serialization_payload(payload)

    @beartype
    def get_params(self, deep: bool = True) -> dict[str, object]:
        """Return system parameters in a scikit-learn-like shape.

        Args:
            deep (bool, default=True):
                If ``True``, include pipeline primitives and their nested
                parameters under ``step__param`` keys.

        Returns:
            dict[str, object]:
                Parameter mapping describing the system and optionally the whole
                pipeline tree.
        """
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
        """Update system or nested primitive parameters.

        Args:
            **params (object):
                Parameter updates using either direct attribute names or nested
                ``step__param`` syntax.

        Returns:
            MetroSystem:
                The updated system instance.

        Raises:
            ValueError:
                Raised through the validation registry when an unknown parameter
                or pipeline step is referenced.
        """
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

    def _serialization_payload(self) -> dict[str, object]:
        return {
            "format": "metrogym.metro_system",
            "version": self.SERIALIZATION_VERSION,
            "system": {
                "name": self.name,
                "tick_ms": self.tick_ms,
                "size": self.size,
                "verbose": self.verbose,
                "stop_all_on_collision": self.stop_all_on_collision,
                "render_scale": self.render_scale,
            },
            "steps": list(self.steps),
        }

    @classmethod
    def _from_serialization_payload(cls, payload: object) -> "MetroSystem":
        if not isinstance(payload, dict):
            raise ValueError("MetroSystem.load() expected a dictionary payload.")
        if payload.get("format") != "metrogym.metro_system":
            raise ValueError("MetroSystem.load() received an unsupported payload format.")
        if payload.get("version") != cls.SERIALIZATION_VERSION:
            raise ValueError(
                f"MetroSystem.load() supports version {cls.SERIALIZATION_VERSION}, "
                f"got {payload.get('version')!r}."
            )
        system_config = payload.get("system")
        steps = payload.get("steps")
        if not isinstance(system_config, dict):
            raise ValueError("MetroSystem.load() expected a 'system' mapping in the payload.")
        if not isinstance(steps, list):
            raise ValueError("MetroSystem.load() expected a 'steps' list in the payload.")
        system = cls(
            name=system_config["name"],
            tick_ms=system_config["tick_ms"],
            size=system_config["size"],
            verbose=system_config["verbose"],
            stop_all_on_collision=system_config["stop_all_on_collision"],
            render_scale=system_config["render_scale"],
        )
        system.pipeline(steps)
        system.context = None
        system.simulator = None
        return system

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
