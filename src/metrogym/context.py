from __future__ import annotations

"""Shared build-state container used while fitting a MetroGYM pipeline."""

from dataclasses import dataclass, field

from beartype import beartype


@beartype
@dataclass
class MetroContext:
    """Accumulate validated world state during :meth:`MetroSystem.fit`.

    The context is passed from primitive to primitive while the declarative
    pipeline is materialised into runtime objects. Public users usually inspect
    it only after fitting, when they want to understand what the build step
    produced.

    Args:
        simulator (object):
            Runtime simulator receiving built primitives.
        network_count (int, default=0):
            Number of network aggregators encountered so far.
        line_names (set[str], default_factory=set):
            Known line names.
        station_names (set[str], default_factory=set):
            Known station names.
        train_ids (set[str], default_factory=set):
            Known train identifiers.
        signal_ids (set[str], default_factory=set):
            Known signal identifiers.
        train_lines (dict[str, str], default_factory=dict):
            Mapping from train identifier to line name.
        auto_peer_trains (dict[str, list[str]], default_factory=dict):
            Same-line train groups that should be auto-linked for peer checks.
    """

    simulator: object
    network_count: int = 0
    line_names: set[str] = field(default_factory=set)
    station_names: set[str] = field(default_factory=set)
    train_ids: set[str] = field(default_factory=set)
    signal_ids: set[str] = field(default_factory=set)
    train_lines: dict[str, str] = field(default_factory=dict)
    auto_peer_trains: dict[str, list[str]] = field(default_factory=dict)
