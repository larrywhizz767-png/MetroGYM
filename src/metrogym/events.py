from __future__ import annotations

"""Public event records produced by the runtime world."""

from dataclasses import dataclass

from beartype import beartype

from metrogym.core.coordinates import Position


@beartype
@dataclass(frozen=True)
class CollisionEvent:
    """Describe a detected train collision.

    Collision events are immutable snapshots recorded on both the involved train
    and the world control system. They are surfaced through solver observations
    and world views so agents can react to incidents.

    Args:
        train_id (str):
            Identifier of the reporting train.
        peer_id (str):
            Identifier of the other train involved.
        position (Position):
            Collision location.
    """

    train_id: str
    peer_id: str
    position: Position
