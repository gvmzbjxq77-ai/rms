"""Fire and burn history: can a recorded or plausible fire explain a candidate?

Two MODIS products are read from Planetary Computer on their native
sinusoidal grid (no resampling of the categorical values):

- MCD64A1 burned area: monthly files, 463 m pixels, value = day of year of burn
  (0 unburned, -1 unmapped, -2 water).
- MOD14A1 / MYD14A1 active fire: 8-day files with one layer per day, 927 m
  pixels, FireMask 7/8/9 = fire at low/nominal/high confidence.

MODIS misses fires smaller than roughly 25 hectares, so "no detection" never
proves "no fire". The Sentinel-2 spectral test is judged independently and can
never explain a candidate on its own. All spectral deltas are after minus
before, as written by the detectors.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.windows import Window

from ..core import config, io
from ..core.models import BBox, Candidate, CheckResult

__all__ = ["burn_history", "burn_likeness", "check_fire", "fire_survey"]

#: MODIS sinusoidal grid: sphere radius, tile size and upper-left corner (metres).
_R = 6371007.181
_TILE_M = 1111950.5196666666
_X_MIN = -20015109.354
_Y_MAX = 10007554.677
#: Each tile is cached in ``_BLOCKS`` x ``_BLOCKS`` blocks (about 56 km each).
_BLOCKS = 20

_CACHE_DIR: Path = config.CACHE / "fire"
_THREADS = 8
_RETRIES = 3
_MAX_ITEMS = 6000
#: Hard bound on remote block reads for one product in one survey.
_MAX_READS = 1500
#: Longest window for which the daily active-fire files are read by default.
_AF_AUTO_DAYS = 800
#: Catalogue answers are re-asked after 3 days for periods this recent (files still
#: arriving) and after 30 days otherwise (the archive has gaps that may be filled).
_FRESH_DAYS = 150
_SEARCH_TTL_DAYS = 3
_SETTLED_TTL_DAYS = 30

_MODIS_BA_START = date(2000, 11, 1)
_S2_START = date(2015, 7, 1)
#: Onset windows are widened by this many days on both sides.
PAD_DAYS = 15
#: Lookback before the onset window for candidates dated from yearly composites.
YEARLY_LOOKBACK_DAYS = 400
_MAX_RADIUS_M = 5000.0
_S2_SPAN_DAYS = 60

MODIS_LIMIT = ("MODIS misses fires smaller than roughly 25 hectares (and fires under "
               "persistent cloud), so a small fire is not excluded")

_ID_RE = re.compile(r"^(?P<product>MCD64A1|MOD14A1|MYD14A1)\.A(?P<year>\d{4})(?P<doy>\d{3})"
                    r"\.h(?P<h>\d{2})v(?P<v>\d{2})\.\d{3}\.(?P<production>\d+)$")
_FIRE_CONFIDENCE = {7: "low", 8: "nominal", 9: "high"}
_CONFIDENCE_RANK = {"low": 0, "nominal": 1, "high": 2}


class _GridMismatch(RuntimeError):
    """A remote file is not on the expected MODIS sinusoidal tile grid."""


@dataclass(frozen=True)
class _Product:
    key: str
    collection: str
    asset: str
    npix: int            # pixels per tile side
    tolerance_m: float   # allowance beyond the radius for the sensor footprint
    fill: int            # value meaning "no information"


_BA = _Product("burned_area", "modis-64A1-061", "Burn_Date", 2400, 250.0, -1)
_AF = _Product("active_fire", "modis-14A1-061", "FireMask", 1200, 600.0, 0)


@dataclass(frozen=True)
class _Pixels:
    """Product pixels around a point: tile, in-tile position and distance of each."""

    h: np.ndarray
    v: np.ndarray
    row: np.ndarray
    col: np.ndarray
    dist: np.ndarray

    @property
    def size(self) -> int:
        return int(self.dist.size)


@dataclass
class _Sample:
    """Values of one granule period (all tiles merged) at the footprint pixels."""

    product: str
    first_day: date
    values: np.ndarray | None = None      # (layers, pixels)
    dates: list[date] = field(default_factory=list)
    tiles: set[tuple[int, int]] = field(default_factory=set)
    complete: bool = True


# --------------------------------------------------------------------------
# Geometry on the MODIS sinusoidal grid
# --------------------------------------------------------------------------

def _to_sinusoidal(lon: np.ndarray | float, lat: np.ndarray | float) -> tuple[np.ndarray, np.ndarray]:
    lat_r = np.radians(np.asarray(lat, dtype="float64"))
    lon_r = np.radians(np.asarray(lon, dtype="float64"))
    return _R * lon_r * np.cos(lat_r), _R * lat_r


def _haversine(lat: float, lon: float, lats: np.ndarray | float, lons: np.ndarray | float) -> np.ndarray:
    """Great-circle distance in metres from one point to many."""
    p1, p2 = np.radians(lat), np.radians(np.asarray(lats, dtype="float64"))
    dlon = np.radians(np.asarray(lons, dtype="float64") - lon)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlon / 2) ** 2
    return np.asarray(2 * 6371008.8 * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0))), dtype="float64")


def _footprint(lat: float, lon: float, reach_m: float, npix: int) -> _Pixels:
    """Grid cells of an ``npix``-per-tile product within ``reach_m`` of a point.

    Distance is measured on the ground from the point to the nearest part of
    each cell (0 inside it). Cells are squares in the sinusoidal projection
    but sheared parallelograms on the ground, so the shear at the point is
    applied: east = dx + shear * dy, north = dy.
    """
    pix = _TILE_M / npix
    xs, ys = _to_sinusoidal(lon, lat)
    xp, yp = float(xs), float(ys)
    shear = math.radians(lon) * math.sin(math.radians(lat))
    span_x = reach_m * (1.0 + abs(shear)) + pix
    c0 = max(math.floor((xp - span_x - _X_MIN) / pix), 0)
    c1 = min(math.floor((xp + span_x - _X_MIN) / pix), 36 * npix - 1)
    r0 = max(math.floor((_Y_MAX - yp - reach_m - pix) / pix), 0)
    r1 = min(math.floor((_Y_MAX - yp + reach_m + pix) / pix), 18 * npix - 1)
    empty = np.zeros(0, dtype="int64")
    if c1 < c0 or r1 < r0 or (c1 - c0 + 1) * (r1 - r0 + 1) > 4_000_000:
        return _Pixels(empty, empty, empty, empty, np.zeros(0))
    cols, rows = np.meshgrid(np.arange(c0, c1 + 1), np.arange(r0, r1 + 1))
    x0 = _X_MIN + cols * pix - xp
    x1 = x0 + pix
    y1 = _Y_MAX - rows * pix - yp
    y0 = y1 - pix
    dist = np.full(cols.shape, np.inf)
    for edge in (y0, y1):                      # nearest point on the two east-west edges
        dx = np.clip(-shear * edge, x0, x1)
        dist = np.minimum(dist, np.hypot(dx + shear * edge, edge))
    for edge in (x0, x1):                      # and on the two north-south edges
        dy = np.clip(-shear * edge / (1.0 + shear ** 2), y0, y1)
        dist = np.minimum(dist, np.hypot(edge + shear * dy, dy))
    dist[(x0 <= 0) & (x1 >= 0) & (y0 <= 0) & (y1 >= 0)] = 0.0
    # Cells beyond the 180th meridian of the projection hold no data.
    on_earth = np.abs(x0 + xp + pix / 2) <= _R * np.pi * np.cos((y0 + yp + pix / 2) / _R)
    keep = on_earth & (dist <= reach_m)
    cols, rows, dist = cols[keep], rows[keep], dist[keep]
    return _Pixels(cols // npix, rows // npix, rows % npix, cols % npix, dist)


# --------------------------------------------------------------------------
# Catalogue and pixel access (cached)
# --------------------------------------------------------------------------

def _today() -> date:
    return datetime.now(UTC).date()


def _parse_day(text: Any) -> date:
    """ISO date (a trailing time is ignored); ValueError when unusable."""
    if isinstance(text, datetime):
        return text.date()
    if isinstance(text, date):
        return text
    if not isinstance(text, str) or len(text) < 10:
        raise ValueError(f"not an ISO date: {text!r}")
    return date.fromisoformat(text[:10])


def _atomic_write(path: Path, writer: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, tmp = tempfile.mkstemp(dir=path.parent, suffix=path.suffix + ".tmp")
    os.close(handle)
    try:
        writer(tmp)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def _search_bbox(lat: float, lon: float, reach_m: float) -> BBox:
    """Box around the point, cut at the poles and the 180th meridian (the catalogue rejects more)."""
    west, south, east, north = io.point_bbox(lat, lon, reach_m)
    return (max(west, -180.0), max(south, -90.0), min(east, 180.0), min(north, 90.0))


def _search(product: _Product, bbox: BBox, start: date, end: date) -> list[dict[str, Any]]:
    """Granules of a product intersecting a box and period (one catalogue query)."""
    items = io.stac_search("pc", product.collection, bbox,
                           f"{start.isoformat()}T00:00:00Z/{end.isoformat()}T23:59:59Z",
                           max_items=_MAX_ITEMS)
    wanted = (product.asset, "Burn_Date_Uncertainty")
    out: list[dict[str, Any]] = []
    for item in items:
        match = _ID_RE.match(item.id)
        if not match or product.asset not in item.assets:
            continue
        first = date(int(match["year"]), 1, 1) + timedelta(days=int(match["doy"]) - 1)
        out.append({"id": item.id, "product": match["product"], "first_day": first.isoformat(),
                    "h": int(match["h"]), "v": int(match["v"]), "production": match["production"],
                    "hrefs": {k: item.assets[k].href for k in wanted if k in item.assets}})
    return out


def _granules(product: _Product, tiles: list[tuple[int, int]], bbox: BBox, start: date,
              end: date, use_cache: bool) -> list[dict[str, Any]]:
    """Newest version of each granule on ``tiles`` in the period, cached on disk."""
    key = hashlib.sha1(json.dumps([product.collection, tiles, start.isoformat(),
                                   end.isoformat()]).encode()).hexdigest()[:20]
    path = _CACHE_DIR / "search" / f"{key}.json"
    today = _today()
    granules: list[dict[str, Any]] | None = None
    if use_cache and path.exists():
        try:
            saved = json.loads(path.read_text())
            fetched = date.fromisoformat(saved["fetched"])
            settled = end < fetched - timedelta(days=_FRESH_DAYS)
            if (today - fetched).days <= (_SETTLED_TTL_DAYS if settled else _SEARCH_TTL_DAYS):
                granules = list(saved["granules"])
        except (OSError, ValueError, KeyError, TypeError):
            granules = None
    if granules is None:
        granules = _search(product, bbox, start, end)
        if use_cache:
            payload = json.dumps({"fetched": today.isoformat(), "granules": granules})
            _atomic_write(path, lambda tmp: Path(tmp).write_text(payload))
    newest: dict[tuple[str, str, int, int], dict[str, Any]] = {}
    for g in granules:
        if (g["h"], g["v"]) not in tiles:
            continue
        slot = (g["product"], g["first_day"], g["h"], g["v"])
        if slot not in newest or g["production"] > newest[slot]["production"]:
            newest[slot] = g
    return sorted(newest.values(), key=lambda g: (g["first_day"], g["product"], g["h"], g["v"]))


def _fetch_block(href: str, npix: int, h: int, v: int, col_off: int, row_off: int,
                 size: int) -> tuple[np.ndarray, list[str]]:
    """Read a native-resolution window (layers, size, size) of a remote MODIS tile."""
    last: Exception | None = None
    for attempt in range(_RETRIES):
        try:
            with rasterio.open(io.sign(href)) as src:
                tr = src.transform
                if (src.width != npix or src.height != npix
                        or abs(tr.c - (_X_MIN + h * _TILE_M)) > 1.0
                        or abs(tr.f - (_Y_MAX - v * _TILE_M)) > 1.0):
                    raise _GridMismatch(f"unexpected MODIS grid in {href.split('?')[0]}")
                data = src.read(window=Window(col_off, row_off, size, size))
                dates = (src.tags().get("Dates") or "").split()
            return data, dates
        except _GridMismatch:
            raise
        except Exception as exc:
            last = exc
            time.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"read failed after {_RETRIES} tries: {href.split('?')[0]}: {last!r}")


def _load_block(granule: dict[str, Any], product: _Product, asset: str, brow: int, bcol: int,
                use_cache: bool) -> tuple[np.ndarray, list[str]]:
    """One block of one granule asset, from the disk cache or the network."""
    path = _CACHE_DIR / "blocks" / f"{granule['id']}.{asset}.{brow:02d}_{bcol:02d}.npz"
    if use_cache and path.exists():
        try:
            with np.load(path, allow_pickle=False) as saved:
                return saved["data"], [str(d) for d in saved["dates"]]
        except Exception:
            path.unlink(missing_ok=True)  # unreadable cache entry: fetch again
    size = product.npix // _BLOCKS
    data, dates = _fetch_block(granule["hrefs"][asset], product.npix, granule["h"], granule["v"],
                               bcol * size, brow * size, size)
    if use_cache:
        def save(tmp: str) -> None:
            with open(tmp, "wb") as handle:  # a handle stops numpy appending ".npz"
                np.savez_compressed(handle, data=data, dates=np.array(dates, dtype="U10"))
        _atomic_write(path, save)
    return data, dates


def _collect(product: _Product, asset: str, pixels: _Pixels, bbox: BBox, start: date, end: date,
             use_cache: bool, only: set[str] | None = None) -> list[_Sample]:
    """Read ``asset`` of every granule in the period at the footprint pixels.

    Returns one sample per (product, period), tiles merged. A sample is
    incomplete when a tile is missing from the catalogue or a read failed.
    """
    tiles = sorted({(int(h), int(v)) for h, v in zip(pixels.h, pixels.v)})
    granules = [g for g in _granules(product, tiles, bbox, start, end, use_cache)
                if asset in g["hrefs"] and (only is None or g["first_day"] in only)]
    size = product.npix // _BLOCKS
    brow, bcol = pixels.row // size, pixels.col // size
    jobs: list[tuple[dict[str, Any], int, int, np.ndarray]] = []
    for g in granules:
        in_tile = (pixels.h == g["h"]) & (pixels.v == g["v"])
        for br, bc in sorted({(int(r), int(c)) for r, c in zip(brow[in_tile], bcol[in_tile])}):
            jobs.append((g, br, bc, np.flatnonzero(in_tile & (brow == br) & (bcol == bc))))
    if len(jobs) > _MAX_READS:
        raise ValueError(f"{len(jobs)} reads needed for {product.collection}; "
                         f"shorten the period (limit {_MAX_READS})")

    def one(job: tuple[dict[str, Any], int, int, np.ndarray]) -> tuple[np.ndarray, list[str]] | None:
        g, br, bc, idx = job
        try:
            data, dates = _load_block(g, product, asset, br, bc, use_cache)
            return data[:, pixels.row[idx] - br * size, pixels.col[idx] - bc * size], dates
        except Exception:
            return None

    with ThreadPoolExecutor(_THREADS) as pool:
        results = list(pool.map(one, jobs))
    samples: dict[tuple[str, str], _Sample] = {}
    for (g, _br, _bc, idx), result in zip(jobs, results):
        first = date.fromisoformat(g["first_day"])
        sample = samples.setdefault((g["product"], g["first_day"]), _Sample(g["product"], first))
        if result is None:
            sample.complete = False
            continue
        values, dates = result
        if sample.values is None:
            sample.values = np.full((values.shape[0], pixels.size), product.fill, dtype="int32")
            try:
                parsed = [date.fromisoformat(d) for d in dates]
            except ValueError:
                parsed = []
            if len(parsed) != values.shape[0]:
                parsed = [first + timedelta(days=i) for i in range(values.shape[0])]
            sample.dates = parsed
        if values.shape[0] != sample.values.shape[0]:
            sample.complete = False
            continue
        sample.values[:, idx] = values
        sample.tiles.add((g["h"], g["v"]))
    for sample in samples.values():
        if sample.values is None or sample.tiles != set(tiles):
            sample.complete = False
    return sorted(samples.values(), key=lambda s: (s.first_day, s.product))


# --------------------------------------------------------------------------
# Product summaries
# --------------------------------------------------------------------------

def _months(start: date, end: date) -> list[date]:
    out, cursor = [], date(start.year, start.month, 1)
    while cursor <= end:
        out.append(cursor)
        cursor = date(cursor.year + cursor.month // 12, cursor.month % 12 + 1, 1)
    return out


def _burned_area(lat: float, lon: float, radius_m: float, start: date, end: date,
                 use_cache: bool) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Burned-area detections and coverage for the footprint."""
    reach = radius_m + _BA.tolerance_m
    pixels = _footprint(lat, lon, reach, _BA.npix)
    months = _months(start, end)
    info: dict[str, Any] = {"status": "no_coverage", "product": "MCD64A1", "pixels": pixels.size,
                            "months_expected": len(months), "months_read": 0,
                            "months_missing": [], "months_failed": [], "months_unmapped": []}
    if pixels.size == 0:
        info["detail"] = "the point is outside the MODIS land grid"
        return [], info
    bbox = _search_bbox(lat, lon, reach)
    samples = {s.first_day: s for s in _collect(_BA, _BA.asset, pixels, bbox, start, end, use_cache)}
    hits: list[tuple[date, np.ndarray]] = []
    for month in months:
        sample = samples.get(month)
        label = month.strftime("%Y-%m")
        if sample is None:
            info["months_missing"].append(label)
            continue
        if not sample.complete or sample.values is None:
            info["months_failed"].append(label)
            if sample.values is None:
                continue
        else:
            info["months_read"] += 1
        values = sample.values[0]
        if np.mean(values != _BA.fill) < 0.5 and sample.complete:
            info["months_unmapped"].append(label)
        for doy in np.unique(values[(values >= 1) & (values <= 366)]):
            day = date(month.year, 1, 1) + timedelta(days=int(doy) - 1)
            if start <= day <= end:
                hits.append((day, np.flatnonzero(values == doy)))
    uncertainty: dict[date, np.ndarray] = {}
    if hits:
        wanted = {date(day.year, day.month, 1).isoformat() for day, _ in hits}
        try:
            for s in _collect(_BA, "Burn_Date_Uncertainty", pixels, bbox, start, end, use_cache, wanted):
                if s.values is not None:
                    uncertainty[s.first_day] = s.values[0]
        except Exception:
            uncertainty = {}
    detections: list[dict[str, Any]] = []
    for day, idx in hits:
        unc = uncertainty.get(date(day.year, day.month, 1))
        days = float(np.median(unc[idx])) if unc is not None and (unc[idx] > 0).all() else None
        confidence = "nominal" if days is None else "high" if days <= 3 else "nominal" if days <= 8 else "low"
        detections.append({"date": day.isoformat(), "product": "MCD64A1",
                           "distance_m": round(float(pixels.dist[idx].min()), 1),
                           "pixels": int(idx.size), "confidence": confidence,
                           "date_uncertainty_days": days})
    gaps = info["months_missing"] or info["months_failed"] or info["months_unmapped"]
    if info["months_read"] == 0:
        info["status"] = "failed" if info["months_failed"] else "no_coverage"
    else:
        info["status"] = "partial" if gaps else "ok"
    info["detail"] = (f"{info['months_read']}/{len(months)} monthly files read for {pixels.size} pixels"
                      + (f"; no file for {', '.join(info['months_missing'][:6])}" if info["months_missing"] else "")
                      + (f"; incomplete (failed read or absent tile) for {', '.join(info['months_failed'][:6])}"
                         if info["months_failed"] else "")
                      + (f"; unmapped in {', '.join(info['months_unmapped'][:6])}" if info["months_unmapped"] else ""))
    return detections, info


