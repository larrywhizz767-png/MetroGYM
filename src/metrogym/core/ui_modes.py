from __future__ import annotations

from typing import Literal, TypeAlias

from beartype import beartype

UIMode: TypeAlias = Literal["minimal", "full", "dynamic", "static"]

UI_MODES: tuple[UIMode, ...] = ("minimal", "full", "dynamic", "static")
UI_MODE_LABELS: dict[UIMode, str] = {
    "minimal": "Minimal",
    "full": "Full",
    "dynamic": "Dynamic",
    "static": "Static",
}


@beartype
def next_ui_mode(mode: UIMode | str) -> UIMode:
    current = validate_ui_mode(mode)
    index = UI_MODES.index(current)
    return UI_MODES[(index + 1) % len(UI_MODES)]


@beartype
def ui_mode_label(mode: UIMode | str) -> str:
    return UI_MODE_LABELS[validate_ui_mode(mode)]


@beartype
def validate_ui_mode(mode: UIMode | str) -> UIMode:
    if mode in UI_MODES:
        return mode
    modes = ", ".join(UI_MODES)
    raise ValueError(f"Unknown UI mode {mode!r}. Expected one of: {modes}")
