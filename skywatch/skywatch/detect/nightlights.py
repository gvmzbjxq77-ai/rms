"""Night-light evidence: persistent artificial light where no settlement is mapped.

Data: the World Bank "Light Every Night" archive (public bucket
``globalnightlight.s3.amazonaws.com``). The archive holds nightly VIIRS DNB
swaths (130-300 MB each, several thousand per month, no spatial index) and,
under ``composites/``, global *monthly cloud-free average radiance* mosaics
with a matching count of cloud-free nights. This module uses the monthly
composites: one small window read per month instead of a search through
hundreds of swaths per night.

What a composite value is: the mean DNB radiance (nW/cm2/sr) of the nights
of one month that passed the producer's filters, on a 15 arc-second grid
(about 463 m at the equator). The grid oversamples the sensor: the real DNB
footprint is about 750 m and bright sources bloom over neighbouring pixels,
so a light cannot be located better than roughly 1 km.

Filtered by the producer before averaging: cloud (VIIRS cloud mask), sunlit
and moonlit data, lightning and, in the ``slexcl`` products used here by
preference, nights affected by stray light (``slcorr`` products, used only
where ``slexcl`` has no observation, keep those nights after a correction).
NOT filtered: fires and gas flares, aurora, fishing boats, snow-brightened
background. Requiring light in most of the sampled months removes
short-lived fires; it does not remove flares, which are installations.

Every period reported by this module is therefore one month, not one night:
``max_nights`` caps the number of monthly composites read and the number of
cloud-free nights behind them is reported separately.
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import time
import warnings
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import rasterio
import requests
from affine import Affine
from rasterio.windows import Window
from scipy import ndimage

from ..core import config
from ..core.models import BBox, Candidate, CheckResult, Region

logger = logging.getLogger(__name__)

BUCKET = "https://globalnightlight.s3.amazonaws.com"
SOURCE = ("World Bank Light Every Night archive, VIIRS DNB monthly cloud-free "
          "composites (globalnightlight.s3.amazonaws.com/composites)")
UNITS = "nW/cm2/sr"
#: Real ground footprint of one VIIRS DNB pixel, metres.
RESOLUTION_M = 750.0
#: Latitudes covered by the composites (south, north).
COVERAGE_LAT = (-65.0, 75.0)
FILTERS = {
    "applied_by_producer": ["cloud", "sunlit", "moonlit", "lightning",
                            "stray light (excluded, or corrected where flagged)"],
    "not_filtered": ["fires and gas flares", "aurora", "boats", "snow-brightened background"],
}

#: A month counts as lit when the footprint peak exceeds the ring median by
#: max(MIN_EXCESS, K_SIGMA * ring sigma), or reaches ABSOLUTE_LIT outright
#: (so a site inside a uniformly lit area is still reported as lit).
MIN_EXCESS = 1.0
K_SIGMA = 5.0
ABSOLUTE_LIT = 5.0
#: Light is persistent when at least this share of the usable months is lit.
MIN_LIT_FRACTION = 2.0 / 3.0
#: Fewer usable months than this: persistence is not judged (None).
MIN_MONTHS = 3
#: A month needs this many cloud-free nights over the footprint to be used.
MIN_CLEAR_NIGHTS = 2
#: Background ring: starts RING_GAP_M outside the footprint, RING_WIDTH_M wide.
RING_GAP_M = 3000.0
RING_WIDTH_M = 5000.0
#: A source is "isolated" when mapped built-up land covers less than this
#: share of the disc around it.
ISOLATED_MAX_BUILTUP = 0.01

_CACHE: Path = config.CACHE / "nightlights"
_INVENTORY_TTL_S = 7 * 86400
_THREADS = 8
_REGION_MARGIN_M = 12_000.0
_REGION_MAX_PX = 2400
_BLOCK_PX = 24
_NAME = re.compile(r"composites/[^/]+/DNB_(npp|j01)_(\d{8})-(\d{8})_global_(vcm|ecm)-?"
                   r"(slexcl|slcorr|slcfg|cfg)_v10_(\w+?)\.(avg_rade9|n_cf)\.tif$")
_STRAY = {"slexcl": "excluded", "cfg": "excluded", "slcorr": "corrected", "slcfg": "corrected"}
_memo: dict[str, Any] = {}


class ArchiveError(RuntimeError):
    """The archive could not be listed or read."""


@dataclass(frozen=True)
class Composite:
    """One monthly composite: average radiance and cloud-free night count."""

    month: str       # YYYYMM
    start: str       # YYYYMMDD
    end: str         # YYYYMMDD
    satellite: str   # "npp" (Suomi NPP) or "j01" (NOAA-20)
    stray_light: str  # "excluded" or "corrected"
    avg_key: str
    ncf_key: str


# --------------------------------------------------------------------------
# Inventory
# --------------------------------------------------------------------------

def _fetch_keys(retries: int = 3) -> list[str]:
    """List every object under ``composites/`` (one or two small requests)."""
    keys: list[str] = []
    token: str | None = None
    while True:
        params = {"list-type": "2", "prefix": "composites/", "max-keys": "1000"}
        if token:
            params["continuation-token"] = token
        last: Exception | None = None
        text = ""
        for attempt in range(retries):
            try:
                resp = requests.get(BUCKET + "/", params=params, timeout=30,
                                    headers={"User-Agent": config.USER_AGENT})
                resp.raise_for_status()
                text = resp.text
                last = None
                break
            except Exception as exc:
                last = exc
                time.sleep(1.5 * (attempt + 1))
        if last is not None:
            raise ArchiveError(f"listing failed: {type(last).__name__}: {last}")
        keys += re.findall(r"<Key>([^<]+)</Key>", text)
        more = re.search(r"<NextContinuationToken>([^<]+)</NextContinuationToken>", text)
        if not more:
            return keys
        token = more.group(1)


def _parse_keys(keys: Sequence[str]) -> dict[str, list[Composite]]:
    """Group object keys into composites per month, best choice first.

    Order within a month: Suomi NPP before NOAA-20 (one consistent sensor
    over the whole series), stray-light-excluded before corrected. Products
    without both files are dropped.
    """
    parts: dict[tuple[str, str, str, str, str, str], dict[str, str]] = {}
    for key in keys:
        match = _NAME.search(key)
        if not match:
            continue
        sat, start, end, mask, stray, run, kind = match.groups()
        parts.setdefault((sat, start, end, mask, _STRAY[stray], run), {})[kind] = key
    out: dict[str, list[Composite]] = {}
    for (sat, start, end, _mask, stray, _run), files in parts.items():
        if "avg_rade9" in files and "n_cf" in files:
            out.setdefault(start[:6], []).append(
                Composite(start[:6], start, end, sat, stray, files["avg_rade9"], files["n_cf"]))
    for month in out:
        out[month].sort(key=lambda c: (c.satellite != "npp", c.stray_light != "excluded", c.avg_key))
    return dict(sorted(out.items()))


def _inventory() -> dict[str, list[Composite]]:
    """Composites per month, from memory, the disk cache or the bucket.

    A stale disk cache is used when the bucket cannot be listed; with no
    cache at all the failure is raised as ``ArchiveError``.
    """
    if "inventory" in _memo:
        return _memo["inventory"]
    path = _CACHE / "inventory.json"
    cached: list[str] | None = None
    age = math.inf
    if path.exists():
        try:
            raw = json.loads(path.read_text())
            cached, age = list(raw["keys"]), time.time() - float(raw["fetched"])
        except Exception:
            cached = None
    if cached is None or age > _INVENTORY_TTL_S:
        try:
            keys = _fetch_keys()
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(f".{os.getpid()}.tmp")
            tmp.write_text(json.dumps({"fetched": time.time(), "keys": keys}))
            os.replace(tmp, path)
            cached = keys
        except ArchiveError:
            if cached is None:
                raise
            logger.warning("night-light inventory refresh failed; using cached listing")
    inventory = _parse_keys(cached)
    if not inventory:
        raise ArchiveError("no monthly composites found in the archive listing")
    _memo["inventory"] = inventory
    return inventory


def available_months() -> list[str]:
    """Months (YYYYMM) with a monthly composite. Raises ``ArchiveError``."""
    return list(_inventory())


def archive_end() -> str:
    """ISO date of the last night covered by a composite. Raises ``ArchiveError``."""
    end = max(c.end for comps in _inventory().values() for c in comps)
    return f"{end[:4]}-{end[4:6]}-{end[6:]}"


def _norm_month(text: str) -> str:
    digits = re.sub(r"\D", "", str(text))
    return digits[:6]


def _iso(day: str) -> str:
    return f"{day[:4]}-{day[4:6]}-{day[6:]}"


# --------------------------------------------------------------------------
# Pixel access
# --------------------------------------------------------------------------

def _read_window(key: str, bbox: BBox, retries: int = 2) -> tuple[np.ndarray, Affine]:
    """Native pixels of one archive raster inside ``bbox`` and their transform.

    The window is clipped to the raster; an empty intersection raises
    ``ValueError``, a failed read ``ArchiveError``. Results are cached.
    """
    tag = hashlib.sha1((key + "|" + "|".join(f"{v:.6f}" for v in bbox)).encode()).hexdigest()[:24]
    path = _CACHE / "win" / f"{tag}.npz"
    if path.exists():
        try:
            with np.load(path, allow_pickle=False) as data:
                return data["a"], Affine(*[float(v) for v in data["t"]])
        except Exception:
            path.unlink(missing_ok=True)
    west, south, east, north = bbox
    last: Exception | None = None
    for attempt in range(retries):
        try:
            with rasterio.open(f"{BUCKET}/{key}") as src:
                inv = ~src.transform
                c0, r0 = inv * (west, north)
                c1, r1 = inv * (east, south)
                col0, row0 = max(0, math.floor(c0)), max(0, math.floor(r0))
                col1, row1 = min(src.width, math.ceil(c1)), min(src.height, math.ceil(r1))
                if col1 <= col0 or row1 <= row0:
                    raise ValueError("bbox is outside the composite grid")
                window = Window(col0, row0, col1 - col0, row1 - row0)
                arr = src.read(1, window=window)
                transform = src.window_transform(window)
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(f".{os.getpid()}.{time.monotonic_ns()}.tmp")
            with tmp.open("wb") as handle:
                np.savez_compressed(handle, a=arr, t=np.array(list(transform)[:6], dtype="float64"))
            os.replace(tmp, path)
            return arr, transform
        except ValueError:
            raise
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise ArchiveError(f"read failed: {key}: {type(last).__name__}: {last}")


def _read_pair(comp: Composite, bbox: BBox) -> tuple[np.ndarray, np.ndarray, Affine]:
    """Radiance (NaN where no cloud-free night) and night count for one month."""
    avg, transform = _read_window(comp.avg_key, bbox)
    ncf, _ = _read_window(comp.ncf_key, bbox)
    if avg.shape != ncf.shape:
        raise ArchiveError(f"radiance and night-count grids differ for {comp.month}")
    nights = ncf.astype("float32")
    radiance = avg.astype("float32")
    radiance[~(nights > 0) | ~np.isfinite(radiance)] = np.nan
    return radiance, nights, transform


def _pixel_metres(transform: Affine, shape: tuple[int, int], lat: float,
                  lon: float) -> tuple[np.ndarray, np.ndarray]:
    """East and north offsets (m) of every pixel centre from a point."""
    rows, cols = np.indices(shape, dtype="float32")
    lons = transform.c + (cols + 0.5) * transform.a
    lats = transform.f + (rows + 0.5) * transform.e
    dx = (lons - lon) * 111_320.0 * max(math.cos(math.radians(lat)), 0.05)
    dy = (lats - lat) * 110_574.0
    return dx, dy


# --------------------------------------------------------------------------
# Point statistics
# --------------------------------------------------------------------------

def _ring(radius_m: float) -> tuple[float, float, float]:
    """Effective footprint radius and background-ring inner and outer radii."""
    footprint = max(float(radius_m), RESOLUTION_M)
    inner = footprint + RING_GAP_M
    return footprint, inner, inner + RING_WIDTH_M


def _point_stats(radiance: np.ndarray, nights: np.ndarray, transform: Affine, lat: float,
                 lon: float, radius_m: float) -> dict[str, Any] | None:
    """Footprint and background-ring statistics for one month.

    ``radiance`` holds NaN where no cloud-free night exists. Returns None
    when the month cannot be used: no pixel under the footprint, fewer than
    ``MIN_CLEAR_NIGHTS`` nights over it, or too little ring to estimate the
    background.
    """
    if radiance.size == 0:
        return None
    footprint_r, inner, outer = _ring(radius_m)
    dx, dy = _pixel_metres(transform, radiance.shape, lat, lon)
    dist = np.hypot(dx, dy)
    foot = dist <= footprint_r
    if not foot.any():
        return None
    ok = np.isfinite(radiance)
    foot_ok = foot & ok
    ring_ok = (dist >= inner) & (dist <= outer) & ok
    if foot_ok.sum() < max(1, 0.5 * foot.sum()) or ring_ok.sum() < 10:
        return None
    clear = float(np.median(nights[foot_ok]))
    if clear < MIN_CLEAR_NIGHTS:
        return None
    values = radiance[foot_ok]
    ring = radiance[ring_ok]
    background = float(np.median(ring))
    sigma = float(1.4826 * np.median(np.abs(ring - background)))
    peak = float(values.max())
    threshold = max(MIN_EXCESS, K_SIGMA * sigma)
    excess = peak - background
    return {
        "clear_nights": int(round(clear)),
        "footprint_mean": round(float(values.mean()), 3),
        "footprint_median": round(float(np.median(values)), 3),
        "footprint_max": round(peak, 3),
        "footprint_pixels": int(foot_ok.sum()),
        "background_median": round(background, 3),
        "background_sigma": round(sigma, 3),
        "background_pixels": int(ring_ok.sum()),
        "excess": round(excess, 3),
        "threshold": round(threshold, 3),
        "lit": bool(excess >= threshold or peak >= ABSOLUTE_LIT),
    }


def _persistence(lit: Sequence[bool]) -> bool | None:
    """True/False once ``MIN_MONTHS`` usable months exist, else None."""
    if len(lit) < MIN_MONTHS:
        return None
    return bool(sum(lit) >= math.ceil(MIN_LIT_FRACTION * len(lit) - 1e-9))


def _month_point(comps: Sequence[Composite], lat: float, lon: float, radius_m: float,
                 bbox: BBox) -> dict[str, Any]:
    """One month at a point: the preferred product, else the stray-light-corrected one."""
    period: dict[str, Any] = {"month": comps[0].month, "usable": False, "reason": ""}
    errors: list[str] = []
    tried: set[str] = set()
    for comp in comps:
        if comp.satellite + comp.stray_light in tried:
            continue
        tried.add(comp.satellite + comp.stray_light)
        try:
            radiance, nights, transform = _read_pair(comp, bbox)
        except ValueError:
            errors.append("outside the composite grid")
            continue
        except Exception as exc:
            errors.append(f"read failed ({type(exc).__name__})")
            period["read_failed"] = True
            continue
        stats = _point_stats(radiance, nights, transform, lat, lon, radius_m)
        if stats is None:
            errors.append(f"{comp.satellite}/{comp.stray_light}: too few cloud-free nights")
            continue
        period.update(stats)
        period.update({"usable": True, "dates": f"{_iso(comp.start)}/{_iso(comp.end)}",
                       "satellite": comp.satellite, "stray_light": comp.stray_light,
                       "files": [comp.avg_key, comp.ncf_key]})
        period.pop("read_failed", None)
        return period
    period["reason"] = "; ".join(errors)
    return period


def _unavailable(reason: str, lat: float, lon: float, radius_m: float) -> dict[str, Any]:
    return {"status": "not_available", "reason": reason, "lat": float(lat), "lon": float(lon),
            "radius_m": float(radius_m), "periods": [], "months_used": 0, "months_lit": 0,
            "clear_nights": 0, "persistent_light": None, "files": [], "units": UNITS,
            "resolution_m": RESOLUTION_M, "source": SOURCE}


def radiance_at(lat: float, lon: float, radius_m: float = 1500.0,
                months: Sequence[str] | None = None, max_nights: int = 12) -> dict[str, Any]:
    """Night-time radiance at a point from monthly VIIRS composites.

    ``months`` are ``"YYYYMM"`` (or ``"YYYY-MM"``) strings; by default the
    latest ``max_nights`` months in the archive. ``max_nights`` caps the
    number of monthly composites read (each is the mean of that month's
    cloud-free, moon-free nights). Never raises.

    Returns a dict with ``status`` (``"ok"`` or ``"not_available"``),
    ``reason``, ``periods`` (one dict per month: ``month``, ``usable``,
    ``reason``, ``dates``, ``satellite``, ``stray_light``, ``clear_nights``,
    ``footprint_mean/median/max``, ``background_median``,
    ``background_sigma``, ``excess``, ``threshold``, ``lit``, ``files``),
    ``months_used``, ``months_lit``, ``lit_fraction``, ``clear_nights``
    (total behind the used months), ``radiance`` / ``radiance_mean`` /
    ``background`` / ``excess`` (medians over used months, nW/cm2/sr),
    ``persistent_light`` (True, False, or None when fewer than
    ``MIN_MONTHS`` months were usable), ``threshold`` (the rule applied),
    ``files``, ``archive_end``, ``resolution_m`` and ``filters``.
    The footprint is never smaller than one sensor pixel (750 m radius).
    """
    try:
        return _radiance_at(float(lat), float(lon), float(radius_m), months, int(max_nights))
    except Exception as exc:  # contract: report, never raise
        logger.warning("radiance_at failed: %r", exc)
        return _unavailable(f"night-light lookup failed: {type(exc).__name__}: {exc}",
                            lat, lon, radius_m)


def _radiance_at(lat: float, lon: float, radius_m: float, months: Sequence[str] | None,
                 max_nights: int) -> dict[str, Any]:
    if not (math.isfinite(lat) and math.isfinite(lon)):
        return _unavailable("coordinates are not finite", lat, lon, radius_m)
    if not (COVERAGE_LAT[0] <= lat <= COVERAGE_LAT[1]):
        return _unavailable(f"latitude {lat:.3f} is outside the composite coverage "
                            f"({COVERAGE_LAT[0]:.0f} to {COVERAGE_LAT[1]:.0f})", lat, lon, radius_m)
    if max_nights < 1:
        return _unavailable("max_nights must be at least 1", lat, lon, radius_m)
    try:
        inventory = _inventory()
    except ArchiveError as exc:
        return _unavailable(f"archive unreachable: {exc}", lat, lon, radius_m)
    end = archive_end()
    first = next(iter(inventory))
    if months is None:
        chosen = list(inventory)[-max_nights:]
    else:
        wanted = sorted({_norm_month(m) for m in months})
        chosen = [m for m in wanted if m in inventory][-max_nights:]
        if not chosen:
            out = _unavailable(f"none of the requested months is in the archive "
                               f"(composites run {first[:4]}-{first[4:]} to {end})", lat, lon, radius_m)
            out["archive_end"] = end
            return out
    _footprint, _inner, outer = _ring(radius_m)
    dlat = (outer + 1000.0) / 110_574.0
    dlon = (outer + 1000.0) / (111_320.0 * max(math.cos(math.radians(lat)), 0.05))
    bbox: BBox = (lon - dlon, lat - dlat, lon + dlon, lat + dlat)
    with ThreadPoolExecutor(_THREADS) as pool:
        periods = list(pool.map(lambda m: _month_point(inventory[m], lat, lon, radius_m, bbox), chosen))
    used = [p for p in periods if p["usable"]]
    out = _unavailable("", lat, lon, radius_m)
    footprint, inner, outer = _ring(radius_m)
    out.update({
        "periods": periods, "archive_end": end, "months_requested": chosen,
        "footprint_radius_m": footprint, "background_ring_m": [inner, outer], "filters": FILTERS,
        "threshold": {"min_excess": MIN_EXCESS, "k_sigma": K_SIGMA, "absolute": ABSOLUTE_LIT,
                      "min_lit_fraction": round(MIN_LIT_FRACTION, 3), "min_months": MIN_MONTHS,
                      "rule": "month lit if footprint_max - background_median >= "
                              "max(min_excess, k_sigma*background_sigma) or footprint_max >= "
                              "absolute; persistent if lit in >= min_lit_fraction of usable months"},
    })
    if not used:
        failed = [p for p in periods if p.get("read_failed")]
        out["reason"] = ("archive unreachable: every composite read failed" if len(failed) == len(periods)
                         else "no usable cloud-free observations in the sampled months: "
                         + (periods[0]["reason"] if periods else "none"))
        return out
    lit = [bool(p["lit"]) for p in used]
    out.update({
        "status": "ok",
        "months_used": len(used), "months_lit": int(sum(lit)),
        "lit_fraction": round(sum(lit) / len(used), 3),
        "clear_nights": int(sum(p["clear_nights"] for p in used)),
        "radiance": round(float(np.median([p["footprint_max"] for p in used])), 3),
        "radiance_mean": round(float(np.median([p["footprint_mean"] for p in used])), 3),
        "background": round(float(np.median([p["background_median"] for p in used])), 3),
        "excess": round(float(np.median([p["excess"] for p in used])), 3),
        "persistent_light": _persistence(lit),
        "files": [f for p in used for f in p["files"]],
    })
    return out


# --------------------------------------------------------------------------
# Region scan
# --------------------------------------------------------------------------

def _background(image: np.ndarray, block: int = _BLOCK_PX) -> tuple[np.ndarray, np.ndarray]:
    """Local background level and noise of one radiance image.

    Median and scaled MAD in ``block``-pixel tiles, each replaced by the
    median of its 3x3 tile neighbourhood so that one tile filled by a town
    does not hide the town. NaN pixels are ignored; an all-NaN image gives
    all-NaN outputs.
    """
    height, width = image.shape
    ny, nx = -(-height // block), -(-width // block)
    padded = np.full((ny * block, nx * block), np.nan, dtype="float32")
    padded[:height, :width] = image
    tiles = padded.reshape(ny, block, nx, block).transpose(0, 2, 1, 3).reshape(ny, nx, -1)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        med = np.nanmedian(tiles, axis=-1)
        mad = np.nanmedian(np.abs(tiles - med[..., None]), axis=-1) * 1.4826

        def smooth(values: np.ndarray) -> np.ndarray:
            if not np.isfinite(values).any():
                return values
            out = ndimage.generic_filter(values, np.nanmedian, size=3, mode="nearest")
            out[~np.isfinite(out)] = np.nanmedian(values)
            return out

        med, mad = smooth(med), smooth(mad)
    expand = lambda a: np.repeat(np.repeat(a, block, axis=0), block, axis=1)[:height, :width]  # noqa: E731
    return expand(med).astype("float32"), expand(mad).astype("float32")


def _find_sources(radiance: np.ndarray, nights: np.ndarray) -> list[dict[str, Any]]:
    """Persistent light sources in a stack of monthly images, brightest first.

    ``radiance`` and ``nights`` are (months, rows, cols); radiance is NaN
    where a month has no cloud-free night. A pixel is persistent when it is
    lit (see ``MIN_EXCESS``) in at least ``MIN_LIT_FRACTION`` of its valid
    months and valid in at least ``min(MIN_MONTHS, months)`` (never fewer
    than two: one month cannot show persistence). Touching pixels form one
    source. Positions are array (row, col) coordinates.
    """
    months = radiance.shape[0]
    if months < 2 or radiance.size == 0:
        return []
    need = max(2, min(MIN_MONTHS, months))
    valid = np.isfinite(radiance)
    n_valid = valid.sum(axis=0)
    n_lit = np.zeros(radiance.shape[1:], dtype="int16")
    backgrounds = np.empty_like(radiance)
    with np.errstate(invalid="ignore"):
        for i in range(months):
            background, sigma = _background(radiance[i])
            backgrounds[i] = np.where(valid[i], background, np.nan)
            threshold = np.maximum(MIN_EXCESS, K_SIGMA * sigma)
            n_lit += valid[i] & (((radiance[i] - background) >= threshold)
                                 | (radiance[i] >= ABSOLUTE_LIT))
    persistent = (n_valid >= need) & (n_lit >= np.ceil(MIN_LIT_FRACTION * n_valid - 1e-9))
    labels, count = ndimage.label(persistent, structure=np.ones((3, 3), dtype=bool))
    if count == 0:
        return []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        median = np.nanmedian(radiance, axis=0)
        level = np.nanmedian(backgrounds, axis=0)
    excess = np.where(persistent, median - level, 0.0)
    weight = np.where(persistent, np.maximum(excess, 1e-3), 0.0)
    index = np.arange(1, count + 1)
    peaks = ndimage.maximum_position(np.where(persistent, excess, -np.inf), labels, index)
    centres = ndimage.center_of_mass(weight, labels, index)
    sizes = ndimage.sum(persistent, labels, index)
    means = ndimage.mean(np.where(persistent, median, 0.0), labels, index)
    boxes = ndimage.find_objects(labels)
    clear = np.where(valid, nights, 0.0).sum(axis=0)
    sources: list[dict[str, Any]] = []
    for i in range(count):
        row, col = int(peaks[i][0]), int(peaks[i][1])
        rows, cols = boxes[i]
        sources.append({
            "peak": (row, col), "centre": (float(centres[i][0]), float(centres[i][1])),
            "pixels": int(sizes[i]), "radiance": float(median[row, col]),
            "radiance_mean": float(means[i]), "background": float(level[row, col]),
            "excess": float(excess[row, col]), "months_used": int(n_valid[row, col]),
            "months_lit": int(n_lit[row, col]), "nights": int(round(float(clear[row, col]))),
            "rows": (int(rows.start), int(rows.stop)), "cols": (int(cols.start), int(cols.stop)),
        })
    sources.sort(key=lambda s: -s["excess"])
    return sources


def _region_stack(bbox: BBox, comps_by_month: Sequence[Sequence[Composite]]
                  ) -> tuple[np.ndarray, np.ndarray, Affine | None, list[Composite]]:
    """Read the months of a region; months that fail or hold no data are skipped."""
    def one(comps: Sequence[Composite]) -> tuple[np.ndarray, np.ndarray, Affine, Composite] | None:
        best: tuple[np.ndarray, np.ndarray, Affine, Composite] | None = None
        tried: set[str] = set()
        for comp in comps:
            if comp.satellite + comp.stray_light in tried:
                continue
            tried.add(comp.satellite + comp.stray_light)
            try:
                radiance, nights, transform = _read_pair(comp, bbox)
            except Exception as exc:
                logger.warning("night-light month %s skipped: %r", comp.month, exc)
                continue
            share = float(np.isfinite(radiance).mean()) if radiance.size else 0.0
            if share >= 0.5:
                return radiance, nights, transform, comp
            if share > 0 and best is None:
                best = (radiance, nights, transform, comp)
        return best
    with ThreadPoolExecutor(_THREADS) as pool:
        got = [g for g in pool.map(one, comps_by_month) if g is not None]
    got = [g for g in got if g[0].shape == got[0][0].shape]
    if not got:
        return np.empty((0, 0, 0), "float32"), np.empty((0, 0, 0), "float32"), None, []
    return (np.stack([g[0] for g in got]), np.stack([g[1] for g in got]), got[0][2],
            [g[3] for g in got])


def _settlement(lat: float, lon: float, radius_m: float) -> dict[str, Any]:
    """Mapped built-up land around a source; a failed lookup is reported, not guessed."""
    try:
        from ..eliminate.landcover import builtup_within
        info = builtup_within(lat, lon, radius_m)
        fraction = info.get("builtup_fraction")
        if fraction is None or not math.isfinite(float(fraction)):
            raise ValueError("no built-up fraction returned")
        return {"settlement_context": "ok", "builtup_fraction": round(float(fraction), 4),
                "nearest_builtup_m": info.get("nearest_builtup_m"),
                "builtup_radius_m": float(radius_m), "builtup_map_year": info.get("map_year"),
                "isolated": bool(float(fraction) < ISOLATED_MAX_BUILTUP)}
    except Exception as exc:
        return {"settlement_context": f"not_run: {type(exc).__name__}: {exc}",
                "builtup_fraction": None, "nearest_builtup_m": None,
                "builtup_radius_m": float(radius_m), "isolated": None}


def detect_isolated_lights(region: Region, max_nights: int = 8, max_candidates: int = 50, *,
                           include_settled: bool = False) -> list[Candidate]:
    """Persistent light sources inside a region with no mapped settlement.

    Reads the latest ``max_nights`` monthly composites over the region (plus
    a 12 km margin for the background), finds pixels lit in at least two
    thirds of them and groups them into sources. Each source is looked up in
    the land-cover map: sources on mapped built-up land (share of the disc
    at or above ``ISOLATED_MAX_BUILTUP``) are dropped unless
    ``include_settled`` is true; a source whose lookup failed is kept with
    ``measurements["isolated"] = None``. Brightest first, at most
    ``max_candidates``. Returns [] and never raises when the archive is
    unreachable, the region is outside coverage or wider than about 1000 km,
    or fewer than two months are usable.
    """
    try:
        return _detect(region, int(max_nights), int(max_candidates), include_settled)
    except Exception as exc:  # contract: a detector failure is an empty result
        logger.warning("detect_isolated_lights failed for %s: %r", getattr(region, "id", "?"), exc)
        return []


def _detect(region: Region, max_nights: int, max_candidates: int,
            include_settled: bool) -> list[Candidate]:
    west, south, east, north = (float(v) for v in region.bbox)
    if max_nights < 2 or max_candidates < 1 or not (west < east and south < north):
        return []
    if north < COVERAGE_LAT[0] or south > COVERAGE_LAT[1]:
        return []
    mid = (south + north) / 2
    dlat = _REGION_MARGIN_M / 110_574.0
    dlon = _REGION_MARGIN_M / (111_320.0 * max(math.cos(math.radians(mid)), 0.05))
    read_box: BBox = (west - dlon, south - dlat, east + dlon, north + dlat)
    step = 15.0 / 3600.0
    if (read_box[2] - read_box[0]) / step > _REGION_MAX_PX or (read_box[3] - read_box[1]) / step > _REGION_MAX_PX:
        logger.warning("region %s is too large for a night-light scan", region.id)
        return []
    inventory = _inventory()
    chosen = list(inventory)[-max_nights:]
    radiance, nights, transform, comps = _region_stack(read_box, [inventory[m] for m in chosen])
    if transform is None or len(comps) < 2:
        return []
    sources = _find_sources(radiance, nights)
    px_x = abs(transform.a) * 111_320.0 * max(math.cos(math.radians(mid)), 0.05)
    px_y = abs(transform.e) * 110_574.0
    half_lat = (RESOLUTION_M / 2) / 110_574.0
    out: list[Candidate] = []
    looked_up = 0
    for src in sources:
        if len(out) >= max_candidates or looked_up >= 3 * max_candidates:
            break
        row, col = src["peak"]
        peak_lon = transform.c + (col + 0.5) * transform.a
        peak_lat = transform.f + (row + 0.5) * transform.e
        if not (west <= peak_lon <= east and south <= peak_lat <= north):
            continue
        lon = transform.c + (src["centre"][1] + 0.5) * transform.a
        lat = transform.f + (src["centre"][0] + 0.5) * transform.e
        if not (math.isfinite(lat) and math.isfinite(lon)):
            lat, lon = peak_lat, peak_lon
        area = src["pixels"] * px_x * px_y
        radius = max(1500.0, math.sqrt(area / math.pi) + RESOLUTION_M)
        context = _settlement(lat, lon, radius)
        looked_up += 1
        if context["isolated"] is False and not include_settled:
            continue
        half_lon = (RESOLUTION_M / 2) / (111_320.0 * max(math.cos(math.radians(lat)), 0.05))
        box: BBox = (
            min(transform.c + src["cols"][0] * transform.a, lon - half_lon),
            min(transform.f + src["rows"][1] * transform.e, lat - half_lat),
            max(transform.c + src["cols"][1] * transform.a, lon + half_lon),
            max(transform.f + src["rows"][0] * transform.e, lat + half_lat))
        state = {True: "no mapped settlement", False: "mapped built-up land",
                 None: "settlement lookup not run"}[context["isolated"]]
        out.append(Candidate(
            id=f"SW-{region.id}-NL{len(out) + 1:04d}", region_id=region.id,
            lat=round(float(lat), 6), lon=round(float(lon), 6), bbox=box,
            signature="installation", detector="viirs_light",
            score=round(float(1.0 - math.exp(-max(src["excess"], 0.0) / 10.0)), 4),
            area_m2=round(float(area), 1), sensors=["nightlights_viirs"],
            shape={"pixels": src["pixels"], "pixel_m": [round(px_x, 1), round(px_y, 1)],
                   "equivalent_radius_m": round(math.sqrt(area / math.pi), 1),
                   "note": "extent is an upper bound: 750 m sensor footprint plus blooming"},
            measurements={
                "radiance": round(src["radiance"], 3), "background": round(src["background"], 3),
                "excess": round(src["excess"], 3), "radiance_mean": round(src["radiance_mean"], 3),
                "units": UNITS, "nights": src["nights"], "months_used": src["months_used"],
                "months_lit": src["months_lit"],
                "dates": [f"{_iso(c.start)}/{_iso(c.end)}" for c in comps],
                "files": [c.avg_key for c in comps],
                "peak_lat": round(float(peak_lat), 6), "peak_lon": round(float(peak_lon), 6),
                "resolution_m": RESOLUTION_M, **context},
            notes=(f"Persistent VIIRS night light ({state}). Light shows human activity or "
                   "combustion, not its nature; position is good to about 1 km."),
        ))
    return out


# --------------------------------------------------------------------------
# Elimination check
# --------------------------------------------------------------------------

def _summary(result: dict[str, Any]) -> dict[str, Any]:
    keep = ("status", "reason", "radius_m", "months_used", "months_lit", "lit_fraction",
            "clear_nights", "radiance", "radiance_mean", "background", "excess",
            "persistent_light", "threshold", "archive_end", "resolution_m", "units", "files")
    out = {k: result[k] for k in keep if k in result}
    out["months"] = [p["month"] for p in result.get("periods", []) if p.get("usable")]
    return out


def check_lights(candidate: Candidate) -> list[CheckResult]:
    """Night-light context for a candidate: one ``night_lights`` result.

    Never ``explains``: light shows activity, it does not say what a feature
    is. ``does_not_explain`` carries the measured radiance and whether
    persistent light is present (after the onset when the candidate has one,
    with the months before it for comparison). ``not_run`` when the archive
    is unreachable, does not cover the latitude or the period after the
    onset (the archive end date is stated), or has too few clear months.
    """
    try:
        return [_check(candidate)]
    except Exception as exc:  # a failed check is never a passed check
        logger.warning("check_lights failed: %r", exc)
        return [CheckResult("night_lights", "infrastructure", "not_run",
                            f"night-light check failed: {type(exc).__name__}: {exc}", SOURCE)]


def _check(candidate: Candidate) -> CheckResult:
    def result(status: str, detail: str, evidence: dict[str, Any] | None = None) -> CheckResult:
        return CheckResult("night_lights", "infrastructure", status, detail, SOURCE,  # type: ignore[arg-type]
                           evidence or {})

    lat, lon = float(candidate.lat), float(candidate.lon)
    if not (COVERAGE_LAT[0] <= lat <= COVERAGE_LAT[1]):
        return result("not_run", f"The night-light composites cover latitudes {COVERAGE_LAT[0]:.0f} "
                                 f"to {COVERAGE_LAT[1]:.0f} only; the candidate is at {lat:.3f}.")
    try:
        inventory = _inventory()
    except ArchiveError as exc:
        return result("not_run", f"Night-light archive unreachable: {exc}")
    end = archive_end()
    months = list(inventory)
    onset = _norm_month(candidate.present_from) if candidate.present_from else ""
    after = [m for m in months if m > onset] if onset else months
    radius = min(5000.0, max(1500.0, math.sqrt(max(candidate.area_m2, 0.0) / math.pi) + RESOLUTION_M))
    evidence: dict[str, Any] = {"archive_end": end, "radius_m": radius, "resolution_m": RESOLUTION_M}
    if not after:
        return result("not_run", f"The night-light archive ends {end}; the feature is first seen "
                                 f"{candidate.present_from}, so no night-light data exists for the "
                                 "period after its appearance.", evidence)
    now = radiance_at(lat, lon, radius, months=after[-12:], max_nights=12)
    evidence["after_onset" if onset else "latest"] = _summary(now)
    span = f"{after[-12:][0]} to {after[-1]}"
    if now["status"] != "ok":
        return result("not_run", f"No night-light measurement for {span}: {now['reason']}. "
                                 f"The archive ends {end}.", evidence)
    if now["persistent_light"] is None:
        return result("not_run", f"Only {now['months_used']} usable monthly composite(s) in {span} "
                                 f"(need {MIN_MONTHS}); persistence cannot be judged. The archive "
                                 f"ends {end}.", evidence)
    before_text = ""
    if onset and candidate.absent_until:
        earlier = [m for m in months if m < _norm_month(candidate.absent_until)][-6:]
        if earlier:
            before = radiance_at(lat, lon, radius, months=earlier, max_nights=6)
            evidence["before_onset"] = _summary(before)
            if before["status"] == "ok" and before["persistent_light"] is not None:
                word = "was already present" if before["persistent_light"] else "was absent"
                before_text = (f" Before the onset ({earlier[0]} to {earlier[-1]}) persistent light "
                               f"{word} (radiance {before['radiance']}, background "
                               f"{before['background']} {UNITS}).")
            else:
                before_text = " The months before the onset could not be measured."
    measured = (f"peak radiance {now['radiance']} against background {now['background']} {UNITS}, "
                f"lit in {now['months_lit']} of {now['months_used']} monthly composites ({span}, "
                f"{now['clear_nights']} cloud-free nights)")
    if now["persistent_light"]:
        head = (f"Persistent artificial light IS present within {radius:.0f} m of the candidate: "
                f"{measured}. This indicates ongoing human activity or combustion at or near the "
                "site; it does not say what the feature is.")
    else:
        head = (f"No persistent light within {radius:.0f} m of the candidate: {measured}. Unlit "
                "sites are not thereby unexplained; many installations carry no lights.")
    tail = (f" Sensor footprint about {RESOLUTION_M:.0f} m, so a neighbour within roughly 1 km "
            f"cannot be separated. Archive ends {end}.")
    evidence["persistent_light"] = now["persistent_light"]
    return result("does_not_explain", head + before_text + tail, evidence)
