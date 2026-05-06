from __future__ import annotations

from beartype import beartype

from metrogym.core.coordinates import PositionLike, to_position
from metrogym.solvers import SignalAgent, SignalVerb, reset_solver_state


@beartype
class RuntimeTrafficLight:
    @beartype
    def __init__(self, id: str, position: PositionLike, initial_green: bool = True, period_ticks: int = 5, label: str | None = None, solver: object | None = None):
        self.id = id
        self.position = to_position(position)
        self.green = initial_green
        self.granted_line: str | None = None
        self.granted_train_id: str | None = None
        self.period_ticks = max(1, period_ticks)
        self.label = label
        self.solver = solver
        self.control = None
        self._initial_green = initial_green
        self._ticks_since_change = 0

    def reset(self) -> None:
        self.green = self._initial_green
        self.granted_line = None
        self.granted_train_id = None
        self._ticks_since_change = 0
        reset_solver_state(self.solver)

    @beartype
    def set_state(self, *, green: bool, granted_line: str | None = None, granted_train_id: str | None = None) -> None:
        self.green = green
        self.granted_line = granted_line if green else None
        self.granted_train_id = granted_train_id if green else None
        self._ticks_since_change = 0

    def update(self) -> None:
        self._ticks_since_change += 1
        if self.solver is not None and self.control is not None and hasattr(self.control, "simulator"):
            if not isinstance(self.solver, SignalAgent):
                raise TypeError(f"Signal solver {self.solver!r} must inherit from SignalAgent.")
            decision = self.solver(self.control.simulator.world_view(signal_id=self.id).observe_signal(self.id))
            if decision.verb == SignalVerb.AUTO:
                return
            if decision.verb == SignalVerb.DENY or decision.verb == SignalVerb.LOCK_ALL:
                self.set_state(green=False)
                return
            if decision.verb == SignalVerb.TOGGLE:
                self.set_state(green=not self.green)
                return
            self.set_state(green=True, granted_line=decision.granted_line, granted_train_id=decision.granted_train_id)
            return
        if self._ticks_since_change >= self.period_ticks:
            self.green = not self.green
            self.granted_line = None
            self.granted_train_id = None
            self._ticks_since_change = 0

    @property
    def ticks_since_change(self) -> int:
        return self._ticks_since_change

    def draw(self, surface: object, *args: object, **kwargs: object) -> None:
        renderer = kwargs.get("renderer")
        if renderer is None:
            raise ValueError("TrafficLight.draw requires renderer=...")
        renderer.draw_traffic_light(surface, self, *args)


TrafficLight = RuntimeTrafficLight
