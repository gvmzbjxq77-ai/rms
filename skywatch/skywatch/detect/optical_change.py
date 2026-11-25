"""Abrupt, dated surface changes in Sentinel-2 yearly same-season composites.

For every pixel the yearly series of four features is tested for a single
step (a change between two consecutive years that then persists) and for a
single-year transient. Changes are normalised by the pixel's own year-to-year
noise and by a region-wide noise floor, so naturally variable surfaces do not
dominate. Connected pixels that changed in the same year form a candidate.
"""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from typing import Any, Sequence

import numpy as np
from scipy import ndimage

from ..core import io
from ..core.models import Candidate, Region

log = logging.getLogger(__name__)

FEATURES = ("brightness", "ndvi", "nbr", "swir")
#: Smallest change in a feature that counts, in the feature's own units.
MIN_STEP = {"brightness": 0.03, "ndvi": 0.08, "nbr": 0.08, "swir": 0.04}
#: Robust z thresholds for a persistent step and for a one-year transient.
Z_STEP = 6.0
Z_TRANSIENT = 9.0
#: The year-on-year jump at the break must carry this share of the full step.
ABRUPT_SHARE = 0.6
#: 2017 is left out: its imagery comes from a different processing chain.
DEFAULT_YEARS = tuple(range(2018, 2027))
#: Window (metres) in which same-year changes around a blob are counted.
CROWD_WINDOW_M = 3000.0
_SERIES_BANDS = ("blue", "green", "red", "nir", "swir22")


def season_window(year: int, season: tuple[str, str]) -> tuple[str, str]:
    """ISO start and end of a (MM-DD, MM-DD) season beginning in ``year``.

    A season whose end precedes its start wraps into the following year.
    """
    start = f"{year}-{season[0]}"
    end_year = year + 1 if season[1] < season[0] else year
    return start, f"{end_year}-{season[1]}"


def season_middle(year: int, season: tuple[str, str]) -> str:
    """ISO date at the middle of the season window: the target date for composites."""
    start, end = season_window(year, season)
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    return (first + (last - first) / 2).isoformat()


def features(bands: dict[str, np.ndarray]) -> np.ndarray:
    """Stack the four change features (brightness, NDVI, NBR, SWIR) as float32."""
    red, nir = bands["red"], bands["nir"]
    with np.errstate(divide="ignore", invalid="ignore"):
        brightness = (bands["blue"] + bands["green"] + red) / 3.0
        ndvi = (nir - red) / (nir + red)
        nbr = (nir - bands["swir22"]) / (nir + bands["swir22"])
    swir = bands.get("swir16", bands["swir22"])
    out = np.stack([brightness, ndvi, nbr, swir]).astype("float32")
    out[~np.isfinite(out)] = np.nan
    return out


def yearly_stack(region: Region, years: Sequence[int], res: float,
                 max_scenes: int = 3, workers: int = 2) -> tuple[io.Grid, list[int], np.ndarray, dict[int, dict[str, Any]]]:
    """Composite every year; return grid, usable years, features[y, f, H, W], metadata."""
    grid = io.make_grid(region.bbox, res)

    def one(year: int) -> tuple[int, tuple[np.ndarray, dict[str, Any]] | None]:
        start, end = season_window(year, region.season)
        if start > date.today().isoformat():
            return year, None
        try:
            comp = io.s2_composite(grid, start, end, max_scenes=max_scenes,
                                   prefer_date=season_middle(year, region.season))
        except Exception as exc:
            log.warning("composite failed for %s %s: %r", region.id, year, exc)
            return year, None
        if comp is None:
            return year, None
        return year, (features(comp), {"dates": comp["dates"], "scene_ids": comp["scene_ids"]})

    # Fill one preallocated array as years arrive, so no second copy is held.
    stack = np.full((len(years), 4, *grid.shape), np.nan, "float32")
    meta: dict[int, dict[str, Any]] = {}
    with ThreadPoolExecutor(workers) as pool:
        for index, (year, result) in enumerate(pool.map(one, years)):
            if result is not None:
                stack[index] = result[0]
                meta[year] = result[1]
    usable = [y for y in years if y in meta]
    if len(usable) < len(years):
        stack = stack[[i for i, y in enumerate(years) if y in meta]]
    return grid, usable, stack, meta


