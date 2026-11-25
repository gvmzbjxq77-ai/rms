"""Landsat 8/9 evidence: an optical and thermal instrument independent of Sentinel-2.

Used two ways: ``confirm`` asks whether Landsat independently sees a change
found elsewhere, and ``detect_thermal_anomalies`` looks for places that stay
hotter or colder than their surroundings across seasons and years.

Thermal data is natively 100 m (delivered resampled to 30 m); nothing here
resolves objects smaller than that.
"""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from typing import Any

import numpy as np
from pystac import Item
from rasterio.enums import Resampling
from scipy import ndimage

from ..core import io
from ..core.models import Candidate, Region

log = logging.getLogger(__name__)

_QA_BAD = 0b111111           # fill, dilated cloud, cirrus, cloud, shadow, snow
_OPTICAL = ("blue", "green", "red", "nir08", "swir22")


def landsat_scenes(bbox: io.BBox, start: str, end: str, max_cloud: float = 20.0,
                   max_items: int = 200) -> list[Item]:
    """Landsat 8/9 Collection 2 Level 2 scenes over a box, oldest first."""
    items = io.stac_search("pc", "landsat-c2-l2", bbox, f"{start}/{end}",
                           query={"eo:cloud_cover": {"lt": max_cloud},
                                  "platform": {"in": ["landsat-8", "landsat-9"]}},
                           max_items=max_items)
    return sorted(items, key=lambda it: it.datetime)


def _spread(items: list[Item], count: int) -> list[Item]:
    if len(items) <= count:
        return items
    picks = np.unique(np.round(np.linspace(0, len(items) - 1, count)).astype(int))
    return [items[i] for i in picks]


def read_scene(item: Item, grid: io.Grid, thermal: bool = True,
               optical: bool = True) -> dict[str, np.ndarray]:
    """One scene on the grid: reflectance bands, ``kelvin`` and a ``valid`` mask."""
    names = (list(_OPTICAL) if optical else []) + (["lwir11"] if thermal else [])
    hrefs = [item.assets[n].href for n in names] + [item.assets["qa_pixel"].href]
    with ThreadPoolExecutor(6) as pool:
        arrays = list(pool.map(
            lambda pair: io.read_to_grid(pair[0], grid, resampling=pair[1]),
            [(h, Resampling.bilinear) for h in hrefs[:-1]] + [(hrefs[-1], Resampling.nearest)]))
    qa = arrays[-1]
    bad = np.isnan(qa) | ((np.nan_to_num(qa).astype("uint16") & _QA_BAD) > 0)
    out: dict[str, np.ndarray] = {}
    for name, arr in zip(names, arrays[:-1]):
        value = arr * 0.00341802 + 149.0 if name == "lwir11" else arr * 0.0000275 - 0.2
        value[bad | np.isnan(arr) | (arr == 0)] = np.nan
        out["kelvin" if name == "lwir11" else name] = value.astype("float32")
    out["valid"] = ~bad
    return out


def _masks(grid: io.Grid, lat: float, lon: float, radius: float) -> tuple[np.ndarray, np.ndarray]:
    col, row = grid.lonlat_to_xy(lon, lat)
    yy, xx = np.mgrid[:grid.height, :grid.width]
    dist = np.hypot(xx + 0.5 - col, yy + 0.5 - row) * grid.res
    return dist <= radius, (dist >= 2 * radius) & (dist <= 4 * radius)


