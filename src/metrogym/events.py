from __future__ import annotations

from dataclasses import dataclass
from beartype import beartype
from metrogym.core.coordinates import Position


@beartype
@dataclass(frozen=True)
class CollisionEvent:
    train_id: str
    peer_id: str
    position: Position
