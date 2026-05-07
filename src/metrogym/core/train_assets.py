from __future__ import annotations

"""Public helpers for train sprite assets."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal, TypeAlias

import pygame
from beartype import beartype

from metrogym.core.constants import ASSETS_DIR

TrainAssetName: TypeAlias = Literal["metro_nose", "maintenance", "city_tram", "bullet_metro"]

DEFAULT_TRAIN_ASSET: TrainAssetName = "metro_nose"
TRAIN_ASSET_NAMES: tuple[TrainAssetName, ...] = ("metro_nose", "maintenance", "city_tram", "bullet_metro")
TRAIN_ASSET_SCALES: tuple[int, ...] = (1, 2, 3, 4)
TRAIN_ASSETS_DIR = ASSETS_DIR / "trains"
TRAIN_ASSET_BASE_SIZE = (64, 40)


@beartype
@dataclass(frozen=True)
class TrainAsset:
    """Describe one train sprite family.

    Args:
        name (TrainAssetName):
            Stable asset identifier.
        title (str):
            Human-readable title for docs and UI.
        width (int):
            Base sprite width in pixels.
        height (int):
            Base sprite height in pixels.
        svg_paths (dict[int, Path]):
            SVG files keyed by integer scale.
    """

    name: TrainAssetName
    title: str
    width: int
    height: int
    svg_paths: dict[int, Path]


@beartype
def validate_train_asset_name(name: TrainAssetName | str) -> TrainAssetName:
    """Validate and normalise a public train asset name.

    Args:
        name (TrainAssetName | str):
            Asset name to validate.

    Returns:
        TrainAssetName:
            Validated asset name.

    Raises:
        ValueError:
            If the asset name is not supported.
    """
    if name in TRAIN_ASSET_NAMES:
        return name
    names = ", ".join(TRAIN_ASSET_NAMES)
    raise ValueError(f"Unknown train asset {name!r}. Expected one of: {names}")


@beartype
def train_asset(name: TrainAssetName | str = DEFAULT_TRAIN_ASSET) -> TrainAsset:
    """Return metadata for a public train asset.

    Args:
        name (TrainAssetName | str, default=DEFAULT_TRAIN_ASSET):
            Asset name to resolve.

    Returns:
        TrainAsset:
            Asset metadata.
    """
    asset_name = validate_train_asset_name(name)
    return train_asset_manifest()[asset_name]


@lru_cache(maxsize=1)
def train_asset_manifest() -> dict[TrainAssetName, TrainAsset]:
    """Return the full train-asset manifest.

    Returns:
        dict[TrainAssetName, TrainAsset]:
            Asset metadata keyed by asset name.
    """
    width, height = TRAIN_ASSET_BASE_SIZE
    return {
        name: TrainAsset(
            name=name,
            title=name.replace("_", " ").title(),
            width=width,
            height=height,
            svg_paths={scale: TRAIN_ASSETS_DIR / f"{name}_{width * scale}x{height * scale}.svg" for scale in TRAIN_ASSET_SCALES},
        )
        for name in TRAIN_ASSET_NAMES
    }


@beartype
def load_train_asset_surface(name: TrainAssetName | str = DEFAULT_TRAIN_ASSET, *, scale: int | float = 1.0) -> object:
    """Load a pygame surface for a train asset.

    Args:
        name (TrainAssetName | str, default=DEFAULT_TRAIN_ASSET):
            Asset name to load.
        scale (int | float, default=1.0):
            Display scale requested by the renderer.

    Returns:
        object:
            Pygame surface containing the scaled train sprite.
    """
    asset = train_asset(name)
    source_scale = _train_display_scale_for(scale)
    target_width = max(1, asset.width * source_scale)
    target_height = max(1, asset.height * source_scale)
    return _load_train_asset_surface(asset.name, source_scale, target_width, target_height)


@lru_cache(maxsize=128)
def _load_train_asset_surface(name: TrainAssetName, source_scale: int, width: int, height: int) -> object:
    asset = train_asset(name)
    surface = pygame.image.load(str(asset.svg_paths[source_scale])).convert_alpha()
    if surface.get_size() == (width, height):
        return surface
    return pygame.transform.smoothscale(surface, (width, height))


@beartype
def _asset_scale_for(scale: int | float) -> int:
    rounded = round(float(scale))
    return max(min(rounded, max(TRAIN_ASSET_SCALES)), min(TRAIN_ASSET_SCALES))


@beartype
def _train_display_scale_for(scale: int | float) -> int:
    rounded = round(float(scale))
    if rounded <= min(TRAIN_ASSET_SCALES):
        return min(TRAIN_ASSET_SCALES)
    return max(min(rounded - 1, max(TRAIN_ASSET_SCALES)), min(TRAIN_ASSET_SCALES))
