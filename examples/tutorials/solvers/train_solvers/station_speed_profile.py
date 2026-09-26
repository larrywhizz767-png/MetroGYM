from __future__ import annotations

"""Run a two-line service that brakes, dwells, and accelerates at stations."""

from dataclasses import dataclass, field

from beartype import beartype

from metrogym import Color, MetroSystem, train
from metrogym.core.coordinates import Position
from metrogym.primitives import Line, Network, Station, Train
from metrogym.solvers import TrainAgent, TrainDecision, TrainObservation


TICK_MS = 400
MAX_SPEED_KPH = 80
KPH_PER_SPEED_UNIT = 20
CRUISE_SPEED = MAX_SPEED_KPH // KPH_PER_SPEED_UNIT
BRAKING_SPEED = 1.0
BRAKING_DISTANCE = 300.0
CENTRAL_DWELL_SECONDS = 12
STATION_DWELL_TICKS = 5


@beartype
@dataclass
class StationSpeedProfile(TrainAgent):
    """Apply a station-aware speed profile to one train service.

    The simulation maps one speed unit to 20 km/h, so a cruise target of four
    units represents 80 km/h. The runtime eases toward each requested target,
    making the braking and departure acceleration visible in the renderer.
    """

    stations: tuple[Position, ...]
    dwell_station: Position
    dwell_ticks: int
    station_dwell_ticks: int = STATION_DWELL_TICKS
    cruise_speed: float = CRUISE_SPEED
    braking_distance: float = BRAKING_DISTANCE
    _dwell_remaining: int = field(default=0, init=False)
    _departing_station: Position | None = field(default=None, init=False)

    def reset(self) -> None:
        self._dwell_remaining = 0
        self._departing_station = None

    def act(self, observation: TrainObservation) -> TrainDecision:
        service = observation.self
        current_position = service.position

        if self._dwell_remaining > 0:
            self._dwell_remaining -= 1
            return train.hold(reason=f"station dwell: {self._dwell_remaining} ticks remaining")

        if self._departing_station is not None:
            if current_position.distance(self._departing_station) <= self.braking_distance:
                return train.accelerate_to(self.cruise_speed, reason="clearing departure station")
            self._departing_station = None

        station = self._station_at(current_position)
        if station is not None:
            self._dwell_remaining = self.dwell_ticks if station == self.dwell_station else self.station_dwell_ticks
            self._departing_station = station
            if station == self.dwell_station:
                return train.hold(reason=f"dwelling at Central for {CENTRAL_DWELL_SECONDS} seconds")
            return train.hold(reason="dwelling at station")

        if any(service.next_position.distance(station) <= self.braking_distance for station in self.stations):
            return train.brake_to(BRAKING_SPEED, reason="braking for next station")

        return train.accelerate_to(self.cruise_speed, reason=f"cruising at {MAX_SPEED_KPH} km/h")

    def _station_at(self, position: Position) -> Position | None:
        for station in self.stations:
            if position.distance(station) <= 1:
                return station
        return None


def build_system(*, tick_ms: int = TICK_MS, render_scale: int | float = 1) -> MetroSystem:
    """Create the station speed-profile demonstration world."""
    central = Position(600, 360)
    harbour_stations = (Position(120, 360), central, Position(1080, 360), Position(1080, 720), Position(120, 720))
    hill_stations = (Position(600, 120), central, Position(600, 900))
    dwell_ticks = round(CENTRAL_DWELL_SECONDS * 1_000 / tick_ms)

    return MetroSystem(
        name="Station Speed Profile: Brake, Dwell, Accelerate",
        tick_ms=tick_ms,
        size=(1_200, 1_000),
        render_scale=render_scale,
    ).pipeline([
        Network([
            Line("Harbour Loop", Color.BLUE, [*harbour_stations, harbour_stations[0]]),
            Line("Hill Shuttle", Color.GREEN, [*hill_stations, hill_stations[1], hill_stations[0]]),
            Station("Harbour", harbour_stations[0]),
            Station("Central", central, radius=12),
            Station("Market", harbour_stations[2]),
            Station("Riverside", harbour_stations[3]),
            Station("Depot", harbour_stations[4]),
            Station("Hilltop", hill_stations[0]),
            Station("Museum", hill_stations[2]),
        ]),
        Train(
            "Harbour Service",
            line="Harbour Loop",
            solver=StationSpeedProfile(harbour_stations, central, dwell_ticks),
            speed=CRUISE_SPEED,
            asset="metro_nose",
        ),
        Train(
            "Hill Service",
            line="Hill Shuttle",
            start_at=50,
            solver=StationSpeedProfile(hill_stations, central, dwell_ticks),
            speed=CRUISE_SPEED,
            asset="metro_nose",
        ),
    ])


def main() -> None:
    build_system().fit().run()


if __name__ == "__main__":
    main()
