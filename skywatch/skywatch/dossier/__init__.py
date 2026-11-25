"""Evidence dossiers: auditable per-candidate folders and viewing imagery."""
from .build import CLOSING_STATEMENT, build_dossier, detail_grid, thumbnail
from .hires import (
    ATTRIBUTION,
    MAX_TILES_PER_CANDIDATE,
    RELEASE_DATE_MEANING,
    HiresError,
    TileCapExceeded,
    chip_xy,
    hires_chip,
    tile_budget,
    wayback_releases,
    wayback_series,
)

__all__ = [
    "ATTRIBUTION",
    "CLOSING_STATEMENT",
    "MAX_TILES_PER_CANDIDATE",
    "RELEASE_DATE_MEANING",
    "HiresError",
    "TileCapExceeded",
    "build_dossier",
    "chip_xy",
    "detail_grid",
    "hires_chip",
    "thumbnail",
    "tile_budget",
    "wayback_releases",
    "wayback_series",
]
