from __future__ import annotations

"""Simulate depot dispatching for a passenger loop with AM and PM peaks."""

from dataclasses import dataclass, field

from beartype import beartype

from metrogym import Color, MetroSystem, train
from metrogym.core.coordinates import Position
from metrogym.primitives import Line, Network, Station, Train
from metrogym.solvers import TrainAgent, TrainDecision, TrainObservation


TICK_MS = 300
SIMULATED_MINUTES_PER_TICK = 5
SERVICE_DAY_START_MINUTE = 7 * 60 + 30
OFF_PEAK_FLEET = 4
PEAK_FLEET = 8
DEPOT_CAPACITY = 8
OFF_PEAK_DISPATCH_HEADWAY_TICKS = 1
PEAK_DISPATCH_HEADWAY_TICKS = 0
CRUISE_SPEED = 3


@beartype
@dataclass
class FleetSchedule:
    """Coordinate peak fleet needs and safe, staggered depot departures."""

    fleet_size: int
    target_fleet: int = field(default=0, init=False)
    dispatch_ticks: dict[int, int] = field(default_factory=dict, init=False)
    _last_tick: int = field(default=-1, init=False)

    def refresh(self, tick: int) -> None:
        """Update the schedule once per simulation tick and print its state."""
        if tick == self._last_tick:
            return
        self._last_tick = tick
        clock_minute = self.clock_minute(tick)
        required_fleet = PEAK_FLEET if self.is_peak(clock_minute) else OFF_PEAK_FLEET

        if required_fleet != self.target_fleet:
            previous_target = self.target_fleet
            self.target_fleet = required_fleet
            print(
                f"[SCHEDULE] {self.clock_label(clock_minute)} | "
                f"fleet need changed: {previous_target} -> {required_fleet} trains"
            )
            if required_fleet > previous_target:
                dispatch_headway = self.dispatch_headway(clock_minute)
                for rank in range(previous_target, required_fleet):
                    release_tick = tick + (rank - previous_target) * dispatch_headway
                    self.dispatch_ticks[rank] = release_tick
                    print(
                        f"[DISPATCH NEED] {self.clock_label(clock_minute)} | "
                        f"release service {rank + 1} at tick {release_tick} "
                        f"with a {dispatch_headway}-tick depot headway"
                    )
            else:
                returning = ", ".join(f"service {rank + 1}" for rank in range(required_fleet, previous_target))
                print(
                    f"[RETURN NEED] {self.clock_label(clock_minute)} | "
                    f"{returning} must complete its current loop and return to its dedicated depot bay"
                )

        if clock_minute % 30 == 0:
            print(
                f"[CLOCK] {self.clock_label(clock_minute)} | peak={self.is_peak(clock_minute)} | "
                f"required fleet={self.target_fleet}/{self.fleet_size} | "
                f"depot departure headway={self.dispatch_headway(clock_minute)} ticks"
            )

    def should_operate(self, rank: int, tick: int) -> bool:
        """Return whether this ranked service has been released for operation."""
        return rank < self.target_fleet and tick >= self.dispatch_ticks.get(rank, 0)

    @staticmethod
    def dispatch_headway(clock_minute: int) -> int:
        return PEAK_DISPATCH_HEADWAY_TICKS if FleetSchedule.is_peak(clock_minute) else OFF_PEAK_DISPATCH_HEADWAY_TICKS

    @staticmethod
    def clock_minute(tick: int) -> int:
        return (SERVICE_DAY_START_MINUTE + tick * SIMULATED_MINUTES_PER_TICK) % (24 * 60)

    @staticmethod
    def is_peak(clock_minute: int) -> bool:
        return 8 * 60 <= clock_minute < 9 * 60 or 16 * 60 <= clock_minute < 17 * 60

    @staticmethod
    def clock_label(clock_minute: int) -> str:
        return f"{clock_minute // 60:02d}:{clock_minute % 60:02d}"


