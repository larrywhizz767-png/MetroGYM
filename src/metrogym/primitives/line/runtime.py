from __future__ import annotations

from dataclasses import dataclass
from beartype import beartype
from metrogym.core.colors import ColorRGBA
from metrogym.core.coordinates import Position


@beartype
@dataclass(frozen=True)
class RuntimeLine:
    name: str
    color: ColorRGBA
    path: list[Position]

    def size(self) -> int:
        return len(self.path)

    @beartype
    def get(self, index: int) -> Position:
        return self.path[index]

    def midpoint_path(self) -> list[Position]:
        mid = len(self.path) // 2
        return [*self.path[mid:], *self.path[:mid]]
