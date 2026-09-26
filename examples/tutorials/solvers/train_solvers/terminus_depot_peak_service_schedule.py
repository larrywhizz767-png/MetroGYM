from __future__ import annotations

"""Run peak dispatching from a western depot on an east-west terminus line."""

from dataclasses import dataclass, field

from beartype import beartype

from depot_peak_service_schedule import (
    CRUISE_SPEED,
    DEPOT_CAPACITY,
    TICK_MS,
    DepotServiceAgent,
    FleetSchedule,
)
from metrogym import Color, MetroSystem
from metrogym.core.coordinates import Position
from metrogym.primitives import Line, Network, Station, Train
from metrogym.solvers import TrainDecision, TrainObservation


@beartype
@dataclass
class TerminusDepotServiceAgent(DepotServiceAgent):
    """Add eastern-terminus diagnostics to the shared depot scheduling policy."""

    eastern_terminus: Position
    _at_eastern_terminus: bool = field(default=False, init=False)

    def reset(self) -> None:
        super().reset()
        self._at_eastern_terminus = False

    def act(self, observation: TrainObservation) -> TrainDecision:
        decision = super().act(observation)
        at_eastern_terminus = observation.self.position.distance(self.eastern_terminus) <= 1
        if at_eastern_terminus and not self._at_eastern_terminus:
            clock_minute = self.schedule.clock_minute(observation.tick)
            print(
                f"[TERMINUS] {self.schedule.clock_label(clock_minute)} | "
                f"service {self.service_rank + 1} reached Eastern Terminus and is reversing westbound"
            )
        self._at_eastern_terminus = at_eastern_terminus
        return decision


def terminus_service_path(depot_bay: Position) -> list[Position]:
    """Create a depot spur and bidirectional passenger corridor between termini."""
    depot_gate = Position(160, 570)
    western_terminus = Position(260, 430)
    central = Position(580, 430)
    eastern_terminus = Position(980, 430)
    return [
        depot_bay,
        depot_gate,
        western_terminus,
        Position(400, 430),
        central,
        Position(760, 430),
        eastern_terminus,
        Position(760, 430),
        central,
        Position(400, 430),
        western_terminus,
        depot_gate,
        depot_bay,
    ]


def build_system(*, tick_ms: int = TICK_MS, render_scale: int | float = 1) -> MetroSystem:
    """Build an east-west terminus line with a western depot and peak fleet plan."""
    depot_bays = tuple(Position(60, 440 + rank * 36) for rank in range(DEPOT_CAPACITY))
    eastern_terminus = Position(980, 430)
    schedule = FleetSchedule(fleet_size=len(depot_bays))
    lines = [Line(f"East-West Service {rank + 1}", Color.BLUE, terminus_service_path(depot_bay)) for rank, depot_bay in enumerate(depot_bays)]
    stations = [
        Station("Western Terminus", (260, 430), radius=11, label="West terminus"),
        Station("Westfield", (400, 430)),
        Station("Central", (580, 430), radius=10),
        Station("Riverside", (760, 430)),
        Station("Eastern Terminus", eastern_terminus, radius=11, label="East terminus"),
        Station("Western Depot Gate", (160, 570), label="Depot access"),
        *[Station(f"Western Depot Bay {rank + 1}", depot_bay, label=f"Bay {rank + 1}") for rank, depot_bay in enumerate(depot_bays)],
    ]
    services = [
        Train(
            f"East-West Service {rank + 1}",
            line=f"East-West Service {rank + 1}",
            solver=TerminusDepotServiceAgent(rank, depot_bay, schedule, eastern_terminus),
            speed=CRUISE_SPEED,
            asset="metro_nose",
        )
        for rank, depot_bay in enumerate(depot_bays)
    ]

    return MetroSystem(
        name="Western Depot: East-West Peak Service",
        tick_ms=tick_ms,
        size=(1_080, 760),
        render_scale=render_scale,
    ).pipeline([Network([*lines, *stations]), *services])


def main() -> None:
    print("[START] Eight western depot bays feed an east-west terminus line. One tick equals five simulated minutes.")
    system = build_system().fit()
    system.simulator.set_clock_label_provider(lambda tick: FleetSchedule.clock_label(FleetSchedule.clock_minute(tick)))
    system.run()


if __name__ == "__main__":
    main()
