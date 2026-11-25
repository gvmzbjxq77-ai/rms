"""Sentinel-1 radar evidence: sees through cloud and darkness, responds to metal.

The ground-range products used here are not terrain-corrected and not
radiometrically calibrated. Values are relative decibels (20*log10 of the
amplitude), compared only between scenes from the same relative orbit, where
the viewing geometry repeats. On steep ground positions can be off by tens to
hundreds of metres.

Millimetre ground-deformation measurement (interferometry) is NOT available:
see ``deformation_status``.
"""
from __future__ import annotations

import logging
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from typing import Any

import numpy as np
from pystac import Item
from scipy import ndimage

from ..core import io
from ..core.models import Candidate, Region

log = logging.getLogger(__name__)


def sar_scenes(bbox: io.BBox, start: str, end: str, max_items: int = 300) -> list[Item]:
    """Sentinel-1 IW ground-range scenes with VV over a box, oldest first."""
    items = io.stac_search("pc", "sentinel-1-grd", bbox, f"{start}/{end}",
                           query={"sar:instrument_mode": {"eq": "IW"}}, max_items=max_items)
    return sorted((it for it in items if "vv" in it.assets), key=lambda it: it.datetime)


def _orbit(item: Item) -> tuple[int, str]:
    return (int(item.properties.get("sat:relative_orbit", -1)),
            str(item.properties.get("sat:orbit_state", "")))


def _read_db(item: Item, grid: io.Grid, pol: str = "vv") -> np.ndarray | None:
    try:
        amplitude = io.read_to_grid(item.assets[pol].href, grid)
    except Exception as exc:
        log.debug("sar read failed: %r", exc)
        return None
    with np.errstate(divide="ignore", invalid="ignore"):
        db = 20.0 * np.log10(amplitude)
    db[~np.isfinite(db)] = np.nan
    return db.astype("float32")


def _spread(items: list[Item], count: int) -> list[Item]:
    if len(items) <= count:
        return items
    picks = np.unique(np.round(np.linspace(0, len(items) - 1, count)).astype(int))
    return [items[i] for i in picks]


def backscatter_stack(grid: io.Grid, start: str, end: str, pol: str = "vv",
                      relative_orbit: int | None = None, max_scenes: int = 12) -> dict[str, Any]:
    """Relative-dB scenes on the grid from one relative orbit (the most frequent by default)."""
    items = sar_scenes(grid.bbox_wgs84(), start, end)
    if not items:
        return {"arrays": [], "dates": [], "scene_ids": [], "relative_orbit": None, "orbit_state": None}
    if relative_orbit is None:
        relative_orbit = Counter(_orbit(it)[0] for it in items).most_common(1)[0][0]
    chosen = _spread([it for it in items if _orbit(it)[0] == relative_orbit], max_scenes)
    with ThreadPoolExecutor(3) as pool:
        arrays = list(pool.map(lambda it: _read_db(it, grid, pol), chosen))
    keep = [(a, it) for a, it in zip(arrays, chosen) if a is not None and np.isfinite(a).mean() > 0.3]
    return {"arrays": [a for a, _ in keep],
            "dates": [it.datetime.strftime("%Y-%m-%d") for _, it in keep],
            "scene_ids": [it.id for _, it in keep], "relative_orbit": relative_orbit,
            "orbit_state": _orbit(chosen[0])[1] if chosen else None}


def confirm(candidate: Candidate, scenes_per_side: int = 5) -> dict[str, Any]:
    """Does radar backscatter inside the footprint shift across the onset?

    Uses up to ``scenes_per_side`` scenes from the 240 days before
    ``absent_until`` and after ``present_from``, all from the one relative orbit
    with most coverage of both periods. The inside-minus-ring contrast in dB
    must shift by at least 1 dB and three times the scene-to-scene noise; then
    "radar_s1" is appended to ``candidate.sensors``. Footprints under about
    40 m radius cannot be tested. Evidence is stored under
    ``candidate.measurements["sar"]`` and returned. Never raises.
    """
    result: dict[str, Any] = {"status": "not_run"}
    candidate.measurements["sar"] = result
    if not (candidate.absent_until and candidate.present_from):
        result["reason"] = "candidate has no onset window"
        return result
    radius = float(np.sqrt(max(candidate.area_m2, 1.0) / np.pi))
    if radius < 40:
        result["reason"] = f"footprint radius {radius:.0f} m is under two radar pixels"
        return result
    try:
        before_end = datetime.fromisoformat(candidate.absent_until).date()
        after_start = datetime.fromisoformat(candidate.present_from).date()
        grid = io.make_grid(io.point_bbox(candidate.lat, candidate.lon, max(4.5 * radius, 500.0)), 20.0)
        box = grid.bbox_wgs84()
        before_items = sar_scenes(box, (before_end - timedelta(days=240)).isoformat(), before_end.isoformat())
        after_end = min(after_start + timedelta(days=240), date.today())
        after_items = sar_scenes(box, after_start.isoformat(), after_end.isoformat())
        shared = Counter(_orbit(it) for it in before_items) & Counter(_orbit(it) for it in after_items)
        if not shared:
            result["reason"] = (f"no relative orbit covers both periods "
                                f"({len(before_items)} scenes before, {len(after_items)} after)")
            return result
        orbit = shared.most_common(1)[0][0]
        before_items = _spread([it for it in before_items if _orbit(it) == orbit], scenes_per_side)
        after_items = _spread([it for it in after_items if _orbit(it) == orbit], scenes_per_side)
        col, row = grid.lonlat_to_xy(candidate.lon, candidate.lat)
        yy, xx = np.mgrid[:grid.height, :grid.width]
        dist = np.hypot(xx + 0.5 - col, yy + 0.5 - row) * grid.res
        inside, ring = dist <= radius, (dist >= 2 * radius) & (dist <= 4 * radius)

        def contrast(item: Item) -> dict[str, Any] | None:
            db = _read_db(item, grid)
            if db is None or np.isfinite(db[inside]).mean() < 0.8:
                return None
            return {"date": item.datetime.strftime("%Y-%m-%d"), "scene_id": item.id,
                    "contrast_db": float(np.nanmean(db[inside]) - np.nanmean(db[ring]))}

        with ThreadPoolExecutor(3) as pool:
            before = [r for r in pool.map(contrast, before_items) if r]
            after = [r for r in pool.map(contrast, after_items) if r]
    except Exception as exc:
        result["reason"] = f"{type(exc).__name__}: {str(exc)[:160]}"
        return result
    if len(before) < 2 or len(after) < 2:
        result["reason"] = f"too few usable radar scenes ({len(before)} before, {len(after)} after)"
        return result
    b = np.array([r["contrast_db"] for r in before])
    a = np.array([r["contrast_db"] for r in after])
    shift = float(np.median(a) - np.median(b))
    noise = float((np.median(np.abs(b - np.median(b))) + np.median(np.abs(a - np.median(a)))) * 1.4826 / 2)
    confirmed = abs(shift) >= max(1.0, 3 * noise)
    result.update({"status": "ok", "relative_orbit": orbit[0], "orbit_state": orbit[1],
                   "before": before, "after": after, "shift_db": shift, "noise_db": noise,
                   "confirmed": bool(confirmed), "footprint_radius_m": radius})
    if confirmed and "radar_s1" not in candidate.sensors:
        candidate.sensors.append("radar_s1")
    return result