def _contrasts(items: list[Item], grid: io.Grid, inside: np.ndarray,
               ring: np.ndarray) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in items:
        try:
            scene = read_scene(item, grid)
        except Exception as exc:
            log.debug("landsat read failed: %r", exc)
            continue
        if scene["valid"][inside].mean() < 0.6 or scene["valid"][ring].mean() < 0.4:
            continue
        with np.errstate(divide="ignore", invalid="ignore"):
            feats = {
                "brightness": (scene["blue"] + scene["green"] + scene["red"]) / 3,
                "ndvi": (scene["nir08"] - scene["red"]) / (scene["nir08"] + scene["red"]),
                "nbr": (scene["nir08"] - scene["swir22"]) / (scene["nir08"] + scene["swir22"]),
                "kelvin": scene["kelvin"],
            }
        row: dict[str, Any] = {"date": item.datetime.strftime("%Y-%m-%d"), "scene_id": item.id}
        for name, arr in feats.items():
            row[name] = float(np.nanmean(arr[inside]) - np.nanmean(arr[ring]))
        rows.append(row)
    return rows


def _shift(before: list[float], after: list[float]) -> tuple[float, float]:
    b, a = np.array(before), np.array(after)
    shift = float(np.median(a) - np.median(b))
    noise = float((np.median(np.abs(b - np.median(b))) + np.median(np.abs(a - np.median(a)))) * 1.4826 / 2)
    return shift, noise


def confirm(candidate: Candidate, scenes_per_side: int = 4) -> dict[str, Any]:
    """Does Landsat independently see the candidate's change, with the same timing?

    Compares inside-minus-ring contrast in up to ``scenes_per_side`` clear
    scenes from the year before ``absent_until`` with scenes from the year
    after ``present_from``. Optical confirmation needs the shift to exceed
    three times the scene-to-scene noise and a quarter of the detector's
    minimum step, with the sign Sentinel-2 saw; then "optical_landsat" is appended to
    ``candidate.sensors``. Thermal confirmation needs a footprint of at least
    60 m radius and a shift of at least 1 K and three times the noise; then
    "thermal_landsat" is appended. The evidence is stored under
    ``candidate.measurements["landsat"]`` and returned. Never raises.
    """
    m = candidate.measurements
    result: dict[str, Any] = {"status": "not_run"}
    m["landsat"] = result
    if not (candidate.absent_until and candidate.present_from):
        result["reason"] = "candidate has no onset window"
        return result
    radius = float(np.sqrt(max(candidate.area_m2, 1.0) / np.pi))
    if radius < 30:
        result["reason"] = f"footprint radius {radius:.0f} m is below one Landsat pixel"
        return result
    try:
        before_end = datetime.fromisoformat(candidate.absent_until).date()
        after_start = datetime.fromisoformat(candidate.present_from).date()
        grid = io.make_grid(io.point_bbox(candidate.lat, candidate.lon, max(4.5 * radius, 600.0)), 30.0)
        inside, ring = _masks(grid, candidate.lat, candidate.lon, radius)
        box = grid.bbox_wgs84()
        before_items = _spread(landsat_scenes(box, (before_end - timedelta(days=400)).isoformat(),
                                              before_end.isoformat()), scenes_per_side)
        after_end = min(after_start + timedelta(days=400), date.today())
        after_items = _spread(landsat_scenes(box, after_start.isoformat(), after_end.isoformat()),
                              scenes_per_side)
        before = _contrasts(before_items, grid, inside, ring)
        after = _contrasts(after_items, grid, inside, ring)
    except Exception as exc:
        result["reason"] = f"{type(exc).__name__}: {str(exc)[:160]}"
        return result
    if len(before) < 2 or len(after) < 2:
        result["reason"] = f"too few clear Landsat scenes ({len(before)} before, {len(after)} after)"
        return result
    result.update({"status": "ok", "before": before, "after": after, "footprint_radius_m": radius})
    steps = {"brightness": float(m.get("d_brightness", 0.0) or 0.0),
             "ndvi": float(m.get("d_ndvi", 0.0) or 0.0), "nbr": float(m.get("d_nbr", 0.0) or 0.0)}
    scale = {"brightness": 0.03, "ndvi": 0.08, "nbr": 0.08}
    main = max(steps, key=lambda key: abs(steps[key]) / scale[key])
    shift, noise = _shift([r[main] for r in before], [r[main] for r in after])
    optical_ok = (abs(shift) >= max(3 * noise, 0.25 * scale[main])
                  and (steps[main] == 0 or np.sign(shift) == np.sign(steps[main])))
    result["optical"] = {"feature": main, "shift": shift, "noise": noise,
                         "sentinel2_step": steps[main], "confirmed": bool(optical_ok)}
    if optical_ok and "optical_landsat" not in candidate.sensors:
        candidate.sensors.append("optical_landsat")
    if radius >= 60:
        t_shift, t_noise = _shift([r["kelvin"] for r in before], [r["kelvin"] for r in after])
        thermal_ok = abs(t_shift) >= max(1.0, 3 * t_noise)
        result["thermal"] = {"shift_K": t_shift, "noise_K": t_noise, "confirmed": bool(thermal_ok)}
        if thermal_ok and "thermal_landsat" not in candidate.sensors:
            candidate.sensors.append("thermal_landsat")
    else:
        result["thermal"] = {"confirmed": False,
                             "reason": f"footprint radius {radius:.0f} m is below thermal resolution"}
    return result


