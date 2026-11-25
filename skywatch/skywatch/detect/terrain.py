"""Terrain from the Copernicus 30 m DEM: slope, cast shadow, closed depressions.

The DEM is a supporting sensor. It explains optical false alarms (terrain
shadow), describes the ground under a candidate (flat pad, pit, ridge) and
finds crater-like closed depressions. It was built from 2011-2015 radar data,
so it is blind to anything newer: see ``DEM_CAVEAT``.
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
from typing import Any

import numpy as np
from scipy import ndimage
from skimage.morphology import reconstruction

from ..core import config, io
from ..core.io import Grid
from ..core.models import Candidate, Region

log = logging.getLogger(__name__)

DEM_COLLECTION = "cop-dem-glo-30"
#: Native ground sampling of the DEM; finer grids only interpolate it.
DEM_RES_M = 30.0
DEM_CAVEAT = ("Copernicus GLO-30 DEM: 30 m posting from TanDEM-X radar acquired 2011-2015. "
              "Features created after that are absent, features removed since are still "
              "present, water bodies are flattened, and pits narrower than about 90 m or "
              "shallower than about 2-3 m are not resolved.")

#: Depth below the spill level at which a pixel counts as inside a depression.
MIN_DEPRESSION_DEPTH_M = 2.0
#: A candidate depression must be at least this deep at its deepest point ...
MIN_CANDIDATE_DEPTH_M = 3.0
#: ... and at least this deep relative to its equivalent diameter.
MIN_DEPTH_DIAMETER_RATIO = 0.015
#: Minimum circularity (area / area of the centroid-centred enclosing circle).
MIN_CIRCULARITY = 0.45
#: ``flatness_anomaly``: surroundings must slope at least this much (degrees) ...
FLATNESS_MIN_SURROUND_SLOPE_DEG = 3.0
#: ... and the footprint's median slope must be below this fraction of it.
FLATNESS_MAX_RATIO = 0.4

_EIGHT = np.ones((3, 3), dtype=bool)


# --------------------------------------------------------------------------
# DEM access
# --------------------------------------------------------------------------

def _grid_key(grid: Grid) -> str:
    raw = json.dumps([grid.crs, list(grid.transform)[:6], grid.width, grid.height])
    return hashlib.sha1(raw.encode()).hexdigest()[:20]


def dem(grid: Grid) -> np.ndarray:
    """Copernicus DEM elevation (metres, float32) on ``grid``; NaN where missing.

    Mosaics every 1-degree tile touching the grid (first non-NaN wins) and
    caches the result on disk. Open sea has no tiles and stays NaN. Raises
    ``RuntimeError`` when the catalogue or every tile read fails, so a network
    failure is never mistaken for "no terrain data here".
    """
    cache_file = config.CACHE / "terrain" / f"dem_{_grid_key(grid)}.npz"
    if cache_file.exists():
        with np.load(cache_file, allow_pickle=False) as data:
            return data["dem"].astype("float32")
    items = io.stac_search("pc", DEM_COLLECTION, grid.bbox_wgs84(), max_items=40)
    hrefs = sorted({item.assets["data"].href for item in items if "data" in item.assets})
    out = np.full(grid.shape, np.nan, dtype="float32")
    complete = True
    if hrefs:
        tiles = io.read_many(hrefs, grid)
        if all(tile is None for tile in tiles):
            raise RuntimeError(f"all {len(hrefs)} Copernicus DEM tile reads failed")
        for tile in tiles:
            if tile is None:
                complete = False
                continue
            fill = np.isnan(out) & np.isfinite(tile)
            out[fill] = tile[fill]
    if complete:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(cache_file, dem=out)
    else:
        log.warning("some DEM tiles failed to read; mosaic not cached")
    return out


# --------------------------------------------------------------------------
# Slope, aspect, cast shadow
# --------------------------------------------------------------------------

def _slope_aspect(z: np.ndarray, res: float) -> tuple[np.ndarray, np.ndarray]:
    """Slope and aspect (degrees) of an elevation array with square pixels."""
    if min(z.shape) < 2:
        nan = np.full(z.shape, np.nan, dtype="float32")
        return nan, nan.copy()
    d_row, d_col = np.gradient(z.astype("float64"), res)
    d_east, d_north = d_col, -d_row
    slope = np.degrees(np.arctan(np.hypot(d_east, d_north)))
    aspect = np.degrees(np.arctan2(-d_east, -d_north)) % 360.0
    aspect[~(slope > 0.01)] = np.nan
    return slope.astype("float32"), aspect.astype("float32")


def slope_aspect(grid: Grid) -> tuple[np.ndarray, np.ndarray]:
    """Slope (degrees from horizontal) and aspect on ``grid``.

    Aspect is the downslope direction in degrees clockwise from north
    (90 = east-facing); it is NaN on flat ground. Both are NaN where the DEM
    is missing.
    """
    return _slope_aspect(dem(grid), grid.res)


def _cast_shadow(z: np.ndarray, res: float, sun_azimuth_deg: float,
                 sun_elevation_deg: float) -> np.ndarray:
    """Pixels whose line of sight to the sun is blocked by terrain in ``z``."""
    finite = np.isfinite(z)
    if not finite.any():
        return np.zeros(z.shape, dtype=bool)
    if sun_elevation_deg <= 0.0:
        return finite.copy()
    if sun_elevation_deg >= 90.0:
        return np.zeros(z.shape, dtype=bool)
    height, width = z.shape
    surface = np.where(finite, z, -np.inf).astype("float32")
    relief = float(np.nanmax(z) - np.nanmin(z))
    tan_e = math.tan(math.radians(sun_elevation_deg))
    d_col = math.sin(math.radians(sun_azimuth_deg))
    d_row = -math.cos(math.radians(sun_azimuth_deg))
    step = max(1.0, 20.0 / res)                       # pixels per march step
    # Beyond this distance the ray is above the highest terrain in the grid.
    n_steps = int(min(math.ceil(relief / (res * tan_e) / step), math.hypot(height, width) / step))
    shadow = np.zeros(z.shape, dtype=bool)
    for k in range(1, n_steps + 1):
        dist = k * step
        dc, dr = int(round(dist * d_col)), int(round(dist * d_row))
        if abs(dc) >= width or abs(dr) >= height:
            break
        r0, r1 = max(0, -dr), height - max(0, dr)
        c0, c1 = max(0, -dc), width - max(0, dc)
        blocker = surface[r0 + dr:r1 + dr, c0 + dc:c1 + dc]
        shadow[r0:r1, c0:c1] |= blocker > surface[r0:r1, c0:c1] + np.float32(dist * res * tan_e)
    return shadow & finite


def hillshade_shadow(grid: Grid, sun_azimuth_deg: float, sun_elevation_deg: float) -> np.ndarray:
    """Boolean mask of terrain-cast shadow on ``grid`` for one sun position.

    Marches from every pixel towards the sun (azimuth clockwise from north,
    elevation above the horizon) and marks it shadowed when DEM terrain rises
    above the ray. Terrain outside the grid cannot cast shadow into it, so pad
    the grid when high ground lies sunward. DEM-missing pixels are False.
    """
    return _cast_shadow(dem(grid), grid.res, sun_azimuth_deg, sun_elevation_deg)


# --------------------------------------------------------------------------
# Depressions
# --------------------------------------------------------------------------

def _fill_depressions(z: np.ndarray) -> np.ndarray:
    """Raise every closed depression to its spill level (grid edge and NaN drain)."""
    finite = np.isfinite(z)
    if not finite.any() or min(z.shape) < 3:
        return z.astype("float32", copy=True)
    low = float(np.nanmin(z)) - 1.0
    ground = np.where(finite, z, low).astype("float64")
    seed = np.full(z.shape, float(np.nanmax(z)), dtype="float64")
    seed[0, :], seed[-1, :] = ground[0, :], ground[-1, :]
    seed[:, 0], seed[:, -1] = ground[:, 0], ground[:, -1]
    seed[~finite] = low
    filled = reconstruction(seed, ground, method="erosion").astype("float32")
    filled[~finite] = np.nan
    return filled


def _local_depth(z: np.ndarray, res: float, scale_m: float) -> np.ndarray:
    """Depth (m) below the local spill level, for depressions up to ``scale_m`` wide.

    Filling is done in overlapping tiles of ``2 * scale_m`` whose edges drain,
    and the deepest result per pixel is kept. A pit on the floor of a much
    larger closed basin is therefore measured against the floor around it
    instead of being swallowed by the basin.
    """
    stride = max(int(math.ceil(scale_m / res)), 8)
    tile = 2 * stride
    height, width = z.shape
    if height <= tile and width <= tile:
        return np.nan_to_num(_fill_depressions(z) - z, nan=0.0).astype("float32")
    depth = np.zeros(z.shape, dtype="float32")
    for r0 in range(0, max(height - stride, 1), stride):
        for c0 in range(0, max(width - stride, 1), stride):
            sub = z[r0:r0 + tile, c0:c0 + tile]
            part = np.nan_to_num(_fill_depressions(sub) - sub, nan=0.0)
            view = depth[r0:r0 + tile, c0:c0 + tile]
            np.maximum(view, part, out=view)
    return depth


def _circularity(component: np.ndarray, res: float) -> float:
    """Area over the area of the centroid-centred enclosing circle (1 = disc)."""
    rows, cols = np.nonzero(component)
    if rows.size == 0:
        return 0.0
    r_max = float(np.hypot(rows - rows.mean(), cols - cols.mean()).max()) + 0.5
    return float(min(1.0, rows.size / (math.pi * r_max ** 2)))


def _rim_height(z: np.ndarray, component: np.ndarray, res: float) -> float | None:
    """Height (m) of the ground just outside a depression above the plain beyond.

    Clearly positive for a raised rim (impact and explosion craters, tuff
    rings, spoil-ringed pits); about zero for a plain sinkhole.
    """
    rows, cols = np.nonzero(component)
    if rows.size == 0:
        return None
    radius_px = math.sqrt(rows.size / math.pi)
    grow = max(1, int(round(0.2 * radius_px)))
    near = ndimage.binary_dilation(component, structure=_EIGHT, iterations=grow) & ~component
    rr, cc = np.indices(z.shape)
    dist = np.hypot(rr - rows.mean(), cc - cols.mean())
    far = (dist > 1.8 * radius_px + grow) & (dist <= 2.8 * radius_px + grow) & ~component
    near &= np.isfinite(z)
    far &= np.isfinite(z)
    if near.sum() < 4 or far.sum() < 10:
        return None
    return float(np.percentile(z[near], 75) - np.median(z[far]))


def _find_depressions(z: np.ndarray, res: float, min_diameter_m: float,
                      max_diameter_m: float) -> list[dict[str, Any]]:
    """Closed depressions in ``z`` within a diameter range, best score first."""
    if not np.isfinite(z).any() or min(z.shape) < 3:
        return []
    depth = _local_depth(z, res, max_diameter_m)
    labels, count = ndimage.label(depth >= MIN_DEPRESSION_DEPTH_M, structure=_EIGHT)
    if count == 0:
        return []
    index = np.arange(1, count + 1)
    area_px = np.bincount(labels.ravel(), minlength=count + 1)[1:]
    diameter = 2.0 * np.sqrt(area_px * res * res / math.pi)
    deepest = ndimage.maximum(depth, labels, index)
    keep = ((diameter >= min_diameter_m) & (diameter <= max_diameter_m)
            & (deepest >= np.maximum(MIN_CANDIDATE_DEPTH_M, MIN_DEPTH_DIAMETER_RATIO * diameter)))
    slices = ndimage.find_objects(labels)
    slope, _ = _slope_aspect(z, res)
    found: list[dict[str, Any]] = []
    for lab in index[keep]:
        window = slices[lab - 1]
        pad = int(math.ceil(3.2 * diameter[lab - 1] / 2.0 / res)) + 2
        r0, r1 = max(window[0].start - pad, 0), min(window[0].stop + pad, z.shape[0])
        c0, c1 = max(window[1].start - pad, 0), min(window[1].stop + pad, z.shape[1])
        comp = labels[r0:r1, c0:c1] == lab
        circ = _circularity(comp, res)
        if circ < MIN_CIRCULARITY:
            continue
        sub = z[r0:r1, c0:c1]
        rows, cols = np.nonzero(comp)
        depth_m = float(deepest[lab - 1])
        diam = float(diameter[lab - 1])
        ratio = depth_m / diam
        rim = _rim_height(sub, comp, res)
        rim_term = min(1.0, max(rim or 0.0, 0.0) / (0.04 * diam))
        score = 0.45 * circ + 0.35 * min(1.0, ratio / 0.12) + 0.20 * rim_term
        found.append({
            "row": float(rows.mean()) + r0, "col": float(cols.mean()) + c0,
            "row_min": int(rows.min()) + r0, "row_max": int(rows.max()) + r0,
            "col_min": int(cols.min()) + c0, "col_max": int(cols.max()) + c0,
            "area_m2": float(rows.size * res * res), "diameter_m": diam,
            "depth_m": depth_m, "depth_diameter_ratio": ratio, "circularity": circ,
            "rim_height_m": rim, "floor_elevation_m": float(np.nanmin(sub[comp])),
            "wall_slope_max_deg": float(np.nanmax(slope[r0:r1, c0:c1][comp])),
            "score": float(min(1.0, score)),
        })
    found.sort(key=lambda d: d["score"], reverse=True)
    return found


def detect_closed_depressions(region: Region, min_diameter_m: float = 150.0,
                              max_diameter_m: float = 3000.0,
                              max_candidates: int = 100) -> list[Candidate]:
    """Circular closed depressions and rimmed pits in the DEM of a region.

    A depression is ground below its local spill level (depression filling in
    tiles of twice ``max_diameter_m``). Kept when its equivalent diameter is in
    range, it is at least 3 m deep and 1.5 % of its diameter deep, and its
    circularity is at least 0.45. Candidates carry detector
    ``"dem_depression"``, sensors ``["terrain_dem"]`` and signature
    ``"crash"`` purely as a triage label: most are sinkholes, volcanic
    craters, kettles, mines and reservoirs, which is for the elimination
    engine to say. Returns ``[]`` (with a logged warning) when the DEM cannot
    be read; the DEM's 2011-2015 date means newer pits are never found.
    """
    west, south, east, north = region.bbox
    mid_lat = (south + north) / 2.0
    pad_lat = (max_diameter_m / 2.0 + 300.0) / 111_320.0
    pad_lon = pad_lat / max(math.cos(math.radians(mid_lat)), 0.05)
    grid = io.make_grid((west - pad_lon, south - pad_lat, east + pad_lon, north + pad_lat),
                        res=DEM_RES_M)
    try:
        z = dem(grid)
    except Exception as exc:
        log.warning("dem_depression: DEM unavailable for region %s: %r", region.id, exc)
        return []
    candidates: list[Candidate] = []
    for dep in _find_depressions(z, grid.res, min_diameter_m, max_diameter_m):
        lon, lat = grid.xy_to_lonlat(dep["col"] - 0.5, dep["row"] - 0.5)
        if not (west <= lon <= east and south <= lat <= north):
            continue
        lon_a, lat_a = grid.xy_to_lonlat(dep["col_min"] - 0.5, dep["row_max"] + 0.5)
        lon_b, lat_b = grid.xy_to_lonlat(dep["col_max"] + 0.5, dep["row_min"] - 0.5)
        rim = dep["rim_height_m"]
        candidates.append(Candidate(
            id=f"SW-{region.id}-DD{len(candidates) + 1:04d}", region_id=region.id,
            lat=lat, lon=lon,
            bbox=(min(lon_a, lon_b), min(lat_a, lat_b), max(lon_a, lon_b), max(lat_a, lat_b)),
            signature="crash", detector="dem_depression", score=round(dep["score"], 4),
            area_m2=dep["area_m2"], sensors=["terrain_dem"],
            shape={"circularity": round(dep["circularity"], 3),
                   "equivalent_diameter_m": round(dep["diameter_m"], 1)},
            measurements={"depth_m": round(dep["depth_m"], 1),
                          "depth_diameter_ratio": round(dep["depth_diameter_ratio"], 4),
                          "rim_height_m": None if rim is None else round(rim, 1),
                          "floor_elevation_m": round(dep["floor_elevation_m"], 1),
                          "wall_slope_max_deg": round(dep["wall_slope_max_deg"], 1),
                          "dem_resolution_m": DEM_RES_M},
            notes="Closed depression in the DEM; 'crash' is a triage label only. " + DEM_CAVEAT))
        if len(candidates) >= max_candidates:
            break
    return candidates


# --------------------------------------------------------------------------
# Point context
# --------------------------------------------------------------------------

def _context_from_dem(z: np.ndarray, res: float, row: float, col: float,
                      radius_m: float) -> dict[str, Any]:
    """Terrain statistics around fractional pixel (``col``, ``row``) of ``z``."""
    rr, cc = np.indices(z.shape)
    dist = np.hypot(rr + 0.5 - row, cc + 0.5 - col) * res
    finite = np.isfinite(z)
    foot = dist <= radius_m
    if not foot.any():
        foot = dist <= dist.min()
    foot &= finite
    if not foot.any():
        return {"status": "not_available",
                "reason": "the DEM has no data at this place (open water or outside coverage)"}
    surround = (dist > radius_m) & (dist <= 3.0 * radius_m) & finite
    slope, _ = _slope_aspect(z, res)
    centre = np.unravel_index(int(np.argmin(np.where(foot, dist, np.inf))), z.shape)
    zf = z[foot].astype("float64")
    # Roughness: RMS height about the best-fit plane, so a tilted smooth pad is smooth.
    design = np.column_stack([rr[foot] * res, cc[foot] * res, np.ones(zf.size)])
    if zf.size >= 4:
        coef, *_ = np.linalg.lstsq(design, zf, rcond=None)
        roughness = float(np.sqrt(np.mean((zf - design @ coef) ** 2)))
    else:
        roughness = float(zf.std())
    slope_med = float(np.nanmedian(slope[foot])) if np.isfinite(slope[foot]).any() else None
    slope_max = float(np.nanmax(slope[foot])) if np.isfinite(slope[foot]).any() else None
    surround_slope = (float(np.nanmedian(slope[surround]))
                      if surround.any() and np.isfinite(slope[surround]).any() else None)
    ratio = (slope_med / surround_slope
             if slope_med is not None and surround_slope and surround_slope > 0 else None)
    out: dict[str, Any] = {
        "status": "ok", "reason": "",
        "elevation_m": float(z[centre]),
        "slope_deg": slope_med, "slope_max_deg": slope_max,
        "local_relief_m": float(zf.max() - zf.min()),
        "tpi": float(zf.mean() - z[surround].mean()) if surround.any() else None,
        "roughness": roughness,
        "surround_slope_deg": surround_slope, "flatness_ratio": ratio,
        "flatness_anomaly": bool(ratio is not None and surround_slope is not None
                                 and surround_slope >= FLATNESS_MIN_SURROUND_SLOPE_DEG
                                 and ratio <= FLATNESS_MAX_RATIO),
        "depression_depth_m": 0.0, "depression_circularity": None,
        "depression_diameter_m": None, "depression_rim_height_m": None,
        "depression_depth_at_point_m": 0.0,
    }
    depth = np.nan_to_num(_fill_depressions(z) - z, nan=0.0)
    labels, count = ndimage.label(depth >= MIN_DEPRESSION_DEPTH_M, structure=_EIGHT)
    if count:
        inside = np.bincount(labels[foot], minlength=count + 1)
        inside[0] = 0
        # The footprint "sits in" a depression when its centre is inside one or
        # a depression covers at least a tenth of it; pick the deepest such.
        eligible = [lab for lab in np.nonzero(inside)[0]
                    if lab == labels[centre] or inside[lab] >= 0.1 * foot.sum()]
        if eligible:
            deepest = ndimage.maximum(depth, labels, eligible)
            lab = eligible[int(np.argmax(deepest))]
            comp = labels == lab
            out.update(
                depression_depth_m=float(np.max(deepest)),
                depression_circularity=_circularity(comp, res),
                depression_diameter_m=float(2.0 * math.sqrt(comp.sum() * res * res / math.pi)),
                depression_rim_height_m=_rim_height(z, comp, res),
                depression_depth_at_point_m=float(depth[centre]))
    return out


def terrain_context(lat: float, lon: float, radius_m: float = 500.0) -> dict[str, Any]:
    """Describe the terrain under a footprint of ``radius_m`` around a point.

    Keys: ``status`` ("ok" or "not_available", with ``reason``),
    ``elevation_m`` (at the point), ``slope_deg`` (footprint median),
    ``slope_max_deg``, ``local_relief_m`` (max minus min in the footprint),
    ``tpi`` (footprint mean elevation minus the mean of the ring out to three
    radii; negative = hollow), ``roughness`` (RMS metres about the best-fit
    plane), ``surround_slope_deg``, ``flatness_ratio`` and
    ``flatness_anomaly`` (pad-like: surroundings slope at least 3 degrees and
    the footprint under 0.4 of that), ``depression_depth_m`` (deepest point
    below the spill level of the closed depression the footprint sits in,
    else 0.0), ``depression_circularity`` (0..1, else None),
    ``depression_diameter_m``, ``depression_rim_height_m``,
    ``depression_depth_at_point_m``, ``dem_caveat``, ``dem_source``,
    ``resolution_m`` and ``window_half_size_m``. Depressions wider than the
    analysis window (``max(4 * radius_m, radius_m + 1500)`` either side) are
    not recognised. When the DEM cannot be read every measurement is None
    and ``status`` is "not_available": never read that as "flat ground".
    """
    half = max(4.0 * radius_m, radius_m + 1500.0)
    out: dict[str, Any] = {
        "status": "not_available", "reason": "", "lat": lat, "lon": lon, "radius_m": radius_m,
        "elevation_m": None, "slope_deg": None, "slope_max_deg": None, "local_relief_m": None,
        "tpi": None, "roughness": None, "surround_slope_deg": None, "flatness_ratio": None,
        "flatness_anomaly": None, "depression_depth_m": None, "depression_circularity": None,
        "depression_diameter_m": None, "depression_rim_height_m": None,
        "depression_depth_at_point_m": None, "dem_caveat": DEM_CAVEAT,
        "dem_source": f"Planetary Computer {DEM_COLLECTION}", "resolution_m": DEM_RES_M,
        "window_half_size_m": half,
    }
    try:
        grid = io.make_grid(io.point_bbox(lat, lon, half), res=DEM_RES_M)
        z = dem(grid)
        col, row = grid.lonlat_to_xy(lon, lat)
    except Exception as exc:
        out["reason"] = f"DEM could not be read: {exc!r}"[:300]
        return out
    out.update(_context_from_dem(z, grid.res, row, col, radius_m))
    return out