def _active_fire(lat: float, lon: float, radius_m: float, start: date, end: date,
                 use_cache: bool) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Active-fire detections and coverage for the footprint."""
    reach = radius_m + _AF.tolerance_m
    pixels = _footprint(lat, lon, reach, _AF.npix)
    n_days = (end - start).days + 1
    info: dict[str, Any] = {"status": "no_coverage", "product": "MOD14A1/MYD14A1",
                            "pixels": pixels.size, "days_expected": n_days, "days_covered": 0,
                            "days_observed": 0, "files_read": 0, "files_failed": 0}
    if pixels.size == 0:
        info["detail"] = "the point is outside the MODIS land grid"
        return [], info
    samples = _collect(_AF, _AF.asset, pixels, _search_bbox(lat, lon, reach), start, end, use_cache)
    covered: set[date] = set()
    observed: set[date] = set()
    detections: list[dict[str, Any]] = []
    for sample in samples:
        if sample.values is None:
            info["files_failed"] += 1
            continue
        info["files_read" if sample.complete else "files_failed"] += 1
        for layer, day in enumerate(sample.dates):
            if not start <= day <= end:
                continue
            values = sample.values[layer]
            if sample.complete:
                covered.add(day)
            if np.isin(values, (3, 5, 7, 8, 9)).any():
                observed.add(day)
            fire = np.flatnonzero((values >= 7) & (values <= 9))
            if fire.size:
                detections.append({"date": day.isoformat(), "product": sample.product,
                                   "distance_m": round(float(pixels.dist[fire].min()), 1),
                                   "pixels": int(fire.size),
                                   "confidence": _FIRE_CONFIDENCE[int(values[fire].max())]})
    info["days_covered"], info["days_observed"] = len(covered), len(observed)
    info["clear_days_by_month"] = {}
    for day in sorted(observed):
        label = day.strftime("%Y-%m")
        info["clear_days_by_month"][label] = info["clear_days_by_month"].get(label, 0) + 1
    if info["files_read"] == 0:
        info["status"] = "failed" if info["files_failed"] else "no_coverage"
    else:
        info["status"] = "ok" if len(covered) >= 0.9 * n_days else "partial"
    info["detail"] = (f"{info['files_read']} eight-day files read ({info['files_failed']} incomplete); "
                      f"{len(covered)}/{n_days} days covered, clear view on {len(observed)}")
    return detections, info


def fire_survey(lat: float, lon: float, radius_m: float, start: str, end: str,
                active_fire: bool | None = None, use_cache: bool = True) -> dict[str, Any]:
    """MODIS fire record around a point, with what was and was not readable.

    Returns ``{"query", "detections", "burned_area", "active_fire"}``. Each
    detection is one product and day: ``date`` (ISO), ``product`` ("MCD64A1",
    "MOD14A1" or "MYD14A1"), ``distance_m`` (point to the nearest detected
    grid cell, 0 inside it), ``pixels`` and ``confidence`` ("low", "nominal"
    or "high"; for burned area it grades the burn-date uncertainty, also
    given in days as ``date_uncertainty_days``). A cell counts when it lies
    within ``radius_m`` plus 250 m (burned area, 463 m cells) or 600 m
    (active fire, 927 m cells). Each product entry has ``status``: "ok",
    "partial", "failed", "no_coverage" or "skipped", and a ``detail``.

    ``active_fire=None`` reads the daily product only for periods up to 800
    days. A period ending in the future is cut at today. Never raises for
    network trouble (see the statuses); raises ValueError for bad arguments.
    """
    if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError(f"invalid coordinates: {lat!r}, {lon!r}")
    if not (math.isfinite(radius_m) and 0 <= radius_m <= 100_000):
        raise ValueError(f"radius_m must be between 0 and 100000: {radius_m!r}")
    first, last = _parse_day(start), min(_parse_day(end), _today())
    if first > last:
        raise ValueError(f"empty period: {start} to {end}")
    out: dict[str, Any] = {"query": {"lat": lat, "lon": lon, "radius_m": radius_m,
                                     "start": first.isoformat(), "end": last.isoformat()},
                           "detections": []}
    try:
        found, out["burned_area"] = _burned_area(lat, lon, radius_m, first, last, use_cache)
        out["detections"] += found
    except Exception as exc:
        out["burned_area"] = {"status": "failed", "product": "MCD64A1",
                              "detail": f"{type(exc).__name__}: {str(exc)[:200]}"}
    if active_fire is False or (active_fire is None and (last - first).days + 1 > _AF_AUTO_DAYS):
        out["active_fire"] = {"status": "skipped", "product": "MOD14A1/MYD14A1",
                              "detail": "daily active-fire files not read for this period"}
    else:
        try:
            found, out["active_fire"] = _active_fire(lat, lon, radius_m, first, last, use_cache)
            out["detections"] += found
        except Exception as exc:
            out["active_fire"] = {"status": "failed", "product": "MOD14A1/MYD14A1",
                                  "detail": f"{type(exc).__name__}: {str(exc)[:200]}"}
    out["detections"].sort(key=lambda d: (d["date"], d["product"]))
    return out


def burn_history(lat: float, lon: float, radius_m: float, start: str, end: str) -> list[dict[str, Any]]:
    """Burn and fire detections near a point between two ISO dates, oldest first.

    One dict per product and day with ``date``, ``product``, ``distance_m``,
    ``pixels`` and ``confidence`` (see ``fire_survey``). An empty list means
    the products were read and show nothing. Raises RuntimeError when neither
    product could be read, so that a failure is never mistaken for "no fire";
    use ``fire_survey`` to see partial coverage.
    """
    survey = fire_survey(lat, lon, radius_m, start, end)
    if not any(survey[key]["status"] in ("ok", "partial") for key in ("burned_area", "active_fire")):
        raise RuntimeError("no MODIS fire product could be read: "
                           + "; ".join(f"{key}: {survey[key]['status']} ({survey[key].get('detail', '')})"
                                       for key in ("burned_area", "active_fire")))
    return list(survey["detections"])


# --------------------------------------------------------------------------
# Spectral judgement
# --------------------------------------------------------------------------

def burn_likeness(d_nbr: float | None, d_ndvi: float | None = None,
                  d_brightness: float | None = None, d_nir: float | None = None) -> tuple[str, str]:
    """Grade a before/after spectral change (after minus before) as a burn scar.

    Returns ``(level, reason)`` with level "burn_like" (NBR drop of 0.10 or
    more with no brightening, greening or NIR rise), "weak" (smaller or
    NDVI-only drop), "not_burn_like" or "unknown" (no NBR and no NDVI).
    """
    if d_nbr is None and d_ndvi is None:
        return "unknown", "no NBR or NDVI change available"
    against = []
    if d_brightness is not None and d_brightness > 0.02:
        against.append(f"surface brightened ({d_brightness:+.3f})")
    if d_nir is not None and d_nir > 0.02:
        against.append(f"near infrared rose ({d_nir:+.3f})")
    if d_nbr is not None and d_nbr > 0.02:
        against.append(f"NBR rose ({d_nbr:+.3f})")
    if d_ndvi is not None and d_ndvi > 0.03:
        against.append(f"NDVI rose ({d_ndvi:+.3f})")
    if against:
        return "not_burn_like", "; ".join(against)
    if d_nbr is not None:
        if d_nbr <= -0.10:
            return "burn_like", f"NBR dropped {d_nbr:+.3f} without brightening or greening"
        if d_nbr <= -0.04:
            return "weak", f"NBR dropped only {d_nbr:+.3f}"
        return "not_burn_like", f"NBR change {d_nbr:+.3f} is too small for a burn"
    assert d_ndvi is not None
    if d_ndvi <= -0.10:
        return "weak", f"NDVI dropped {d_ndvi:+.3f} but NBR is not available"
    return "not_burn_like", f"NDVI change {d_ndvi:+.3f} is too small for a burn"


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _footprint_radius(candidate: Candidate) -> float:
    """Radius of the candidate footprint in metres (0 to 5 km)."""
    radius = math.sqrt(max(_number(candidate.area_m2) or 0.0, 0.0) / math.pi)
    try:
        west, south, east, north = (float(v) for v in candidate.bbox)
        if all(math.isfinite(v) for v in (west, south, east, north)):
            radius = max(radius, 0.5 * float(_haversine(south, west, north, east)))
    except (TypeError, ValueError):
        pass
    return float(min(max(radius, 0.0), _MAX_RADIUS_M))


def _onset_window(candidate: Candidate) -> tuple[date, date] | None:
    """(last date absent, first date present), ordered; None when not both known."""
    try:
        a, b = _parse_day(candidate.absent_until), _parse_day(candidate.present_from)
    except ValueError:
        return None
    return (a, b) if a <= b else (b, a)


def _measure_s2(candidate: Candidate, radius_m: float, window: tuple[date, date]) -> dict[str, Any] | None:
    """Footprint-median spectral change from small Sentinel-2 composites, or None."""
    absent, present = window
    today = _today()
    half = float(np.clip(3.0 * radius_m, 300.0, 1000.0))
    grid = io.make_grid(io.point_bbox(candidate.lat, candidate.lon, half), 10.0)
    bands = ("blue", "green", "red", "nir", "swir22")
    col, row = grid.lonlat_to_xy(candidate.lon, candidate.lat)
    yy, xx = np.mgrid[0:grid.height, 0:grid.width]
    mask = np.hypot(xx + 0.5 - col, yy + 0.5 - row) * grid.res <= max(radius_m, 30.0)

    def stats(first: date, last: date) -> dict[str, Any] | None:
        if last < _S2_START or first > today or not mask.any():
            return None
        comp = io.s2_composite(grid, first.isoformat(), min(last, today).isoformat(),
                               bands=bands, max_scenes=2)
        if comp is None:
            return None
        b = {name: comp[name][mask].astype("float64") for name in bands}
        ok = np.all([np.isfinite(v) for v in b.values()], axis=0)
        ok &= (b["nir"] + b["swir22"] > 0) & (b["nir"] + b["red"] > 0)
        if ok.sum() < max(4, 0.2 * mask.sum()):
            return None
        nir, red, swir = b["nir"][ok], b["red"][ok], b["swir22"][ok]
        return {"nbr": float(np.median((nir - swir) / (nir + swir))),
                "ndvi": float(np.median((nir - red) / (nir + red))),
                "nir": float(np.median(nir)),
                "brightness": float(np.median((b["blue"][ok] + b["green"][ok] + red) / 3)),
                "dates": comp["dates"]}

    before = stats(absent - timedelta(days=_S2_SPAN_DAYS), absent)
    after = stats(present, present + timedelta(days=_S2_SPAN_DAYS))
    if before is None or after is None:
        return None
    out: dict[str, Any] = {f"d_{k}": after[k] - before[k] for k in ("nbr", "ndvi", "nir", "brightness")}
    out["before_dates"], out["after_dates"] = before["dates"], after["dates"]
    step = after["nbr"] - before["nbr"]
    if abs(step) > 0.02 and present + timedelta(days=330) <= today:
        late = stats(present + timedelta(days=330), present + timedelta(days=420))
        if late is not None:
            out["recovery_fraction"] = float(np.clip(1 - (late["nbr"] - before["nbr"]) / step, 0, 1))
    return out


def _spectral(candidate: Candidate, radius_m: float) -> dict[str, Any]:
    """Spectral change of the candidate: detector measurements, else Sentinel-2."""
    raw: dict[str, Any] = candidate.measurements if isinstance(candidate.measurements, dict) else {}
    inner = raw.get("spectral")
    nested: dict[str, Any] = inner if isinstance(inner, dict) else {}
    keys = ("d_nbr", "d_ndvi", "d_brightness", "d_nir", "recovery_fraction")
    values: dict[str, Any] = {k: _number(raw.get(k, nested.get(k))) for k in keys}
    values["source"], values["note"] = "candidate measurements", ""
    if values["d_nbr"] is None and values["d_ndvi"] is None:
        values["source"] = ""
        window = _onset_window(candidate)
        if window is None:
            values["note"] = "no spectral measurements and no onset window to measure across"
        else:
            try:
                measured = _measure_s2(candidate, radius_m, window)
            except Exception as exc:
                measured, values["note"] = None, f"Sentinel-2 measurement failed ({type(exc).__name__})"
            if measured is None:
                values["note"] = values["note"] or "no clear Sentinel-2 imagery on both sides of the onset"
            else:
                values.update({k: _number(measured.get(k)) for k in keys})
                values["source"] = "Sentinel-2 L2A composites (Earth Search)"
                values["before_dates"] = measured["before_dates"]
                values["after_dates"] = measured["after_dates"]
    values["level"], values["reason"] = burn_likeness(
        values["d_nbr"], values["d_ndvi"], values["d_brightness"], values["d_nir"])
    return values


def _fire_consistent(spectral: dict[str, Any]) -> bool | None:
    """Does the change fit a place that MODIS says burned? None when unmeasured.

    Looser than ``burn_likeness``: a modest loss in the burn index or in
    vegetation is enough, because a burnt surface seen months later can be
    brighter than before. Darkening alone is not accepted: solar panels,
    tarmac and wet ground also darken, and industrial heat can trip the
    satellite fire detector.
    """
    if spectral["level"] == "unknown":
        return None
    d_nbr, d_ndvi = spectral["d_nbr"], spectral["d_ndvi"]
    return bool((d_nbr is not None and d_nbr <= -0.04) or (d_ndvi is not None and d_ndvi <= -0.04))


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

def _record_complete(area: dict[str, Any], active: dict[str, Any], first: date,
                     last: date) -> tuple[bool, str]:
    """Can the two products together support "no fire"? Returns (yes, caveat).

    Both must have been read in full. Months the burned-area product left
    unmapped (too few usable observations: snow, darkness, cloud) are accepted
    only when the active-fire product had a clear view of the footprint on at
    least half of their days inside the window.
    """
    if active.get("status") != "ok" or area.get("status") not in ("ok", "partial"):
        return False, ""
    if area["status"] == "ok":
        return True, ""
    if area["months_missing"] or area["months_failed"]:
        return False, ""
    clear = active.get("clear_days_by_month", {})
    for label in area["months_unmapped"]:
        start = date.fromisoformat(label + "-01")
        end = date(start.year + start.month // 12, start.month % 12 + 1, 1) - timedelta(days=1)
        days = (min(end, last) - max(start, first)).days + 1
        if clear.get(label, 0) < 0.5 * days:
            return False, ""
    return True, (f" The burned-area product left {', '.join(area['months_unmapped'])} unmapped (too few "
                  "usable observations, usually snow, darkness or cloud); the active-fire product had "
                  "a clear view on at least half the days of each such month and saw no fire.")


def _describe(detections: list[dict[str, Any]]) -> str:
    burned = [d for d in detections if d["product"] == "MCD64A1"]
    active = [d for d in detections if d["product"] != "MCD64A1"]
    parts = []
    if burned:
        parts.append(f"burned area mapped on {burned[0]['date']}"
                     + (f" to {burned[-1]['date']}" if burned[-1]["date"] != burned[0]["date"] else "")
                     + f" ({sum(d['pixels'] for d in burned)} cells, nearest "
                       f"{min(d['distance_m'] for d in burned):.0f} m from the point)")
    if active:
        days = sorted({d["date"] for d in active})
        best = max(active, key=lambda d: _CONFIDENCE_RANK[d["confidence"]])["confidence"]
        parts.append(f"active fire on {len(days)} day(s) from {days[0]} to {days[-1]} "
                     f"(best confidence {best}, nearest cell "
                     f"{min(d['distance_m'] for d in active):.0f} m from the point)")
    return "; ".join(parts)


def _history(candidate: Candidate, spectral: dict[str, Any], radius_m: float) -> CheckResult:
    source = "MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer)"

    def result(status: str, detail: str, **evidence: Any) -> CheckResult:
        return CheckResult("fire_history", "event", status, detail, source, evidence)  # type: ignore[arg-type]

    window = _onset_window(candidate)
    today = _today()
    if window is None:
        # No onset to tie a fire to: give the burn record of the Sentinel-2 era as context.
        survey = fire_survey(candidate.lat, candidate.lon, radius_m, _S2_START.isoformat(),
                             today.isoformat(), active_fire=False)
        area = survey["burned_area"]
        if area["status"] not in ("ok", "partial"):
            return result("not_run", "no onset window, and the burned-area record could not be read: "
                          + str(area.get("detail", area["status"])), burned_area=area)
        found = survey["detections"]
        context = (_describe(found) if found else "no burn mapped") + f" ({area['detail']})"
        return result("inconclusive", f"no dated onset window, so a fire cannot be tied to the appearance. "
                      f"Burned-area record {_S2_START} to {today} within {radius_m:.0f} m: {context}. "
                      + MODIS_LIMIT + ".", radius_m=radius_m, detections=found[:20],
                      n_detections=len(found), burned_area=area)
    # A burn's brightness signature keeps developing for about a year, so a
    # change dated from yearly composites may be the aftermath of a fire that
    # burned before the last "unchanged" composite: look back a year for those.
    lookback = PAD_DAYS
    if candidate.measurements.get("composite_dates") and candidate.measurements.get("kind") in (
            "step", "transient", "latest_year"):
        lookback = YEARLY_LOOKBACK_DAYS
    first = max(window[0] - timedelta(days=lookback), _MODIS_BA_START)
    last = min(window[1] + timedelta(days=PAD_DAYS), today)
    if first > last:
        return result("not_run", f"onset window {window[0]} to {window[1]} lies outside the MODIS "
                      f"record ({_MODIS_BA_START} to today)")
    survey = fire_survey(candidate.lat, candidate.lon, radius_m, first.isoformat(), last.isoformat())
    area, active, found = survey["burned_area"], survey["active_fire"], survey["detections"]
    evidence: dict[str, Any] = {
        "window": [first.isoformat(), last.isoformat()], "radius_m": radius_m,
        "detections": found[:20], "n_detections": len(found), "burned_area": area,
        "active_fire": active,
        "spectral": {k: spectral[k] for k in ("d_nbr", "d_ndvi", "d_brightness", "level", "source")}}
    span = f"between {first} and {last} within {radius_m:.0f} m of the candidate"
    strong = [d for d in found if d["product"] == "MCD64A1" or d["confidence"] != "low"]
    if strong:
        consistent = _fire_consistent(spectral)
        if consistent is False:
            return result("inconclusive", f"MODIS records fire {span} ({_describe(found)}), but the "
                          f"spectral change is not that of a burn ({spectral['reason']}).", **evidence)
        basis = (f"the spectral change fits a burn ({spectral['reason']})" if consistent
                 else "no spectral measurement was available to cross-check")
        return result("explains", f"MODIS records fire {span}: {_describe(found)}; {basis}.", **evidence)
    if found:
        return result("inconclusive", f"only low-confidence active-fire pixels {span} "
                      f"({_describe(found)}); these are often false alarms.", **evidence)
    readable = [p for p in (area, active) if p["status"] in ("ok", "partial")]
    coverage = f"burned area: {area.get('detail', area['status'])}; active fire: {active.get('detail', active['status'])}"
    if not readable:
        return result("not_run", f"no MODIS fire product could be read ({coverage}).", **evidence)
    complete, caveat = _record_complete(area, active, first, last)
    if complete:
        return result("does_not_explain", f"no burned area and no active fire {span} ({coverage}).{caveat} "
                      + MODIS_LIMIT + ".", **evidence)
    return result("inconclusive", f"no fire seen {span}, but the record is incomplete ({coverage}), "
                  "so a fire in the gap cannot be ruled out.", **evidence)


def _burn_spectral(spectral: dict[str, Any], history: CheckResult) -> CheckResult:
    source = spectral["source"] or "none"
    evidence = {k: spectral.get(k) for k in ("d_nbr", "d_ndvi", "d_brightness", "d_nir",
                                             "recovery_fraction", "level", "before_dates", "after_dates")}
    evidence["fire_history_status"] = history.status

    def result(status: str, detail: str) -> CheckResult:
        return CheckResult("burn_spectral", "natural", status, detail, source, evidence)  # type: ignore[arg-type]

    level = spectral["level"]
    if level == "unknown":
        return result("not_run", spectral["note"] or spectral["reason"])
    recovery = spectral["recovery_fraction"]
    regrowth = "" if recovery is None else (
        f" Recovery fraction {recovery:.2f}: " + (
            "no recovery yet (burn scars can persist for years)" if recovery < 0.1 else
            "gradual recovery, as vegetation regrowth after fire would give" if recovery < 0.9 else
            "fully recovered, which fits a grass fire but also a passing darkening"))
    if level != "burn_like":
        return result("does_not_explain", f"the before/after change does not look like a burn scar: "
                      f"{spectral['reason']}.{regrowth}")
    if history.status == "explains":
        return result("explains", f"burn-like change ({spectral['reason']}) at a place and time where "
                      f"MODIS records fire.{regrowth}")
    return result("inconclusive", f"burn-like change ({spectral['reason']}) with no MODIS fire record "
                  f"(fire_history: {history.status}). A fire too small for MODIS is the leading "
                  f"explanation but is unproven.{regrowth}")


def check_fire(candidate: Candidate) -> list[CheckResult]:
    """Test fire as the explanation: results "fire_history", "burn_spectral", "lightning".

    - fire_history (event): "explains" when MODIS burned area, or active fire
      of nominal or high confidence, overlaps the footprint inside the onset
      window padded by 15 days and the spectral change fits a burn (or is
      unmeasured); "does_not_explain" only when both products were read in
      full and show nothing (months the burned-area product left unmapped
      need a clear active-fire view on half their days); "inconclusive" for
      incomplete records, contradicting spectra, low-confidence fire only or
      a missing onset window; "not_run" when nothing could be read.
    - burn_spectral (natural): Sentinel-2 change graded alone; a burn-like
      change without a MODIS record is "inconclusive", never "explains".
    - lightning (event): always "not_run"; no open archive is reachable.

    Never raises: any failure becomes "not_run" with the reason.
    """
    lightning = CheckResult(
        "lightning", "event", "not_run",
        "no open global lightning archive can be reached without an account, so ignition by "
        "lightning was not tested", "none")
    valid = (_number(candidate.lat) is not None and _number(candidate.lon) is not None
             and -90 <= candidate.lat <= 90 and -180 <= candidate.lon <= 180)
    if not valid:
        reason = "candidate has no valid coordinates"
        return [CheckResult("fire_history", "event", "not_run", reason, "none"),
                CheckResult("burn_spectral", "natural", "not_run", reason, "none"), lightning]
    radius = _footprint_radius(candidate)
    try:
        spectral = _spectral(candidate, radius)
    except Exception as exc:
        spectral = {"d_nbr": None, "d_ndvi": None, "d_brightness": None, "d_nir": None,
                    "recovery_fraction": None, "source": "", "level": "unknown",
                    "reason": "no NBR or NDVI change available",
                    "note": f"spectral measurement failed ({type(exc).__name__}: {str(exc)[:120]})"}
    try:
        history = _history(candidate, spectral, radius)
    except Exception as exc:
        history = CheckResult("fire_history", "event", "not_run",
                              f"{type(exc).__name__}: {str(exc)[:200]}", "MODIS (Planetary Computer)")
    return [history, _burn_spectral(spectral, history), lightning]