def noise_floors(stack: np.ndarray) -> list[float]:
    """Region-wide robust year-to-year noise of each feature (one value per feature)."""
    floors: list[float] = []
    for f, name in enumerate(FEATURES[:stack.shape[1]]):
        diffs = np.abs(np.diff(stack[:, f, ::7, ::7], axis=0))
        finite = diffs[np.isfinite(diffs)]
        floor = float(np.median(finite) * 1.4826 / np.sqrt(2)) if finite.size else 0.0
        floors.append(max(floor, 0.25 * MIN_STEP[name] / 3.0))
    return floors


def _sums(series: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Validity mask and cumulative sums of one feature's yearly series."""
    ok = np.isfinite(series)
    filled = np.where(ok, series, 0.0).astype("float32")
    return ok, np.cumsum(filled, axis=0), np.cumsum(filled ** 2, axis=0), \
        np.cumsum(ok, axis=0, dtype="float32")


def step_statistics(stack: np.ndarray, chunk_rows: int = 400) -> dict[str, np.ndarray]:
    """Per-pixel best persistent step and best single-year transient.

    ``stack`` is features[y, f, H, W] with NaN gaps. Returns arrays over (H, W):
    step_z, step_k (index of the first year after the break), trans_z, trans_k,
    n_valid, and step_delta / trans_delta [f, H, W]: the after-minus-before
    mean at the best step, and the excursion in the best transient year.
    The raster is processed in strips of ``chunk_rows`` rows to bound memory;
    the noise floors are computed once over the whole raster.
    """
    floors = noise_floors(stack)
    parts = [_step_block(stack[:, :, r0:r0 + chunk_rows], floors)
             for r0 in range(0, max(stack.shape[2], 1), chunk_rows)]
    return {key: np.concatenate([p[key] for p in parts], axis=-2) for key in parts[0]}


def _step_block(stack: np.ndarray, floors: Sequence[float]) -> dict[str, np.ndarray]:
    """``step_statistics`` for one strip, with the noise floors supplied."""
    n_years, n_feat, height, width = stack.shape
    best_step = np.zeros((n_years, height, width), "float16")
    best_trans = np.zeros((n_years, height, width), "float16")
    n_valid = np.isfinite(stack).all(axis=1).sum(axis=0).astype("int16")
    for f in range(n_feat):
        series = stack[:, f]
        ok, csum, csum2, cnum = _sums(series)
        floor = floors[f]
        total, total2, count = csum[-1], csum2[-1], cnum[-1]
        minimum = MIN_STEP[FEATURES[f]]
        with np.errstate(divide="ignore", invalid="ignore"):
            for k in range(1, n_years):
                n1, n2 = cnum[k - 1], count - cnum[k - 1]
                m1 = csum[k - 1] / n1
                m2 = (total - csum[k - 1]) / n2
                sse = (csum2[k - 1] - n1 * m1 ** 2) + ((total2 - csum2[k - 1]) - n2 * m2 ** 2)
                resid = np.sqrt(np.clip(sse, 0, None) / np.clip(n1 + n2 - 2, 1, None))
                step = m2 - m1
                jump = series[k] - series[k - 1]
                abrupt = (np.sign(jump) == np.sign(step)) & (np.abs(jump) >= ABRUPT_SHARE * np.abs(step))
                z = np.abs(step) / np.sqrt(resid ** 2 + floor ** 2)
                # Two composites are required on each side: a level known from a
                # single year (above all the first, 2017, whose imagery has
                # known striping) cannot anchor a step.
                good = abrupt & (n1 >= 2) & (n2 >= 2) & (np.abs(step) >= minimum)
                np.maximum(best_step[k], np.where(good, np.clip(z, 0, 250), 0).astype("float16"),
                           out=best_step[k])
                # Single-year transient (the first year has no "before").
                value = np.where(ok[k], series[k], 0.0)
                n_other = count - ok[k]
                base = (total - value) / n_other
                sse_t = (total2 - value ** 2) - n_other * base ** 2
                resid_t = np.sqrt(np.clip(sse_t, 0, None) / np.clip(n_other - 1, 1, None))
                excursion = series[k] - base
                z_t = np.abs(excursion) / np.sqrt(resid_t ** 2 + floor ** 2)
                good_t = ok[k] & (n_other >= 4) & (np.abs(excursion) >= 1.5 * minimum)
                np.maximum(best_trans[k], np.where(good_t, np.clip(z_t, 0, 250), 0).astype("float16"),
                           out=best_trans[k])
        del ok, csum, csum2, cnum
    # The EARLIEST significant step dates the event; later steps are its
    # aftermath (ash blowing away, regrowth, a second construction phase).
    significant = best_step.astype("float32") >= Z_STEP
    first_k = significant.argmax(axis=0)
    step_k = np.where(significant.any(axis=0), first_k, best_step.argmax(axis=0))
    step_z = np.take_along_axis(best_step, step_k[None], 0)[0].astype("float32")
    trans_k = best_trans.argmax(axis=0)
    trans_z = np.take_along_axis(best_trans, trans_k[None], 0)[0].astype("float32")
    del best_step, best_trans
    step_delta = np.zeros((n_feat, height, width), "float32")
    trans_delta = np.zeros((n_feat, height, width), "float32")
    before_index = np.clip(step_k - 1, 0, None)[None]
    for f in range(n_feat):
        series = stack[:, f]
        ok, csum, _csum2, cnum = _sums(series)
        total, count = csum[-1], cnum[-1]
        with np.errstate(divide="ignore", invalid="ignore"):
            c1 = np.take_along_axis(csum, before_index, 0)[0]
            n1 = np.take_along_axis(cnum, before_index, 0)[0]
            delta = (total - c1) / (count - n1) - c1 / n1
            step_delta[f] = np.where((step_k > 0) & np.isfinite(delta), delta, 0)
            value = np.take_along_axis(series, trans_k[None], 0)[0]
            seen = np.take_along_axis(ok, trans_k[None], 0)[0]
            base = (total - np.where(seen, value, 0.0)) / (count - seen)
            excursion = value - base
            trans_delta[f] = np.where(np.isfinite(excursion), excursion, 0)
    return {"step_z": step_z, "step_k": step_k.astype("int8"), "trans_z": trans_z,
            "trans_k": trans_k.astype("int8"), "step_delta": step_delta,
            "trans_delta": trans_delta, "n_valid": n_valid}


def _blobs(mask: np.ndarray, key: np.ndarray, res: float, min_area_m2: float,
           max_area_m2: float) -> list[tuple[int, np.ndarray, tuple[slice, slice], float]]:
    """Connected components of ``mask`` that share one break year ``key``.

    Each blob comes with its crowding: the share of the surrounding
    ``CROWD_WINDOW_M`` window, outside the blob itself, that changed in the
    same year. Isolated changes score near zero; weather, seasonal and
    processing effects, which touch whole neighbourhoods at once, score high.
    """
    out: list[tuple[int, np.ndarray, tuple[slice, slice], float]] = []
    size = max(3, int(round(CROWD_WINDOW_M / res)) | 1)
    for k in np.unique(key[mask]):
        same_year = mask & (key == k)
        density = ndimage.uniform_filter(same_year.astype("float32"), size=size, mode="constant")
        part = ndimage.binary_opening(same_year, structure=np.ones((2, 2), bool))
        part = ndimage.binary_closing(part, structure=np.ones((3, 3), bool))
        labels, count = ndimage.label(part, structure=np.ones((3, 3), int))
        if not count:
            continue
        for index, box in enumerate(ndimage.find_objects(labels), start=1):
            blob = labels[box] == index
            area = blob.sum() * res ** 2
            if min_area_m2 <= area <= max_area_m2:
                own = blob.sum() / float(size * size)
                crowding = max(float(np.median(density[box][blob])) - own, 0.0)
                out.append((int(k), blob, box, crowding))
    return out


def detect_changes(region: Region, years: Sequence[int] | None = None, res: float = 20.0,
                   min_area_m2: float = 1600.0, max_area_m2: float = 3.0e8,
                   max_candidates: int = 200,
                   diagnostics: dict[str, Any] | None = None) -> list[Candidate]:
    """Find abrupt surface changes in ``region`` and return ranked candidates.

    Each candidate carries its break year, the dates of the two composites
    that bracket the change (``absent_until`` / ``present_from``), the size of
    the change in each feature, and its shape. ``score`` is
    ``min(1, median z / 25)`` over the blob. Pixels with fewer than five valid
    years are ignored. Ranking puts persistent steps before single-year
    changes, then favours isolated changes (low ``measurements["crowding"]``)
    with regular outlines.
    Candidates beyond ``max_candidates`` are dropped with a log line saying how
    many. ``measurements["kind"]`` is ``step`` (persisted at least two years),
    ``latest_year`` (changed in the newest composite: persistence unknown) or
    ``transient`` (present in one year only). When ``diagnostics`` is given it
    is filled with the grid, the years used, per-pixel break-year maps and
    the total number of blobs found.
    """
    from .shape import classify_signature, describe_blob

    grid, usable, stack, meta = yearly_stack(region, years or DEFAULT_YEARS, res)
    if len(usable) < 5:
        log.warning("%s: only %d usable years; skipped", region.id, len(usable))
        return []
    stats = step_statistics(stack)
    enough = stats["n_valid"] >= 5
    step_mask = enough & (stats["step_z"] >= Z_STEP)
    trans_mask = enough & ~step_mask & (stats["trans_z"] >= Z_TRANSIENT)
    found: list[tuple[str, int, np.ndarray, tuple[slice, slice], float]] = []
    found += [("step", *b) for b in _blobs(step_mask, stats["step_k"], res, min_area_m2, max_area_m2)]
    found += [("transient", *b) for b in _blobs(trans_mask, stats["trans_k"], res, min_area_m2, max_area_m2)]
    if diagnostics is not None:
        year_of = np.array(usable, dtype="int16")
        diagnostics.update({
            "grid": grid, "years": list(usable), "n_blobs": len(found),
            "step_year": np.where(step_mask, year_of[stats["step_k"]], 0).astype("int16"),
            "transient_year": np.where(trans_mask, year_of[stats["trans_k"]], 0).astype("int16"),
            "step_fraction": float(step_mask.mean()),
            "transient_fraction": float(trans_mask.mean()),
            "valid_fraction": float(enough.mean())})
    candidates: list[Candidate] = []
    for kind, k, blob, box, crowding in found:
        zmap = stats["step_z" if kind == "step" else "trans_z"][box]
        delta = stats["step_delta" if kind == "step" else "trans_delta"][(slice(None),) + box]
        z_med = float(np.median(zmap[blob]))
        d = {name: float(np.median(delta[i][blob])) for i, name in enumerate(FEATURES)}
        rows, cols = np.nonzero(blob)
        row = box[0].start + rows.mean()
        col = box[1].start + cols.mean()
        lon, lat = grid.xy_to_lonlat(col, row)
        w, n = grid.xy_to_lonlat(box[1].start - 2.5, box[0].start - 2.5)
        e, s = grid.xy_to_lonlat(box[1].stop + 1.5, box[0].stop + 1.5)
        year = usable[k]
        if kind == "step":
            prev_year = usable[k - 1]
            persistence = len(usable) - k
            first = np.nanmedian(stack[k][(slice(None),) + box][:, blob], axis=1)
            last = np.nanmedian(stack[-1][(slice(None),) + box][:, blob], axis=1)
            before = first - np.array([d[nm] for nm in FEATURES])
            main = int(np.argmax([abs(d[nm]) / MIN_STEP[nm] for nm in FEATURES]))
            denom = first[main] - before[main]
            recovery = float(np.clip(1 - (last[main] - before[main]) / denom, 0, 1)) if abs(denom) > 1e-6 else 0.0
        else:
            prev_year = usable[k - 1] if k > 0 else None
            persistence = 1
            recovery = 1.0
            if k == len(usable) - 1:
                kind = "latest_year"
                recovery = 0.0
        shape = describe_blob(blob, res)
        spectral = {"d_brightness": d["brightness"], "d_ndvi": d["ndvi"], "d_nbr": d["nbr"],
                    "d_swir": d["swir"], "recovery_fraction": recovery, "origin": "optical"}
        candidates.append(Candidate(
            id="", region_id=region.id, lat=lat, lon=lon,
            bbox=(min(w, e), min(s, n), max(w, e), max(s, n)),
            signature=classify_signature(shape, spectral),  # type: ignore[arg-type]
            detector="optical_change", score=float(min(1.0, z_med / 25.0)),
            area_m2=float(blob.sum() * res ** 2),
            absent_until=max(meta[prev_year]["dates"]) if prev_year is not None else None,
            present_from=min(meta[year]["dates"]),
            sensors=["optical_s2"], shape=shape,
            measurements={
                "kind": kind, "break_year": int(year), "step_snr": z_med,
                "d_brightness": d["brightness"], "d_ndvi": d["ndvi"], "d_nbr": d["nbr"],
                "d_swir": d["swir"], "persistence_years": int(persistence),
                "recovery_fraction": recovery, "crowding": crowding,
                "n_valid_years": int(np.median(stats["n_valid"][box][blob])),
                "years_used": [int(y) for y in usable],
                "composite_dates": {str(y): meta[y]["dates"] for y in usable},
                "scene_ids_before": meta[prev_year]["scene_ids"] if prev_year is not None else [],
                "scene_ids_after": meta[year]["scene_ids"], "res_m": res,
            }))
    def rank(c: Candidate) -> tuple[int, float]:
        # Isolated, geometric changes first: that is what the search is for.
        isolation = 1.0 / (1.0 + c.measurements["crowding"] / 0.02)
        geometry = 1.0 + float(c.shape.get("regularity", 0.0))
        return (0 if c.measurements["kind"] == "step" else 1, -c.score * isolation * geometry)

    candidates.sort(key=rank)
    if len(candidates) > max_candidates:
        # Two thirds of the places go to persistent steps, the rest to
        # single-year changes, so neither kind can crowd the other out.
        steps = [c for c in candidates if c.measurements["kind"] == "step"]
        others = [c for c in candidates if c.measurements["kind"] != "step"]
        n_steps = min(len(steps), max(max_candidates - min(len(others), max_candidates // 3), 0))
        kept = steps[:n_steps] + others[:max_candidates - n_steps]
        log.warning("%s: %d candidates found, %d dropped by the cap of %d", region.id,
                    len(candidates), len(candidates) - len(kept), max_candidates)
        candidates = sorted(kept, key=rank)
    for n, candidate in enumerate(candidates, start=1):
        candidate.id = f"SW-{region.id}-OC{n:04d}"
    return candidates


def detect_event_change(region: Region, event_date: str, window_days: int = 150,
                        res: float = 10.0, min_area_m2: float = 800.0,
                        max_area_m2: float = 2.0e6, z_threshold: float = 6.0,
                        max_candidates: int = 60) -> list[Candidate]:
    """Changes that appeared around a known date (for seeded and dated sites).

    Compares a clear-scene composite from the ``window_days`` after the date
    with one from the same span before it, then subtracts the same
    before/after difference from one year earlier, which removes the ordinary
    seasonal change. The double difference is scaled by its own robust spatial
    spread; pixels beyond ``z_threshold`` with a meaningful absolute change
    form candidates (``measurements["kind"]`` = "event_window"). When the
    previous-year pair is unavailable the single difference is used and
    ``measurements["seasonal_baseline"]`` is False.
    """
    from .shape import classify_signature, describe_blob

    when = datetime.fromisoformat(event_date[:10]).date()
    grid = io.make_grid(region.bbox, res)

    def pair(shift_years: int) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        centre = when.replace(year=when.year - shift_years) if not (when.month == 2 and when.day == 29) \
            else when.replace(year=when.year - shift_years, day=28)
        before = io.s2_composite(grid, (centre - timedelta(days=window_days)).isoformat(),
                                 (centre - timedelta(days=2)).isoformat(), max_scenes=4, max_cloud=40.0)
        after_end = min(centre + timedelta(days=window_days), date.today())
        after = io.s2_composite(grid, (centre + timedelta(days=2)).isoformat(),
                                after_end.isoformat(), max_scenes=4, max_cloud=40.0)
        return before, after

    before, after = pair(0)
    if before is None or after is None:
        log.warning("%s: no clear imagery on one side of %s", region.id, event_date)
        return []
    diff = features(after) - features(before)
    baseline = False
    try:
        prev_before, prev_after = pair(1)
        if prev_before is not None and prev_after is not None:
            diff = diff - (features(prev_after) - features(prev_before))
            baseline = True
    except Exception as exc:
        log.info("no seasonal baseline for %s: %r", region.id, exc)
    z = np.zeros(grid.shape, "float32")
    big = np.zeros(grid.shape, bool)
    for i, name in enumerate(FEATURES):
        layer = diff[i]
        finite = layer[np.isfinite(layer)]
        if finite.size < 100:
            continue
        centre_value = float(np.median(finite))
        spread = max(float(np.median(np.abs(finite - centre_value)) * 1.4826), MIN_STEP[name] / 6.0)
        zi = np.abs(np.nan_to_num(layer - centre_value, nan=0.0)) / spread
        strong = np.abs(np.nan_to_num(layer - centre_value, nan=0.0)) >= MIN_STEP[name]
        z = np.maximum(z, np.where(strong, zi, 0).astype("float32"))
        big |= strong
    mask = big & (z >= z_threshold)
    candidates: list[Candidate] = []
    for _, blob, box, crowding in _blobs(mask, np.zeros(grid.shape, "int8"), res, min_area_m2, max_area_m2):
        z_med = float(np.median(z[box][blob]))
        d = {name: float(np.nanmedian(diff[i][box][blob])) for i, name in enumerate(FEATURES)}
        rows, cols = np.nonzero(blob)
        lon, lat = grid.xy_to_lonlat(box[1].start + cols.mean(), box[0].start + rows.mean())
        w, n = grid.xy_to_lonlat(box[1].start - 2.5, box[0].start - 2.5)
        e, s = grid.xy_to_lonlat(box[1].stop + 1.5, box[0].stop + 1.5)
        shape = describe_blob(blob, res)
        spectral = {"d_brightness": d["brightness"], "d_ndvi": d["ndvi"], "d_nbr": d["nbr"],
                    "d_swir": d["swir"], "origin": "optical"}
        candidates.append(Candidate(
            id="", region_id=region.id, lat=lat, lon=lon,
            bbox=(min(w, e), min(s, n), max(w, e), max(s, n)),
            signature=classify_signature(shape, spectral),  # type: ignore[arg-type]
            detector="optical_event", score=float(min(1.0, z_med / 25.0)),
            area_m2=float(blob.sum() * res ** 2), absent_until=max(before["dates"]),
            present_from=min(after["dates"]), sensors=["optical_s2"], shape=shape,
            measurements={"kind": "event_window", "event_date": event_date[:10],
                          "break_year": when.year, "step_snr": z_med,
                          "d_brightness": d["brightness"], "d_ndvi": d["ndvi"], "d_nbr": d["nbr"],
                          "d_swir": d["swir"], "seasonal_baseline": baseline, "crowding": crowding,
                          "composite_dates": {"before": before["dates"], "after": after["dates"]},
                          "scene_ids_before": before["scene_ids"],
                          "scene_ids_after": after["scene_ids"], "res_m": res}))
    candidates.sort(key=lambda c: -c.score * (1.0 + 0.5 * np.log10(max(c.area_m2, min_area_m2) / min_area_m2))
                    / (1.0 + c.measurements["crowding"] / 0.02))
    if len(candidates) > max_candidates:
        log.warning("%s: %d event candidates, %d dropped by the cap", region.id,
                    len(candidates), len(candidates) - max_candidates)
        candidates = candidates[:max_candidates]
    for n, candidate in enumerate(candidates, start=1):
        candidate.id = f"SW-{region.id}-EV{n:04d}"
    return candidates


def time_series(lat: float, lon: float, footprint_radius_m: float, start: str, end: str,
                max_scenes: int = 60, max_cloud: float = 30.0) -> dict[str, Any]:
    """Per-scene Sentinel-2 statistics inside a footprint and its surrounding ring.

    For each clear scene (10 m, coarser for footprints over about 500 m in
    radius) between ``start`` and ``end``: mean brightness,
    NDVI and NBR inside a disc of ``footprint_radius_m`` and inside the ring
    from 2x to 4x that radius. Scenes are spread evenly over the period.
    Returns ``dates``, ``inside`` and ``ring`` (dicts of lists), ``valid``
    and ``scene_ids``; scenes where the footprint is under 70 % clear are left out.
    """
    radius = max(float(footprint_radius_m), 15.0)
    half = 4.5 * radius + 20.0
    # Large footprints are read at a coarser resolution: at most ~500 px across.
    res = float(max(10, int(np.ceil(2 * half / 500.0 / 10.0)) * 10))
    grid = io.make_grid(io.point_bbox(lat, lon, half), res)
    items = io.s2_scenes(grid.bbox_wgs84(), start, end, max_cloud=max_cloud, max_items=600)
    by_day: dict[str, Any] = {}
    for item in sorted(items, key=lambda it: it.datetime):
        by_day.setdefault(item.datetime.strftime("%Y-%m-%d"), item)
    days = sorted(by_day)
    if len(days) > max_scenes:
        picks = np.unique(np.round(np.linspace(0, len(days) - 1, max_scenes)).astype(int))
        days = [days[i] for i in picks]
    col, row = grid.lonlat_to_xy(lon, lat)
    yy, xx = np.mgrid[:grid.height, :grid.width]
    dist = np.hypot(xx + 0.5 - col, yy + 0.5 - row) * grid.res
    inside_mask = dist <= radius
    ring_mask = (dist >= 2 * radius) & (dist <= 4 * radius)

    def one(day: str) -> dict[str, Any] | None:
        try:
            scene = io.s2_read(by_day[day], grid, _SERIES_BANDS, mask_dilate=1)
        except Exception:
            return None
        valid = scene["valid"]
        if valid[inside_mask].mean() < 0.7 or valid[ring_mask].mean() < 0.4:
            return None
        feats = features(scene)
        row_out: dict[str, Any] = {"date": day, "scene_id": by_day[day].id,
                                   "valid": float(valid[inside_mask].mean())}
        for i, name in enumerate(FEATURES[:3]):
            row_out[f"in_{name}"] = float(np.nanmean(feats[i][inside_mask]))
            row_out[f"ring_{name}"] = float(np.nanmean(feats[i][ring_mask]))
        return row_out

    with ThreadPoolExecutor(4) as pool:
        rows = [r for r in pool.map(one, days) if r is not None]
    return {
        "dates": [r["date"] for r in rows], "scene_ids": [r["scene_id"] for r in rows],
        "valid": [r["valid"] for r in rows],
        "inside": {n: [r[f"in_{n}"] for r in rows] for n in FEATURES[:3]},
        "ring": {n: [r[f"ring_{n}"] for r in rows] for n in FEATURES[:3]},
        "footprint_radius_m": radius, "scenes_considered": len(days),
    }


def refine_onset(candidate: Candidate, pad_days: int = 400, max_scenes: int = 32) -> Candidate:
    """Tighten the onset window using individual scenes; store the series.

    The inside-minus-ring contrast of the most changed feature (or, when the
    surroundings changed too, the absolute inside value) is classified
    scene by scene as "before-like" or "after-like". ``absent_until`` becomes
    the last scene of the unbroken before-like run and ``present_from`` the
    first scene after which every scene is after-like. When the series does
    not separate cleanly the dates are left alone and
    ``measurements["onset_note"]`` says why.
    """
    m = candidate.measurements
    if not candidate.present_from:
        m["onset_note"] = "no onset window to refine"
        return candidate
    after0 = datetime.fromisoformat(candidate.present_from).date()
    before0 = (datetime.fromisoformat(candidate.absent_until).date()
               if candidate.absent_until else after0 - timedelta(days=365))
    start = (before0 - timedelta(days=pad_days)).isoformat()
    end = min(after0 + timedelta(days=pad_days), date.today()).isoformat()
    radius = max(np.sqrt(max(candidate.area_m2, 1.0) / np.pi), 15.0)
    try:
        series = time_series(candidate.lat, candidate.lon, radius, start, end, max_scenes=max_scenes)
    except Exception as exc:
        m["onset_note"] = f"time series unavailable: {type(exc).__name__}"
        return candidate
    m["series"] = series
    if len(series["dates"]) < 6:
        m["onset_note"] = f"only {len(series['dates'])} clear scenes"
        return candidate
    weights = {"brightness": abs(m.get("d_brightness", 0)) / MIN_STEP["brightness"],
               "ndvi": abs(m.get("d_ndvi", 0)) / MIN_STEP["ndvi"],
               "nbr": abs(m.get("d_nbr", 0)) / MIN_STEP["nbr"]}
    main = max(weights, key=lambda key: weights[key])
    dates = [datetime.fromisoformat(d).date() for d in series["dates"]]
    inside = np.array(series["inside"][main])
    is_early = np.array([d <= before0 for d in dates])
    is_late = np.array([d >= after0 for d in dates])
    if is_early.sum() < 2 or is_late.sum() < 2:
        m["onset_note"] = "too few scenes on one side of the window"
        return candidate
    # Inside-minus-ring contrast cancels weather and season, but fails when
    # the ring changed too (a change wider than the footprint). Then the
    # absolute inside value is used instead.
    chosen = None
    for mode, values in (("contrast", inside - np.array(series["ring"][main])), ("absolute", inside)):
        level0, level1 = float(np.median(values[is_early])), float(np.median(values[is_late]))
        spread = float(np.median(np.abs(values[is_early] - level0))
                       + np.median(np.abs(values[is_late] - level1))) * 1.4826
        if abs(level1 - level0) >= max(3 * spread, 1e-4):
            chosen = (mode, values, level0, level1, spread)
            break
    m["series_feature"] = main
    if chosen is None:
        m["series_shift"] = level1 - level0
        m["series_noise"] = spread
        m["onset_note"] = "per-scene values do not separate before from after"
        return candidate
    mode, contrast, level0, level1, spread = chosen
    m["series_mode"] = mode
    m["series_shift"] = level1 - level0
    m["series_noise"] = spread
    after_like = np.abs(contrast - level1) < np.abs(contrast - level0)
    last_before = None
    for i, flag in enumerate(after_like):
        if flag:
            break
        last_before = i
    first_after = None
    for i in range(len(after_like) - 1, -1, -1):
        if not after_like[i]:
            break
        first_after = i
    if last_before is None or first_after is None or first_after <= last_before:
        m["onset_note"] = "series is not a single clean transition"
        return candidate
    candidate.absent_until = dates[last_before].isoformat()
    candidate.present_from = dates[first_after].isoformat()
    m["onset_window_days"] = (dates[first_after] - dates[last_before]).days
    m["onset_flips"] = int(np.abs(np.diff(after_like.astype(int))).sum())
    return candidate
