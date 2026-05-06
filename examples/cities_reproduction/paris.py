from __future__ import annotations

from metrogym import Color, MetroSystem, SignalAgent, SignalObservation, TrainAgent, TrainObservation, signal, train
from metrogym.primitives import ControlRule, Line, Network, Signal, Station, Train

STATIONS: dict[str, tuple[int, int]] = {
    "La Defense": (70, 225),
    "Versailles": (110, 505),
    "Charles de Gaulle": (205, 105),
    "Saint-Lazare": (300, 145),
    "Gare du Nord": (465, 85),
    "Opera": (430, 155),
    "Chatelet": (540, 240),
    "Nation": (825, 225),
    "Bastille": (665, 345),
    "Montparnasse": (285, 395),
    "Denfert": (390, 505),
    "Luxembourg": (455, 365),
    "Austerlitz": (565, 435),
    "Ivry Depot": (785, 445),
    "Invalides": (190, 315),
    "Noisy": (860, 385),
    "Marne-la-Vallee": (955, 150),
    "Maintenance Yard": (915, 535),
    "Workshop Shed": (1035, 620),
}

METRO_BLUE = Color(42, 73, 160)
METRO_GREEN = Color(28, 140, 84)
METRO_ORANGE = Color(232, 126, 36)
RER_RED = Color(192, 41, 66)
RER_PURPLE = Color(135, 76, 180)
SERVICE_YELLOW = Color(250, 207, 44)

COLLISION_SITE = STATIONS["Ivry Depot"]
WORKSHOP_EXIT = STATIONS["Workshop Shed"]
DISABLED_TRAINS = ("M13-LEAD", "M13-FAULT")


def s(name: str) -> tuple[int, int]:
    return STATIONS[name]


def shuttle(*names: str) -> list[tuple[int, int]]:
    points = [s(name) for name in names]
    return [*points, *reversed(points[1:-1]), points[0]]


def distance_to_point(observation: TrainObservation, point: tuple[int, int]) -> float:
    current_train = observation.self
    return min(current_train.position.distance(point), current_train.next_position.distance(point))


class ParisIncidentCoordinator:
    def __init__(self):
        self.phase = "normal"
        self.inspection_ticks = 0
        self.removed_trains: set[str] = set()
        self.simulator: object | None = None
        self.convoy_unlocked = False
        self.incident_point: tuple[int, int] = COLLISION_SITE

    def configure(self, simulator: object) -> None:
        self.simulator = simulator

    def reset(self) -> None:
        self.phase = "normal"
        self.inspection_ticks = 0
        self.removed_trains.clear()
        self.convoy_unlocked = False
        self.incident_point = COLLISION_SITE

    def note_collision(self, point: tuple[int, int] | None = None) -> None:
        if point is not None:
            self.incident_point = point
        if self.phase == "normal":
            self.phase = "dispatch"
            self.inspection_ticks = 0
            self.removed_trains.clear()
            self.convoy_unlocked = False

    def note_maintenance_arrival(self) -> None:
        if self.phase == "dispatch":
            self.phase = "inspection"
            self.inspection_ticks = 0

    def note_inspection_tick(self) -> None:
        if self.phase == "inspection":
            self.inspection_ticks += 1
            if self.inspection_ticks >= 8:
                self.phase = "tow"
                self.unlock_convoy()

    def unlock_convoy(self) -> None:
        if self.convoy_unlocked or self.simulator is None:
            return
        simulator = self.simulator
        simulator.ignore_train_collisions("INSPECT", DISABLED_TRAINS)
        simulator.ignore_train_collisions("M13-LEAD", ["INSPECT", "M13-FAULT"])
        simulator.ignore_train_collisions("M13-FAULT", ["INSPECT", "M13-LEAD"])
        self.convoy_unlocked = True

    def remove_disabled_trains(self) -> None:
        if self.phase != "tow" or self.simulator is None:
            return
        simulator = self.simulator
        active = simulator.world_view().trains
        for train_id in DISABLED_TRAINS:
            if train_id in self.removed_trains or train_id not in active:
                continue
            if simulator.train(train_id).position.distance(WORKSHOP_EXIT) <= 20:
                simulator.deactivate_train(train_id)
                self.removed_trains.add(train_id)
        if self.removed_trains >= set(DISABLED_TRAINS):
            self.phase = "resolved"

    @property
    def lockdown_active(self) -> bool:
        return self.phase in {"dispatch", "inspection", "tow"}


class ParisMetroSolver(TrainAgent):
    def __init__(self, coordinator: ParisIncidentCoordinator):
        self.coordinator = coordinator
        self.guardrail = train.all_of(
            train.respect_signals(approach_distance=60.0),
            train.avoid_collisions(min_distance=65.0),
        )

    def act(self, observation: TrainObservation):
        current_train = observation.self
        if observation.collision_events:
            self.coordinator.note_collision(observation.collision_events[0].position.pygame())
        if self.coordinator.lockdown_active:
            return train.hold(reason="metro network frozen for maintenance recovery")
        if current_train.id == "M8":
            if distance_to_point(observation, s("Opera")) < 80:
                return train.brake_to(1.0, reason="dense platform spacing through Opera")
            return train.accelerate_to(2.0, reason="stop-start metro cadence")
        return self.guardrail(observation)


