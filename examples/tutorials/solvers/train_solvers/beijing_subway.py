from __future__ import annotations

"""A Beijing-inspired subway network with station-aware service profiles."""

from dataclasses import dataclass, field

from beartype import beartype

from metrogym import Color, MetroSystem, train
from metrogym.core.coordinates import Position
from metrogym.primitives import Line, Network, Station, Train
from metrogym.solvers import TrainAgent, TrainDecision, TrainObservation


TICK_MS = 250
CRUISE_SPEED = 3
BRAKING_SPEED = 1.0
BRAKING_DISTANCE = 280.0
NORMAL_DWELL_SECONDS = 5
INTERCHANGE_DWELL_SECONDS = 10


@beartype
@dataclass
class BeijingStationService(TrainAgent):
    """Brake into stations, dwell by station type, and accelerate on departure."""

    stations: tuple[Position, ...]
    interchange_stations: frozenset[Position]
    tick_ms: int = TICK_MS
    _dwell_remaining: int = field(default=0, init=False)
    _departing_station: Position | None = field(default=None, init=False)
    _dwell_complete: bool = field(default=False, init=False)

    def reset(self) -> None:
        self._dwell_remaining = 0
        self._departing_station = None
        self._dwell_complete = False

    def act(self, observation: TrainObservation) -> TrainDecision:
        service = observation.self
        current = service.position

        station = self._station_at(current)
        if station is not None:
            if station != self._departing_station:
                self._departing_station = station
                self._dwell_remaining = 0
                self._dwell_complete = False

            if not self._dwell_complete:
                if service.speed > 0.01:
                    return train.hold(reason="braking into station")
                if self._dwell_remaining == 0:
                    dwell_seconds = INTERCHANGE_DWELL_SECONDS if station in self.interchange_stations else NORMAL_DWELL_SECONDS
                    self._dwell_remaining = round(dwell_seconds * 1_000 / self.tick_ms)
                self._dwell_remaining -= 1
                if self._dwell_remaining > 0:
                    return train.hold(reason=f"platform dwell: {self._dwell_remaining} ticks remaining")
                self._dwell_complete = True
            return train.accelerate_to(CRUISE_SPEED, reason="leaving station")

        if self._departing_station is not None:
            if current.distance(self._departing_station) <= BRAKING_DISTANCE:
                return train.accelerate_to(CRUISE_SPEED, reason="leaving station")
            self._departing_station = None

        if any(service.next_position.distance(station) <= BRAKING_DISTANCE for station in self.stations):
            return train.brake_to(BRAKING_SPEED, reason="braking for station")
        return train.accelerate_to(CRUISE_SPEED, reason="accelerating between stations")

    def _station_at(self, position: Position) -> Position | None:
        for station in self.stations:
            if position.distance(station) <= 1:
                return station
        return None


def build_system(*, tick_ms: int = TICK_MS, render_scale: int | float = 1) -> MetroSystem:
    """Create a five-line Beijing-inspired network using the supplied assets."""
    fuxingmen = Position(400, 390)
    dongdan = Position(720, 390)
    xizhimen = Position(400, 180)
    interchange_stations = frozenset({fuxingmen, dongdan, xizhimen})

    line_1 = (Position(80, 390), fuxingmen, dongdan, Position(1080, 390), Position(1080, 450), Position(80, 450), Position(80, 390))
    line_2 = (xizhimen, Position(720, 180), dongdan, Position(720, 660), fuxingmen, Position(400, 660), xizhimen)
    line_3 = (Position(80, 180), xizhimen, Position(720, 180), Position(1080, 180), Position(1080, 240), Position(80, 240), Position(80, 180))
    line_4 = (Position(80, 660), Position(400, 660), fuxingmen, Position(400, 180), Position(80, 180), Position(80, 660))
    line_5 = (Position(1040, 660), Position(720, 660), dongdan, Position(720, 180), Position(1040, 180), Position(1040, 660))
    lines = (
        ("Line 1", Color.RED, line_1, "beijing_line_1"),
        ("Line 2", Color.PURPLE, line_2, "beijing_line_2"),
        ("Line 3", Color.YELLOW, line_3, "beijing_line_3"),
        ("Line 4", Color.GREEN, line_4, "beijing_line_4"),
        ("Line 5", Color(0, 150, 170), line_5, "beijing_line_5"),
    )
    all_stations = {
        "Pingguoyuan": line_1[0],
        "Fuxingmen": fuxingmen,
        "Dongdan": dongdan,
        "Sihui": line_1[3],
        "Xizhimen": xizhimen,
        "Yonghegong": line_2[1],
        "Beijing South": line_2[3],
        "Tuanjiehu": line_3[3],
        "Gongzhufen": line_4[0],
        "Tiangongyuan": line_5[0],
    }

    return MetroSystem(
        name="Beijing Subway: Station Dwell and Speed Profile",
        tick_ms=tick_ms,
        size=(1_160, 760),
        render_scale=render_scale,
    ).pipeline([
        Network([
            *[Line(name, color, path) for name, color, path, _asset in lines],
            *[Station(name, station, radius=10 if station in interchange_stations else 7) for name, station in all_stations.items()],
        ]),
        *[
            Train(
                f"{name} Service",
                line=name,
                solver=BeijingStationService(path, interchange_stations, tick_ms),
                speed=CRUISE_SPEED,
                asset=asset,
            )
            for name, _color, path, asset in lines
        ],
    ])


def main() -> None:
    print("Normal stations dwell for 5 seconds; interchange stations dwell for 10 seconds.")
    build_system().fit().run()


if __name__ == "__main__":
    main()
