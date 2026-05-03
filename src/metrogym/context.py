from __future__ import annotations

from dataclasses import dataclass, field

from beartype import beartype


@beartype
@dataclass
class MetroContext:
    simulator: object
    network_count: int = 0
    line_names: set[str] = field(default_factory=set)
    station_names: set[str] = field(default_factory=set)
    train_ids: set[str] = field(default_factory=set)
    signal_ids: set[str] = field(default_factory=set)
    train_lines: dict[str, str] = field(default_factory=dict)
    auto_peer_trains: dict[str, list[str]] = field(default_factory=dict)