class ParisRERSolver(TrainAgent):
    def __init__(self, coordinator: ParisIncidentCoordinator):
        self.coordinator = coordinator
        self.guardrail = train.respect_signals(approach_distance=105.0)

    def act(self, observation: TrainObservation):
        current_train = observation.self
        next_signal = observation.signals.next
        if observation.collision_events:
            self.coordinator.note_collision(observation.collision_events[0].position.pygame())
        if self.coordinator.lockdown_active:
            if current_train.id == "RER-A":
                return train.brake_to(1.0, reason="RER-A slowing into protected incident zone")
            return train.hold(reason="RER corridor held during recovery")
        if next_signal is not None and not next_signal.signal_green:
            distance = min(
                current_train.position.distance(next_signal.start),
                current_train.next_position.distance(next_signal.start),
            )
            if distance < 95:
                return train.brake_to(0.0, reason="RER final braking for red signal")
            if distance < 180:
                return train.brake_to(1.5, reason="RER caution braking")
            return train.brake_to(2.5, reason="preparing to decelerate")
        if current_train.id == "RER-A":
            return train.accelerate_to(4.4, reason="cross-city RER express acceleration")
        return train.accelerate_to(3.7, reason="orbital RER cruise")


class ParisCollisionLineSolver(TrainAgent):
    def __init__(self, coordinator: ParisIncidentCoordinator):
        self.coordinator = coordinator

    def act(self, observation: TrainObservation):
        current_train = observation.self
        approach = distance_to_point(observation, COLLISION_SITE)
        if observation.collision_events:
            self.coordinator.note_collision(observation.collision_events[0].position.pygame())
        if self.coordinator.phase == "dispatch":
            if current_train.id == "M13-LEAD":
                return train.hold(reason="lead consist secured after impact")
            return train.hold(reason="damaged consist waiting for maintenance coupling")
        if self.coordinator.phase == "inspection":
            return train.brake_to(0.3, reason="maintenance unlocking the damaged metros")
        if self.coordinator.phase == "tow":
            if current_train.id == "M13-LEAD":
                return train.proceed_at(1.2, reason="lead disabled train following the maintenance convoy")
            return train.proceed_at(1.0, reason="rear disabled train following with recovery spacing")
        if self.coordinator.phase == "resolved":
            return train.hold(reason="disabled train removed into the workshop")
        if current_train.id == "M13-LEAD":
            if approach < 45:
                return train.hold(reason="extended depot-side dwell before the branch")
            if approach < 120:
                return train.brake_to(1.0, reason="braking into the shared depot branch")
            return train.accelerate_to(1.8, reason="line 13 local service")
        if approach < 190:
            return train.accelerate_to(3.2, reason="faulty line 13 train overruns the braking profile")
        return train.accelerate_to(2.6, reason="aggressive line 13 running")


class ParisMaintenanceSolver(TrainAgent):
    def __init__(self, coordinator: ParisIncidentCoordinator):
        self.coordinator = coordinator

    def act(self, observation: TrainObservation):
        if observation.collision_events:
            self.coordinator.note_collision(observation.collision_events[0].position.pygame())
        if self.coordinator.phase == "normal":
            return train.brake_to(0.0, reason="maintenance set waiting beyond the depot")
        if self.coordinator.phase == "dispatch":
            if distance_to_point(observation, self.coordinator.incident_point) < 6:
                self.coordinator.note_maintenance_arrival()
                return train.hold(reason="maintenance reaching the crash site")
            if distance_to_point(observation, self.coordinator.incident_point) < 26:
                return train.brake_to(0.2, reason="maintenance easing into the damaged metros")
            return train.accelerate_to(3.2, reason="maintenance dispatched down the depot branch")
        if self.coordinator.phase == "inspection":
            self.coordinator.note_inspection_tick()
            return train.hold(reason="maintenance coupling both disabled metros")
        if self.coordinator.phase == "tow":
            self.coordinator.remove_disabled_trains()
            if self.coordinator.phase == "resolved":
                return train.hold(reason="damaged metros delivered into the workshop")
            return train.reverse_at(1.2, reason="maintenance leading both disabled metros back to the depot")
        return train.hold(reason="incident solved inside the maintenance workshop")