def detect_thermal_anomalies(region: Region, start: str = "2019-01-01", end: str | None = None,
                             res: float = 90.0, min_scenes: int = 8, z_threshold: float = 3.5,
                             max_scenes: int = 14, max_candidates: int = 60,
                             min_anomaly_k: float = 2.5,
                             diagnostics: dict[str, Any] | None = None) -> list[Candidate]:
    """Places that stay hotter or colder than their surroundings, scene after scene.

    For each clear scene the temperature that surface brightness, vegetation
    and (when the terrain module is available) elevation predict is removed,
    the local background (median within about 2 km) is subtracted and the
    result is scaled to robust z-scores. A pixel is anomalous when |z| >=
    ``z_threshold`` with the same sign in at least 70 % of the scenes in which
    it is clear and its typical anomaly is at least ``min_anomaly_k`` kelvin,
    across at least two years and both halves of the year. Open water
    (NDWI > 0.1) and snow are masked. All scenes are daytime, so differences
    in how rock and sand store heat still produce ordinary anomalies.
    Candidates have signature "thermal" and detector "landsat_thermal".
    """
    end = end or date.today().isoformat()
    grid = io.make_grid(region.bbox, res)
    items = _spread(landsat_scenes(grid.bbox_wgs84(), start, end, max_cloud=15.0, max_items=400), max_scenes)
    elevation = None
    try:
        from .terrain import dem
        elevation = dem(grid)
    except Exception as exc:
        log.info("no terrain for thermal detrending: %r", exc)
    window = max(3, int(round(4000.0 / res)) | 1)
    zs: list[np.ndarray] = []
    anomalies: list[np.ndarray] = []
    dates: list[str] = []
    for item in items:
        try:
            scene = read_scene(item, grid)
        except Exception:
            continue
        kelvin = scene["kelvin"]
        with np.errstate(divide="ignore", invalid="ignore"):
            ndwi = (scene["green"] - scene["nir08"]) / (scene["green"] + scene["nir08"])
        kelvin[ndwi > 0.1] = np.nan
        ok = np.isfinite(kelvin)
        if ok.mean() < 0.5:
            continue
        # Remove what ordinary surface properties predict: darker and barer
        # ground is hotter by day, higher ground is cooler.
        with np.errstate(divide="ignore", invalid="ignore"):
            albedo = (scene["blue"] + scene["green"] + scene["red"] + scene["nir08"]) / 4
            ndvi = (scene["nir08"] - scene["red"]) / (scene["nir08"] + scene["red"])
        predictors = [albedo, ndvi] + ([elevation] if elevation is not None else [])
        good = ok & np.all([np.isfinite(p) for p in predictors], axis=0)
        if good.sum() > 200:
            design = np.column_stack([p[good] for p in predictors] + [np.ones(int(good.sum()))])
            coeffs, *_ = np.linalg.lstsq(design, kelvin[good], rcond=None)
            model = sum(c * p for c, p in zip(coeffs[:-1], predictors)) + coeffs[-1]
            kelvin = np.where(good, kelvin - model, np.nan)
            ok = good
        filled = np.where(ok, kelvin, np.nanmedian(kelvin))
        background = ndimage.median_filter(filled, size=window)
        anomaly = np.where(ok, kelvin - background, np.nan)
        mad = np.nanmedian(np.abs(anomaly - np.nanmedian(anomaly))) * 1.4826
        zs.append((anomaly / max(float(mad), 0.05)).astype("float32"))
        anomalies.append(anomaly.astype("float32"))
        dates.append(item.datetime.strftime("%Y-%m-%d"))
    if diagnostics is not None:
        diagnostics.update({"grid": grid, "dates": dates, "n_scenes": len(dates)})
    if len(dates) < min_scenes:
        log.warning("%s: only %d clear thermal scenes; skipped", region.id, len(dates))
        return []
    z = np.stack(zs)
    seen = np.isfinite(z).sum(axis=0)
    years = {d[:4] for d in dates}
    halves = {int(d[5:7]) in (4, 5, 6, 7, 8, 9) for d in dates}
    if len(years) < 2 or len(halves) < 2:
        log.warning("%s: thermal scenes do not span two years and both half-years", region.id)
        return []
    candidates: list[Candidate] = []
    with np.errstate(invalid="ignore"):
        for sign in (1, -1):
            hits = (np.nan_to_num(z * sign, nan=0.0) >= z_threshold).sum(axis=0)
            typical = np.nanmedian(np.stack(anomalies), axis=0) * sign
            mask = (seen >= min_scenes) & (hits >= 0.7 * seen) & (typical >= min_anomaly_k)
            labels, count = ndimage.label(mask, structure=np.ones((3, 3), int))
            for index, box in enumerate(ndimage.find_objects(labels), start=1):
                blob = labels[box] == index
                if blob.sum() < 2:
                    continue
                rows, cols = np.nonzero(blob)
                lon, lat = grid.xy_to_lonlat(box[1].start + cols.mean(), box[0].start + rows.mean())
                w, n = grid.xy_to_lonlat(box[1].start - 1.5, box[0].start - 1.5)
                e, s = grid.xy_to_lonlat(box[1].stop + 0.5, box[0].stop + 0.5)
                sub_z = z[(slice(None),) + box][:, blob]
                sub_a = np.stack(anomalies)[(slice(None),) + box][:, blob]
                median_z = float(np.nanmedian(sub_z))
                candidates.append(Candidate(
                    id="", region_id=region.id, lat=lat, lon=lon,
                    bbox=(min(w, e), min(s, n), max(w, e), max(s, n)),
                    signature="thermal", detector="landsat_thermal",
                    score=float(min(1.0, abs(median_z) / 12.0)), area_m2=float(blob.sum() * res ** 2),
                    sensors=["thermal_landsat"],
                    measurements={"median_anomaly_K": float(np.nanmedian(sub_a)),
                                  "median_z": median_z,
                                  "hit_fraction": float(np.median((hits / np.maximum(seen, 1))[box][blob])),
                                  "n_scenes": len(dates), "sign": sign, "dates": dates,
                                  "years": sorted(years), "res_m": res,
                                  "elevation_detrended": elevation is not None,
                                  "surface_detrended": True}))
    candidates.sort(key=lambda c: -c.score * np.log10(max(c.area_m2, 100.0)))
    if len(candidates) > max_candidates:
        log.warning("%s: %d thermal candidates, %d dropped by the cap", region.id,
                    len(candidates), len(candidates) - max_candidates)
        candidates = candidates[:max_candidates]
    for n, candidate in enumerate(candidates, start=1):
        candidate.id = f"SW-{region.id}-TH{n:04d}"
    return candidates