def detect_bright_scatterers(region: Region, start: str, end: str, res: float = 20.0,
                             z_threshold: float = 8.0, max_scenes: int = 8,
                             max_candidates: int = 60) -> list[Candidate]:
    """Persistent, compact, very bright radar targets in otherwise dark terrain.

    The temporal median of several same-orbit scenes is compared with a local
    background (median within about 1 km). Compact blobs (at most 25 pixels)
    whose brightness exceeds the background by ``z_threshold`` robust sigmas
    become candidates (signature "installation", detector "sar_bright").
    Steep slopes are excluded when terrain data is available, because slopes
    facing the radar are bright for purely geometric reasons.
    """
    grid = io.make_grid(region.bbox, res)
    stack = backscatter_stack(grid, start, end, max_scenes=max_scenes)
    if len(stack["arrays"]) < 4:
        log.warning("%s: only %d radar scenes; skipped", region.id, len(stack["arrays"]))
        return []
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        median = np.nanmedian(np.stack(stack["arrays"]), axis=0)
    ok = np.isfinite(median)
    filled = np.where(ok, median, np.nanmedian(median))
    background = ndimage.median_filter(filled, size=max(3, int(round(1000.0 / res)) | 1))
    excess = np.where(ok, median - background, np.nan)
    mad = float(np.nanmedian(np.abs(excess - np.nanmedian(excess))) * 1.4826)
    z = excess / max(mad, 0.3)
    mask = np.nan_to_num(z, nan=0.0) >= z_threshold
    slope = None
    try:
        from .terrain import slope_aspect
        slope = slope_aspect(grid)[0]
        mask &= ~(slope > 12)
    except Exception as exc:
        log.info("no terrain for slope masking: %r", exc)
    labels, _ = ndimage.label(mask, structure=np.ones((3, 3), int))
    candidates: list[Candidate] = []
    for index, box in enumerate(ndimage.find_objects(labels), start=1):
        blob = labels[box] == index
        if not 1 <= blob.sum() <= 25:
            continue
        rows, cols = np.nonzero(blob)
        lon, lat = grid.xy_to_lonlat(box[1].start + cols.mean(), box[0].start + rows.mean())
        w, n = grid.xy_to_lonlat(box[1].start - 2.5, box[0].start - 2.5)
        e, s = grid.xy_to_lonlat(box[1].stop + 1.5, box[0].stop + 1.5)
        peak = float(np.nanmax(z[box][blob]))
        candidates.append(Candidate(
            id="", region_id=region.id, lat=lat, lon=lon,
            bbox=(min(w, e), min(s, n), max(w, e), max(s, n)), signature="installation",
            detector="sar_bright", score=float(min(1.0, peak / 30.0)),
            area_m2=float(blob.sum() * res ** 2), sensors=["radar_s1"],
            measurements={"median_db": float(np.nanmax(median[box][blob])),
                          "background_db": float(np.nanmedian(background[box][blob])),
                          "z": peak, "n_scenes": len(stack["arrays"]),
                          "relative_orbit": stack["relative_orbit"], "dates": stack["dates"],
                          "slope_deg": float(np.nanmax(slope[box][blob])) if slope is not None else None}))
    candidates.sort(key=lambda c: -c.score)
    if len(candidates) > max_candidates:
        log.warning("%s: %d radar candidates, %d dropped by the cap", region.id,
                    len(candidates), len(candidates) - max_candidates)
        candidates = candidates[:max_candidates]
    for n, candidate in enumerate(candidates, start=1):
        candidate.id = f"SW-{region.id}-SB{n:04d}"
    return candidates


def deformation_status() -> dict[str, str]:
    """Why ground-deformation measurement was not run (it is never faked)."""
    return {"status": "not_run",
            "reason": ("Millimetre ground deformation needs radar interferometry on single-look "
                       "complex products or ready-made displacement products. Both require a "
                       "data-provider login that this environment does not have.")}
