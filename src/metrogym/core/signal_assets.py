from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal, TypeAlias

import pygame
from beartype import beartype

from metrogym.core.constants import ASSETS_DIR

SignalAssetState: TypeAlias = Literal["go", "stop"]

SIGNAL_ASSET_STATES: tuple[SignalAssetState, ...] = ("go", "stop")
SIGNAL_ASSET_SCALES: tuple[int, ...] = (1, 2, 3, 4)
SIGNAL_ASSETS_DIR = ASSETS_DIR / "signals"
SIGNAL_ASSET_BASE_SIZE = (16, 40)
SIGNAL_ASSET_SIZES = {
    1: (16, 40),
    2: (31, 80),
    3: (47, 120),
    4: (63, 160),
}


@beartype
@dataclass(frozen=True)
class SignalAsset:
    state: SignalAssetState
    title: str
    width: int
    height: int
    svg_paths: dict[int, Path]


@beartype
def signal_asset(state: SignalAssetState | str) -> SignalAsset:
    asset_state = validate_signal_asset_state(state)
    return signal_asset_manifest()[asset_state]


@beartype
def validate_signal_asset_state(state: SignalAssetState | str) -> SignalAssetState:
    if state in SIGNAL_ASSET_STATES:
        return state
    states = ", ".join(SIGNAL_ASSET_STATES)
    raise ValueError(f"Unknown signal asset state {state!r}. Expected one of: {states}")


@lru_cache(maxsize=1)
def signal_asset_manifest() -> dict[SignalAssetState, SignalAsset]:
    width, height = SIGNAL_ASSET_BASE_SIZE
    return {
        state: SignalAsset(
            state=state,
            title=f"{state.title()} signal",
            width=width,
            height=height,
            svg_paths={scale: SIGNAL_ASSETS_DIR / f"{state}_signal_{asset_width}x{asset_height}.svg" for scale, (asset_width, asset_height) in SIGNAL_ASSET_SIZES.items()},
        )
        for state in SIGNAL_ASSET_STATES
    }


@beartype
def load_signal_asset_surface(state: SignalAssetState | str, *, scale: int | float = 1.0) -> object:
    asset = signal_asset(state)
    target_width = max(1, round(asset.width * float(scale)))
    target_height = max(1, round(asset.height * float(scale)))
    source_scale = _asset_scale_for(scale)
    return _load_signal_asset_surface(asset.state, source_scale, target_width, target_height)


@lru_cache(maxsize=64)
def _load_signal_asset_surface(state: SignalAssetState, source_scale: int, width: int, height: int) -> object:
    asset = signal_asset(state)
    surface = pygame.image.load(str(asset.svg_paths[source_scale])).convert_alpha()
    if surface.get_size() == (width, height):
        return surface
    return pygame.transform.smoothscale(surface, (width, height))


@beartype
def _asset_scale_for(scale: int | float) -> int:
    rounded = round(float(scale))
    return max(min(rounded, max(SIGNAL_ASSET_SCALES)), min(SIGNAL_ASSET_SCALES))