@beartype
@dataclass
class DepotServiceAgent(TrainAgent):
    """Hold surplus trains in a dedicated bay and release them on schedule."""

    service_rank: int
    depot_bay: Position
    schedule: FleetSchedule
    _released: bool = field(default=False, init=False)
    _returning: bool = field(default=False, init=False)

    def reset(self) -> None:
        self._released = False
        self._returning = False

    def act(self, observation: TrainObservation) -> TrainDecision:
        self.schedule.refresh(observation.tick)
        service = observation.self
        clock = self.schedule.clock_label(self.schedule.clock_minute(observation.tick))
        required_on_route = self.schedule.should_operate(self.service_rank, observation.tick)
        at_depot = service.position.distance(self.depot_bay) <= 1

        if at_depot and not required_on_route:
            if self._released or self._returning:
                print(f"[DEPOT] {clock} | service {self.service_rank + 1} stored safely in its depot bay")
            self._released = False
            self._returning = False
            return train.hold(reason="stored in depot")

        if at_depot:
            if not self._released:
                print(
                    f"[DISPATCH] {clock} | service {self.service_rank + 1} leaves its dedicated depot track; "
                    "passenger-route slot confirmed"
                )
            self._released = True
            self._returning = False
            return train.accelerate_to(CRUISE_SPEED, reason="dispatched from depot")

        if not required_on_route:
            if not self._returning:
                print(
                    f"[RETURN] {clock} | service {self.service_rank + 1} exits passenger service and is returning "
                    "via the dedicated depot access track"
                )
            self._returning = True
            return train.proceed_at(CRUISE_SPEED, reason="returning to depot")

        return train.proceed_at(CRUISE_SPEED, reason="passenger service")


@beartype
@dataclass
class ContinuousLoopServiceAgent(TrainAgent):
    """Keep an off-peak core service on the passenger loop between all stops."""

    schedule: FleetSchedule

    def act(self, observation: TrainObservation) -> TrainDecision:
        self.schedule.refresh(observation.tick)
        return train.proceed_at(CRUISE_SPEED, reason="continuous passenger loop")


def depot_service_path(depot_bay: Position) -> list[Position]:
    """Create one dedicated depot access path plus the shared passenger loop."""
    depot_gate = Position(210, 480)
    junction = Position(330, 390)
    return [
        depot_bay,
        depot_gate,
        junction,
        Position(500, 180),
        Position(760, 240),
        Position(760, 510),
        Position(500, 570),
        junction,
        depot_gate,
        depot_bay,
    ]


def passenger_loop_path() -> list[Position]:
    """Create the passenger-only loop, directly linking Market back to Central."""
    central = Position(500, 180)
    return [central, Position(760, 240), Position(760, 510), Position(500, 570), central]


def build_system(*, tick_ms: int = TICK_MS, render_scale: int | float = 1) -> MetroSystem:
    """Build the depot, passenger route, and four-service peak schedule."""
    depot_bays = tuple(Position(80, 365 + rank * 36) for rank in range(DEPOT_CAPACITY))
    schedule = FleetSchedule(fleet_size=len(depot_bays))
    core_lines = [Line(f"Core Service {rank + 1} Route", Color.BLUE, passenger_loop_path()) for rank in range(OFF_PEAK_FLEET)]
    depot_lines = [
        Line(f"Depot Service {rank + 1} Route", Color.BLUE, depot_service_path(depot_bays[rank]))
        for rank in range(OFF_PEAK_FLEET, DEPOT_CAPACITY)
    ]
    stations = [
        Station("Central", (500, 180), radius=10),
        Station("Museum", (760, 240)),
        Station("Riverside", (760, 510)),
        Station("Market", (500, 570)),
        Station("Depot Gate", (210, 480), label="Depot access"),
        *[Station(f"Depot Bay {rank + 1}", depot_bay, label=f"Bay {rank + 1}") for rank, depot_bay in enumerate(depot_bays)],
    ]
    core_services = [
        Train(
            f"Core Service {rank + 1}",
            line=f"Core Service {rank + 1} Route",
            solver=ContinuousLoopServiceAgent(schedule),
            speed=CRUISE_SPEED,
            asset="metro_nose",
        )
        for rank in range(OFF_PEAK_FLEET)
    ]
    depot_services = [
        Train(
            f"Depot Service {rank + 1}",
            line=f"Depot Service {rank + 1} Route",
            solver=DepotServiceAgent(rank, depot_bay, schedule),
            speed=CRUISE_SPEED,
            asset="metro_nose",
        )
        for rank, depot_bay in enumerate(depot_bays[OFF_PEAK_FLEET:], start=OFF_PEAK_FLEET)
    ]

    return MetroSystem(
        name="Depot Dispatch: AM and PM Peak Service",
        tick_ms=tick_ms,
        size=(900, 680),
        render_scale=render_scale,
    ).pipeline([Network([*core_lines, *depot_lines, *stations]), *core_services, *depot_services])


def main() -> None:
    print("[START] Four core services loop directly from Market to Central. Four depot services join simultaneously at each peak.")
    system = build_system().fit()
    system.simulator.set_clock_label_provider(lambda tick: FleetSchedule.clock_label(FleetSchedule.clock_minute(tick)))
    system.run()


if __name__ == "__main__":
    main()
