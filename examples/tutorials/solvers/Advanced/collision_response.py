from __future__ import annotations

from metrogym import Color, MetroSystem, SignalAgent, SignalObservation, TrainAgent, TrainObservation, signal, train
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train

DEPOT = (120, 360)
COLLISION_SITE = (340, 240)
LEFT_START = (120, 240)
RIGHT_START = (560, 240)


class AlwaysGreenSignalSolver(SignalAgent):
    def act(self, observation: SignalObservation):
        return signal.grant(reason="broken signal stays open")


class CollisionRecoverySolver(TrainAgent):
    def __init__(self, collision_site: tuple[int, int] = COLLISION_SITE, depot: tuple[int, int] = DEPOT):
        self.collision_site = collision_site
        self.depot = depot
        self.phase = "collision"
        self.arrived: set[str] = set()

    def reset(self) -> None:
        self.phase = "collision"
        self.arrived.clear()

    def act(self, observation: TrainObservation):
        current_train = observation.self
        if observation.collision_events and self.phase == "collision":
            self.phase = "response"
        if self.phase == "response" and current_train.id == "WORK-1" and self._near(current_train, self.collision_site):
            self.phase = "reset"
        if self.phase == "reset":
            if current_train.id == "LEFT-1":
                return self._return_or_hold(current_train, LEFT_START)
            if current_train.id == "RIGHT-1":
                return self._return_or_hold(current_train, RIGHT_START)
            if current_train.id == "WORK-1":
                return self._return_or_hold(current_train, self.depot)
        if self.phase == "response":
            if current_train.id == "WORK-1":
                return train.proceed(reason="dispatching maintenance train")
            return train.hold(reason="incident response")
        if current_train.id == "WORK-1":
            return train.hold(reason="waiting in depot")
        return train.proceed()

    def _return_or_hold(self, current_train: object, target: tuple[int, int]):
        if current_train.id in self.arrived:
            return train.hold(reason="returned to safe position")
        if current_train.position.distance(target) <= 1.5:
            self.arrived.add(current_train.id)
            return train.hold(reason="arrived at reset point")
        return train.reverse(reason="returning from incident site")

    def _near(self, current_train: object, point: tuple[int, int], distance: float = 40.0) -> bool:
        return current_train.position.distance(point) <= distance or current_train.next_position.distance(point) <= distance


def build_system(*, tick_ms: int = 280, render_scale: int | float = 2) -> MetroSystem:
    train_solver = CollisionRecoverySolver()
    return MetroSystem(name="Solver Advanced: Collision Response", tick_ms=tick_ms, render_scale=render_scale).pipeline([
        Network([
            Line("Incident Line", Color.BLUE, [LEFT_START, COLLISION_SITE, RIGHT_START, COLLISION_SITE, LEFT_START]),
            Line("Maintenance Spur", Color.YELLOW, [DEPOT, COLLISION_SITE, DEPOT]),
            Station("Left Terminal", LEFT_START),
            Station("Right Terminal", RIGHT_START),
            Station("Incident Site", COLLISION_SITE, radius=10),
            Station("Maintenance Depot", DEPOT),
        ]),
        Train("LEFT-1", line="Incident Line", solver=train_solver, asset="metro_nose"),
        Train("RIGHT-1", line="Incident Line", start_at=50, solver=train_solver, asset="bullet_metro"),
        Train("WORK-1", line="Maintenance Spur", solver=train_solver, asset="maintenance"),
        Signal(
            "Forgotten Signal",
            (340, 205),
            label="STUCK GREEN",
            controls=ControlRule("Incident Line", LEFT_START, COLLISION_SITE),
            solver=AlwaysGreenSignalSolver(),
        ),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