class ParisDispatchSolver(SignalAgent):
    def __init__(self, coordinator: ParisIncidentCoordinator, approach_distance: float, release_distance: float, red_hold_ticks: int, incident_line: str | None = None):
        self.coordinator = coordinator
        self.dispatch = signal.priority_queue(
            approach_distance=approach_distance,
            release_distance=release_distance,
            red_hold_ticks=red_hold_ticks,
        )
        self.incident_line = incident_line

    def reset(self) -> None:
        self.dispatch.reset()

    def act(self, observation: SignalObservation):
        if observation.collision_events:
            self.coordinator.note_collision(observation.collision_events[0].position.pygame())
        if self.coordinator.phase == "tow":
            return signal.grant(reason="convoy route opened toward the workshop")
        if self.coordinator.lockdown_active:
            if self.incident_line is not None:
                return signal.grant(line=self.incident_line, reason="holding open maintenance access corridor")
            return signal.lock_all(reason="incident lockdown across the trunk")
        return self.dispatch(observation)


def build_system(*, tick_ms: int = 230, render_scale: int | float = 2) -> MetroSystem:
    coordinator = ParisIncidentCoordinator()
    metro_solver = ParisMetroSolver(coordinator)
    rer_solver = ParisRERSolver(coordinator)
    collision_solver = ParisCollisionLineSolver(coordinator)
    maintenance_solver = ParisMaintenanceSolver(coordinator)
    depot_dispatch = ParisDispatchSolver(
        coordinator,
        approach_distance=70.0,
        release_distance=95.0,
        red_hold_ticks=3,
        incident_line="Maintenance Service",
    )
    chatelet_dispatch = ParisDispatchSolver(
        coordinator,
        approach_distance=90.0,
        release_distance=120.0,
        red_hold_ticks=4,
    )
    interchanges = {
        "Charles de Gaulle",
        "Saint-Lazare",
        "Opera",
        "Chatelet",
        "Nation",
        "Montparnasse",
        "Austerlitz",
        "Invalides",
        "Bastille",
        "Ivry Depot",
        "Maintenance Yard",
    }
    stations = [
        Station(name, pos, radius=9 if name in interchanges else 6)
        for name, pos in STATIONS.items()
        if name != "Workshop Shed"
    ]
    return MetroSystem(
        name="City Reproduction: Paris Network",
        tick_ms=tick_ms,
        size=(1040, 640),
        render_scale=render_scale,
    ).pipeline([
        Network([
            Line("Metro 8", METRO_GREEN, shuttle("La Defense", "Charles de Gaulle", "Opera", "Bastille", "Nation", "Ivry Depot")),
            Line("Metro 13", METRO_BLUE, shuttle("Versailles", "Invalides", "Montparnasse", "Luxembourg", "Austerlitz", "Ivry Depot", "Maintenance Yard", "Workshop Shed")),
            Line("Metro 6", METRO_ORANGE, shuttle("Charles de Gaulle", "Saint-Lazare", "Chatelet", "Austerlitz", "Denfert")),
            Line("RER A", RER_RED, shuttle("La Defense", "Saint-Lazare", "Chatelet", "Nation", "Marne-la-Vallee")),
            Line("RER C", RER_PURPLE, shuttle("Versailles", "Invalides", "Luxembourg", "Austerlitz", "Noisy")),
            Line("Maintenance Service", SERVICE_YELLOW, shuttle("Workshop Shed", "Maintenance Yard", "Ivry Depot", "Austerlitz", "Luxembourg", "Montparnasse")),
            *stations,
        ]),
        Train("M8", line="Metro 8", solver=metro_solver, asset="city_tram", speed=1),
        Train("M13-LEAD", line="Metro 13", start_at=18, solver=collision_solver, asset="metro_nose", speed=1),
        Train("M13-FAULT", line="Metro 13", start_at=12, solver=collision_solver, asset="metro_nose", speed=2),
        Train("M6", line="Metro 6", start_at=42, solver=metro_solver, asset="city_tram", speed=1),
        Train("RER-A", line="RER A", solver=rer_solver, asset="bullet_metro", speed=2),
        Train("RER-C", line="RER C", start_at=58, solver=rer_solver, asset="bullet_metro", speed=2),
        Train("INSPECT", line="Maintenance Service", solver=maintenance_solver, asset="maintenance", speed=1),
        Signal(
            "Depot Branch Response",
            (735, 442),
            label="DEP",
            controls=[
                ControlRule("Metro 13", s("Austerlitz"), s("Ivry Depot")),
                ControlRule("Metro 8", s("Nation"), s("Ivry Depot")),
                ControlRule("Maintenance Service", s("Maintenance Yard"), s("Ivry Depot")),
            ],
            solver=depot_dispatch,
        ),
        Signal(
            "Chatelet Trunk",
            (565, 215),
            label="CHT",
            controls=[
                ControlRule("RER A", s("Saint-Lazare"), s("Chatelet")),
                ControlRule("Metro 6", s("Saint-Lazare"), s("Chatelet")),
            ],
            solver=chatelet_dispatch,
        ),
    ])


def prepare_system(system: MetroSystem) -> MetroSystem:
    if system.simulator is None:
        system.fit()
    coordinator = system.simulator.train("INSPECT").solver.coordinator
    coordinator.configure(system.simulator)
    return system


def main() -> None:
    prepare_system(build_system().fit()).run()


if __name__ == "__main__":
    main()
