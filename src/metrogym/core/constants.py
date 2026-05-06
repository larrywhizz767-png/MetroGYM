from __future__ import annotations

from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
DEFAULT_PRIMITIVE_GROUP_ORDER = 4
GRID_STEP = 40
HELP_OVERLAY_ROWS = [
    "Keyboard controls",
    "Ctrl+R      restart from tick 0",
    "Ctrl+-      jump backward 5% of current ticks",
    "Ctrl++      jump forward 5% of current ticks",
    "Ctrl+D      speed up animation by +0.5x",
    "Ctrl+A      slow down animation by -0.5x",
    "Ctrl+M      cycle UI mode",
    "Ctrl+L      cycle log overlay: off / minimalist / trains / signals / collisions",
    "Ctrl+Q      quit visualisation",
    "Ctrl+H      show / hide this help",
]
PATH_STEP = 20
PRIMITIVE_GROUP_ORDER = {
    "network": 0,
    "rolling_stock": 1,
    "control": 2,
    "rendering": 3,
    "generic": DEFAULT_PRIMITIVE_GROUP_ORDER,
}
ROOBERT_DIR = ASSETS_DIR / "fonts" / "Roobert"
ROOBERT_REGULAR = ROOBERT_DIR / "Roobert-Regular.otf"
ROOBERT_MEDIUM = ROOBERT_DIR / "Roobert-Medium.otf"
ROOBERT_SEMIBOLD = ROOBERT_DIR / "Roobert-SemiBold.otf"
ROOBERT_BOLD = ROOBERT_DIR / "Roobert-Bold.otf"
TRAIN_COLLISION_RADIUS = 20
TRAIN_HEIGHT = 16
TRAIN_WIDTH = 26
LOG_OVERLAY_MAX_ROWS = 16
LOG_OVERLAY_MODES: tuple[str, ...] = ("off", "minimalist", "trains", "signals", "collisions")
