"""Land-cover check: is the candidate on cropland, in a settlement or on water?

Uses the ESA WorldCover 10 m map for 2021 (v200), read straight from its
public cloud-optimised GeoTIFF tiles. The map is a single epoch, so every
result says how it relates in time to the candidate's onset.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import threading
import time
from http import HTTPStatus
from pathlib import Path
from typing import Any

import numpy as np
import requests
from rasterio.enums import Resampling
from scipy import ndimage

from ..core import config, io
from ..core.models import BBox, Candidate, CheckResult, CheckStatus

TILE_URL = ("https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"
            "ESA_WorldCover_10m_2021_v200_{tile}_Map.tif")
CHECK_NAME = "landcover"
SOURCE = "ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0"
#: Tile index and raster cache. Looked up at call time.
CACHE_DIR: Path = config.CACHE / "landcover"

#: WorldCover class code -> short name used in every fractions dict.
CLASS_NAMES: dict[int, str] = {
    10: "tree", 20: "shrub", 30: "grass", 40: "cropland", 50: "builtup", 60: "bare",
    70: "snow", 80: "water", 90: "wetland", 95: "mangrove", 100: "moss"}
FRACTION_KEYS: tuple[str, ...] = (*CLASS_NAMES.values(), "nodata")
BUILTUP = 50
#: The whole of this year's imagery went into the map.
MAP_YEAR = 2021
#: WorldCover tiles exist for south-west corners from 60S to 81N.
_LAT_RANGE = (-60, 81)
#: Ring around the footprint used to tell a settlement from a lone structure.
CONTEXT_M = 500.0
#: Share of the footprint a mundane class needs to explain the candidate.
MAJORITY = 0.5
#: Built-up share of the surrounding ring that marks an existing settlement.
SETTLEMENT_CONTEXT = 0.10
#: Connected built-up pixels needed to count as a cluster rather than noise.
MIN_CLUSTER_PX = 5
MAX_RADIUS_M = 50_000.0
_MAX_FOOTPRINT_DEG = 0.25

_TIMEOUT = (10.0, 30.0)
_RETRIES = 3
_index_lock = threading.Lock()
_index: dict[str, bool] = {}
_index_loaded_from: Path | None = None


class LandcoverUnavailable(RuntimeError):
    """WorldCover could not be read for the requested place."""


# --------------------------------------------------------------------------
# Tiles
# --------------------------------------------------------------------------

def tile_name(lat: float, lon: float) -> str:
    """Name of the 3 x 3 degree WorldCover tile holding a point (south-west corner)."""
    south = int(math.floor(lat / 3.0)) * 3
    west = int(math.floor(lon / 3.0)) * 3
    if west >= 180:
        west -= 360
    return f"{'N' if south >= 0 else 'S'}{abs(south):02d}{'E' if west >= 0 else 'W'}{abs(west):03d}"


def _tiles_for(bbox: BBox) -> list[str]:
    west, south, east, north = bbox
    names: list[str] = []
    for lat in range(int(math.floor(south / 3.0)) * 3, int(math.floor(north / 3.0)) * 3 + 1, 3):
        for lon in range(int(math.floor(west / 3.0)) * 3, int(math.floor(east / 3.0)) * 3 + 1, 3):
            name = tile_name(lat + 0.5, lon + 0.5)
            if name not in names:
                names.append(name)
    return names


def _tile_in_extent(name: str) -> bool:
    south = int(name[1:3]) * (1 if name[0] == "N" else -1)
    return _LAT_RANGE[0] <= south <= _LAT_RANGE[1]


def _load_index() -> None:
    global _index_loaded_from
    path = CACHE_DIR / "tile_index.json"
    if _index_loaded_from == path:
        return
    _index.clear()
    try:
        _index.update({str(k): bool(v) for k, v in json.loads(path.read_text()).items()})
    except (OSError, ValueError, AttributeError):
        pass
    _index_loaded_from = path


def _save_index() -> None:
    path = CACHE_DIR / "tile_index.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    tmp.write_text(json.dumps(_index, sort_keys=True))
    os.replace(tmp, path)


def _tile_exists(name: str) -> bool:
    """Whether a tile is published. Open-ocean tiles are simply absent (HTTP 404).

    The answer is cached on disk. Any outcome other than a clear yes or no
    raises ``LandcoverUnavailable`` so that a network fault is never mistaken
    for open ocean.
    """
    if not _tile_in_extent(name):
        return False
    with _index_lock:
        _load_index()
        if name in _index:
            return _index[name]
    last = "no attempt"
    for attempt in range(_RETRIES):
        if attempt:
            time.sleep(1.5 * attempt)
        try:
            resp = requests.head(TILE_URL.format(tile=name), timeout=_TIMEOUT,
                                 headers={"User-Agent": config.USER_AGENT})
        except requests.RequestException as exc:
            last = type(exc).__name__
            continue
        if resp.status_code in (HTTPStatus.OK, HTTPStatus.NOT_FOUND):
            exists = resp.status_code == HTTPStatus.OK
            with _index_lock:
                _load_index()
                _index[name] = exists
                _save_index()
            return exists
        last = f"HTTP {resp.status_code}"
        if resp.status_code < HTTPStatus.INTERNAL_SERVER_ERROR:
            break
    raise LandcoverUnavailable(f"WorldCover tile {name} could not be checked ({last})")


# --------------------------------------------------------------------------
# Raster access
# --------------------------------------------------------------------------

def _read_classes(grid: io.Grid) -> tuple[np.ndarray, list[str], list[str]]:
    """WorldCover codes on ``grid`` as uint8 (0 = no data), tiles read, tiles absent."""
    key = hashlib.sha1(json.dumps(
        [grid.crs, list(grid.transform)[:6], grid.width, grid.height]).encode()).hexdigest()[:20]
    cache_file = CACHE_DIR / "raster" / f"{key}.npz"
    if cache_file.exists():
        try:
            with np.load(cache_file, allow_pickle=False) as data:
                return (data["classes"], [str(t) for t in data["tiles"]],
                        [str(t) for t in data["missing"]])
        except (OSError, ValueError, KeyError):
            cache_file.unlink(missing_ok=True)
    classes = np.zeros(grid.shape, dtype="uint8")
    tiles: list[str] = []
    missing: list[str] = []
    for name in _tiles_for(grid.bbox_wgs84()):
        if not _tile_exists(name):
            missing.append(name)
            continue
        try:
            arr = io.read_to_grid(TILE_URL.format(tile=name), grid,
                                  resampling=Resampling.nearest, retries=_RETRIES)
        except Exception as exc:
            raise LandcoverUnavailable(f"WorldCover tile {name} unreadable: {str(exc)[:160]}") from exc
        ok = np.isfinite(arr) & (arr > 0) & (arr <= 255)
        classes[ok] = arr[ok].astype("uint8")
        tiles.append(name)
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    tmp = cache_file.with_name(f"{key}.{os.getpid()}.{threading.get_ident()}.tmp.npz")
    np.savez_compressed(tmp, classes=classes, tiles=np.array(tiles, dtype=str),
                        missing=np.array(missing, dtype=str))
    os.replace(tmp, cache_file)
    return classes, tiles, missing


def landcover_raster(grid: io.Grid) -> np.ndarray:
    """WorldCover class codes on ``grid`` as uint8, nearest-neighbour sampled.

    0 means no data: outside the map, or a tile that does not exist (open
    ocean). Raises ``LandcoverUnavailable`` when a tile cannot be read.
    """
    return _read_classes(grid)[0]


def fractions_from_classes(classes: np.ndarray, mask: np.ndarray | None = None) -> dict[str, float]:
    """Share of each class among the (masked) pixels; keys are ``FRACTION_KEYS``.

    Fractions sum to 1. An empty selection is reported as all ``nodata``.
    """
    values = classes[mask] if mask is not None else classes.ravel()
    if values.size == 0:
        return {**{name: 0.0 for name in CLASS_NAMES.values()}, "nodata": 1.0}
    counts = np.bincount(values.astype("uint8", copy=False).ravel(), minlength=256)
    out = {name: float(counts[code]) / values.size for code, name in CLASS_NAMES.items()}
    out["nodata"] = max(0.0, 1.0 - sum(out.values()))
    return out


def _validate(lat: float, lon: float, radius_m: float = 1.0) -> None:
    if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError(f"invalid coordinates lat={lat!r} lon={lon!r}")
    if not (math.isfinite(radius_m) and 0 < radius_m <= MAX_RADIUS_M):
        raise ValueError(f"radius must be in (0, {MAX_RADIUS_M:.0f}] m, got {radius_m!r}")


def _disc(lat: float, lon: float, radius_m: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, io.Grid]:
    """Classes, disc mask and pixel-centre distances (m) around a point."""
    _validate(lat, lon, radius_m)
    res = 10.0 if radius_m <= 10_000 else 20.0 if radius_m <= 20_000 else 40.0
    grid = io.make_grid(io.point_bbox(lat, lon, radius_m + 2 * res), res=res)
    classes = _read_classes(grid)[0]
    col, row = grid.lonlat_to_xy(lon, lat)
    yy, xx = np.ogrid[:grid.height, :grid.width]
    dist = (np.hypot(xx + 0.5 - col, yy + 0.5 - row) * res).astype("float32")
    mask = dist <= radius_m
    if not mask.any():
        mask[np.unravel_index(int(np.argmin(dist)), dist.shape)] = True
    return classes, mask, dist, grid


def landcover_fractions(lat: float, lon: float, radius_m: float) -> dict[str, float]:
    """Land-cover class fractions within ``radius_m`` of a point (WorldCover 2021).

    Keys: tree, shrub, grass, cropland, builtup, bare, snow, water, wetland,
    mangrove, moss, nodata; values sum to 1. ``nodata`` covers unmapped pixels
    and tiles that do not exist (open ocean, or beyond 60S-84N). Raises
    ``LandcoverUnavailable`` when a tile cannot be read and ``ValueError`` on
    invalid input (radius is limited to 50 km).
    """
    classes, mask, _, _ = _disc(lat, lon, radius_m)
    return fractions_from_classes(classes, mask)


def _builtup_stats(classes: np.ndarray, mask: np.ndarray, dist: np.ndarray) -> dict[str, Any]:
    built_all = classes == BUILTUP
    built = built_all & mask
    n = int(mask.sum())
    labels, _ = ndimage.label(built_all, structure=np.ones((3, 3), dtype=bool))
    sizes = np.bincount(labels.ravel())
    big = sizes >= MIN_CLUSTER_PX
    big[0] = False
    cluster = big[labels] & mask
    half_pixel = float(dist.min()) if dist.size else 0.0

    def nearest(sel: np.ndarray) -> float | None:
        if not sel.any():
            return None
        d = float(dist[sel].min())
        return 0.0 if d <= half_pixel + 1e-3 else round(d, 1)  # the point's own pixel

    return {"builtup_fraction": float(built.sum()) / n if n else 0.0,
            "builtup_pixels": int(built.sum()),
            "nearest_builtup_m": nearest(built),
            "nearest_builtup_cluster_m": nearest(cluster),
            "nodata_fraction": float((classes[mask] == 0).sum()) / n if n else 1.0}


def builtup_within(lat: float, lon: float, radius_m: float) -> dict[str, Any]:
    """Built-up land around a point, for remoteness and night-light interpretation.

    Returns ``builtup_fraction`` (share of the disc), ``builtup_pixels``,
    ``nearest_builtup_m`` (distance to the nearest built-up pixel centre, 0 if
    the point is on one, None if there is none within ``radius_m``),
    ``nearest_builtup_cluster_m`` (same, ignoring groups of fewer than 5
    connected pixels, which are often misclassified rock), ``nodata_fraction``,
    ``radius_m`` and ``pixel_m``. Raises like ``landcover_fractions``.
    """
    classes, mask, dist, grid = _disc(lat, lon, radius_m)
    return {**_builtup_stats(classes, mask, dist), "radius_m": float(radius_m),
            "pixel_m": grid.res, "map_year": MAP_YEAR}


# --------------------------------------------------------------------------
# Check
# --------------------------------------------------------------------------

def _map_predates_onset(absent_until: str | None, present_from: str | None) -> bool | None:
    """True if the feature was still absent when the map year ended, False if it
    was already present, None when the dates straddle the map year or are unknown."""
    year_end = f"{MAP_YEAR}-12-31"
    if absent_until and str(absent_until)[:10] >= year_end:
        return True
    if present_from and str(present_from)[:10] <= year_end:
        return False
    return None


def evaluate_landcover(footprint: dict[str, float], context: dict[str, float],
                       absent_until: str | None = None,
                       present_from: str | None = None) -> tuple[CheckStatus, str, dict[str, Any]]:
    """Decide the check from class fractions. Pure: no network.

    ``footprint`` and ``context`` are fraction dicts for the candidate and the
    ring around it. Returns status, detail and extra evidence. Built-up land
    explains only when the map predates the onset or the ring holds a
    settlement, because a 2021 map can show the candidate structure itself.
    """
    nodata = footprint.get("nodata", 0.0)
    if nodata > MAJORITY:
        return ("not_run", f"WorldCover has no data for {nodata:.0%} of the footprint "
                "(open ocean, or outside the mapped area).", {"explained_by": None})
    valid = max(1.0 - nodata, 1e-9)
    share = {k: footprint.get(k, 0.0) / valid for k in CLASS_NAMES.values()}
    context_valid = max(1.0 - context.get("nodata", 0.0), 1e-9)
    context_built = context.get("builtup", 0.0) / context_valid
    predates = _map_predates_onset(absent_until, present_from)
    timing = {True: f"the {MAP_YEAR} map predates the onset, so it shows the site before the change",
              False: f"the {MAP_YEAR} map postdates the onset, so it may show the change itself",
              None: f"onset is undated or straddles {MAP_YEAR}, so the map may show either state"}[predates]
    crop = share["cropland"]
    wet = share["water"] + share["wetland"] + share["mangrove"]
    built = share["builtup"]
    built_counts = predates is True or context_built >= SETTLEMENT_CONTEXT
    dominant = max(share, key=lambda k: share[k])
    extra: dict[str, Any] = {"map_predates_onset": predates, "dominant": dominant,
                             "context_builtup": round(context_built, 4), "explained_by": None}
    if crop >= MAJORITY:
        extra["explained_by"] = "cropland"
        return ("explains", f"Footprint is {crop:.0%} cropland: ordinary agricultural change "
                f"(ploughing, harvest, irrigation); {timing}.", extra)
    if wet >= MAJORITY:
        extra["explained_by"] = "water"
        return ("explains", f"Footprint is {wet:.0%} permanent water or wetland: water-level "
                f"or shoreline change; {timing}.", extra)
    if built >= MAJORITY and built_counts:
        extra["explained_by"] = "builtup"
        return ("explains", f"Footprint is {built:.0%} built-up with {context_built:.0%} built-up "
                f"in the surrounding {CONTEXT_M:.0f} m: ordinary development; {timing}.", extra)
    mundane = crop + wet + (built if built_counts else 0.0)
    if mundane >= MAJORITY:
        extra["explained_by"] = "mixed"
        return ("explains", f"Footprint is {mundane:.0%} cropland, water or settlement "
                f"(cropland {crop:.0%}, water/wetland {wet:.0%}, built-up {built:.0%}): "
                f"ordinary land-use change; {timing}.", extra)
    note = ""
    if built >= MAJORITY:
        note = (f" The footprint is {built:.0%} built-up but only {context_built:.0%} of the "
                f"surrounding {CONTEXT_M:.0f} m is, and the map does not predate the onset, so "
                "it may be showing the candidate itself: not counted as an explanation.")
    return ("does_not_explain", f"Footprint is mostly {dominant} ({share[dominant]:.0%}); "
            f"cropland {crop:.0%}, built-up {built:.0%}, water/wetland {wet:.0%}; {timing}.{note}",
            extra)


def _footprint_bbox(candidate: Candidate) -> tuple[BBox, str]:
    lat, lon = float(candidate.lat), float(candidate.lon)
    try:
        west, south, east, north = (float(v) for v in candidate.bbox)
        ok = (all(math.isfinite(v) for v in (west, south, east, north))
              and west < east and south < north
              and east - west <= _MAX_FOOTPRINT_DEG and north - south <= _MAX_FOOTPRINT_DEG
              and west - 0.01 <= lon <= east + 0.01 and south - 0.01 <= lat <= north + 0.01)
    except (TypeError, ValueError):
        ok = False
    if ok:
        return (west, south, east, north), "bbox"
    area = float(candidate.area_m2) if candidate.area_m2 else 0.0
    radius = math.sqrt(area / math.pi) if math.isfinite(area) and area > 0 else 0.0
    return io.point_bbox(lat, lon, min(max(radius, 15.0), 10_000.0)), "area_disc"


def _rect_mask(grid: io.Grid, bbox: BBox, lat: float, lon: float) -> np.ndarray:
    """Pixels of ``grid`` inside a WGS84 box; never fewer than 3 x 3 around the centre."""
    west, south, east, north = bbox
    corners = [grid.lonlat_to_xy(x, y) for x in (west, east) for y in (south, north)]
    cols = [c for c, _ in corners]
    rows = [r for _, r in corners]
    cc, rc = grid.lonlat_to_xy(lon, lat)
    c0 = min(int(math.floor(min(cols))), int(math.floor(cc)) - 1)
    c1 = max(int(math.ceil(max(cols))), int(math.floor(cc)) + 2)
    r0 = min(int(math.floor(min(rows))), int(math.floor(rc)) - 1)
    r1 = max(int(math.ceil(max(rows))), int(math.floor(rc)) + 2)
    mask = np.zeros(grid.shape, dtype=bool)
    mask[max(r0, 0):max(r1, 0), max(c0, 0):max(c1, 0)] = True
    return mask


def check_landcover(candidate: Candidate) -> list[CheckResult]:
    """Test whether ordinary land cover explains a candidate.

    Returns one ``CheckResult`` named ``"landcover"``: ``explains`` when the
    footprint is mostly cropland, permanent water or wetland, or built-up
    land inside a settlement (see ``evaluate_landcover`` for the 2021 map
    caveat); ``does_not_explain`` otherwise, with the class fractions in
    ``evidence``; ``not_run`` when WorldCover cannot be read or has no data.
    """
    evidence: dict[str, Any] = {"worldcover": f"v200 {MAP_YEAR}", "context_margin_m": CONTEXT_M}
    try:
        lat, lon = float(candidate.lat), float(candidate.lon)
        _validate(lat, lon)
        bbox, how = _footprint_bbox(candidate)
        margin = io.point_bbox(lat, lon, CONTEXT_M)
        dlon, dlat = (margin[2] - margin[0]) / 2, (margin[3] - margin[1]) / 2
        grid = io.make_grid((bbox[0] - dlon, bbox[1] - dlat, bbox[2] + dlon, bbox[3] + dlat))
        classes, tiles, missing = _read_classes(grid)
        mask = _rect_mask(grid, bbox, lat, lon)
        footprint = fractions_from_classes(classes, mask)
        context = fractions_from_classes(classes, ~mask)
        status, detail, extra = evaluate_landcover(footprint, context, candidate.absent_until,
                                                   candidate.present_from)
    except Exception as exc:  # a failed read must never read as "nothing ordinary here"
        reason = (str(exc) if isinstance(exc, (LandcoverUnavailable, ValueError))
                  else type(exc).__name__)
        evidence["error"] = type(exc).__name__
        return [CheckResult(CHECK_NAME, "natural", "not_run",
                            f"WorldCover could not be read: {reason}", SOURCE, evidence)]
    evidence.update({
        "footprint": {k: round(v, 4) for k, v in footprint.items()},
        "context": {k: round(v, 4) for k, v in context.items()},
        "footprint_pixels": int(mask.sum()), "footprint_source": how,
        "tiles": tiles, "missing_tiles": missing, **extra})
    if status == "not_run" and missing:
        detail += f" Tiles not published: {', '.join(missing)}."
    return [CheckResult(CHECK_NAME, "natural", status, detail, SOURCE, evidence)]
