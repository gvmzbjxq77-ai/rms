"""Sensor and compositing artefact screen.

Yearly composites can fake a change: a cloud or shadow that slipped past the
mask, a composite built from a single scene, or terrain shadow that moved
because the scenes were taken at different sun angles. These tests look for
positive evidence of such artefacts and for independent per-scene support.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

import numpy as np

from ..core.models import Candidate, CheckResult

SOURCE = "Sentinel-2 per-scene series and composite metadata"


def _result(name: str, status: str, detail: str, **evidence: Any) -> CheckResult:
    return CheckResult(check=name, category="artefact", status=status,  # type: ignore[arg-type]
                       detail=detail, source=SOURCE, evidence=evidence)


def _per_scene_support(candidate: Candidate) -> CheckResult:
    """Do individual scenes, not just the composite, show the change?"""
    m = candidate.measurements
    series = m.get("series")
    name = "artefact:per_scene_support"
    if not series or len(series.get("dates", [])) < 6 or not candidate.present_from:
        return _result(name, "not_run", "no per-scene series available for this candidate")
    feature = m.get("series_feature")
    if feature is None:
        steps = {"brightness": abs(m.get("d_brightness", 0)) / 0.03,
                 "ndvi": abs(m.get("d_ndvi", 0)) / 0.08, "nbr": abs(m.get("d_nbr", 0)) / 0.08}
        feature = max(steps, key=lambda key: steps[key])
    expected = float(m.get({"brightness": "d_brightness", "ndvi": "d_ndvi", "nbr": "d_nbr"}[feature], 0.0))
    dates = [datetime.fromisoformat(d).date() for d in series["dates"]]
    inside = np.array(series["inside"][feature])
    ring = np.array(series["ring"][feature])
    kind = m.get("kind", "step")
    break_year = int(m.get("break_year", datetime.fromisoformat(candidate.present_from).year))
    composite_dates = (m.get("composite_dates") or {}).get(str(break_year), [])
    first_after = min(composite_dates) if composite_dates else candidate.present_from
    before_cut = datetime.fromisoformat(candidate.absent_until).date() if candidate.absent_until else None
    is_before = np.array([before_cut is not None and d <= before_cut for d in dates])
    if is_before.sum() < 2:
        return _result(name, "not_run", "too few clear scenes before the change to form a baseline")
    after_start = datetime.fromisoformat(first_after).date()
    if kind == "step":
        window = np.array([d >= after_start for d in dates])
    else:
        window = np.array([abs((d - after_start).days) <= 100 for d in dates])
    if window.sum() < 2:
        return _result(name, "inconclusive",
                       "fewer than two clear scenes in the period when the change should be visible",
                       n_scenes=int(window.sum()))
    # Test the inside-minus-ring contrast and the absolute inside value, and
    # keep whichever shows the change best: a change wider than the footprint
    # cancels out of the contrast but not out of the absolute value.
    best: tuple[float, str, float, float, np.ndarray] | None = None
    for mode, values in (("contrast", inside - ring), ("absolute", inside)):
        before = values[is_before]
        base = float(np.median(before))
        noise = max(float(np.median(np.abs(before - base)) * 1.4826), 0.25 * abs(expected), 1e-4)
        later = values[window]
        shifted = (np.sign(expected) * (later - base)) >= max(2.0 * noise, 0.4 * abs(expected))
        if best is None or shifted.mean() > best[0]:
            best = (float(shifted.mean()), mode, base, noise, shifted)
    assert best is not None
    share, mode, base, noise, shifted = best
    later = inside[window]
    evidence = dict(feature=feature, mode=mode, expected_shift=expected, baseline=base, noise=noise,
                    scenes_checked=int(later.size), scenes_showing_change=int(shifted.sum()),
                    share=share)
    if kind == "step":
        if share >= 0.7 and shifted.sum() >= 3:
            return _result(name, "does_not_explain",
                           f"{int(shifted.sum())} of {later.size} later scenes independently show the change",
                           **evidence)
        if share <= 0.2 and later.size >= 4:
            return _result(name, "explains",
                           f"only {int(shifted.sum())} of {later.size} later scenes show the change: "
                           "it exists in the yearly composite but not in the individual images "
                           "(cloud, shadow or compositing artefact)", **evidence)
        return _result(name, "inconclusive",
                       f"{int(shifted.sum())} of {later.size} later scenes show the change", **evidence)
    if shifted.sum() >= 2:
        return _result(name, "does_not_explain",
                       f"{int(shifted.sum())} separate scenes show the short-lived change", **evidence)
    if shifted.sum() == 0 and later.size >= 3:
        return _result(name, "explains",
                       f"none of {later.size} individual scenes around that time shows the change: "
                       "compositing artefact", **evidence)
    return _result(name, "inconclusive",
                   f"only {int(shifted.sum())} of {later.size} scenes shows the short-lived change; "
                   "a single-scene feature may be a residual cloud or shadow", **evidence)


def _bracketing_dates(composites: dict[str, list[str]], year: Any) -> tuple[list[str], list[str]] | None:
    """The scene dates of the composites just before and at the break.

    Yearly candidates store composites by year; event-window candidates store
    a ``before`` and an ``after`` composite. None when the year is unknown to
    the yearly layout.
    """
    if "before" in composites or "after" in composites:
        return list(composites.get("before", [])), list(composites.get("after", []))
    years = sorted(int(y) for y in composites)
    if int(year) not in years:
        return None
    index = years.index(int(year))
    before = composites.get(str(years[index - 1]), []) if index > 0 else []
    return list(before), list(composites.get(str(year), []))


def _observation_count(candidate: Candidate) -> CheckResult:
    """Were the bracketing composites built from enough separate dates?"""
    m = candidate.measurements
    name = "artefact:observation_count"
    composites = m.get("composite_dates") or {}
    year = m.get("break_year")
    if not composites or year is None:
        return _result(name, "not_run", "no composite metadata on this candidate")
    bracket = _bracketing_dates(composites, year)
    if bracket is None:
        return _result(name, "not_run", "the break year is not among the composite dates")
    before_dates, after_dates = bracket
    n_before, n_after = len(before_dates), len(after_dates)
    # An event window has two composites by construction; six is the yearly floor.
    valid_years = 6 if "before" in composites else int(m.get("n_valid_years", len(composites)))
    evidence = dict(dates_before=n_before, dates_after=n_after, valid_years=valid_years)
    if min(n_before, n_after) < 2 or valid_years < 6:
        return _result(name, "inconclusive",
                       f"weak composites: {n_before} date(s) before, {n_after} after, "
                       f"{valid_years} valid years", **evidence)
    return _result(name, "does_not_explain",
                   f"composites use {n_before} and {n_after} separate dates; {valid_years} valid years",
                   **evidence)


def _terrain_shadow(candidate: Candidate) -> CheckResult:
    """Darkening on steep ground between scenes taken at different sun angles."""
    m = candidate.measurements
    name = "artefact:terrain_shadow"
    try:
        from ..detect.terrain import terrain_context
        radius = max(float(np.sqrt(max(candidate.area_m2, 1.0) / np.pi)), 90.0)
        ctx = terrain_context(candidate.lat, candidate.lon, radius)
    except Exception as exc:
        return _result(name, "not_run", f"terrain data unavailable: {type(exc).__name__}")
    slope_max = float(ctx.get("slope_max_deg") or ctx.get("slope_deg") or 0.0)
    composites = m.get("composite_dates") or {}
    year = m.get("break_year")
    doy_gap = None
    bracket = _bracketing_dates(composites, year) if composites and year is not None else None
    if bracket is not None and bracket[0] and bracket[1]:
        def mean_doy(values: list[str]) -> float:
            return float(np.mean([date.fromisoformat(v).timetuple().tm_yday for v in values]))
        doy_gap = abs(mean_doy(bracket[1]) - mean_doy(bracket[0]))
    darkening_only = m.get("d_brightness", 0.0) < -0.02 and abs(m.get("d_ndvi", 0.0)) < 0.06
    evidence = dict(slope_max_deg=slope_max, day_of_year_gap=doy_gap, darkening_only=darkening_only)
    if slope_max >= 30 and darkening_only and doy_gap is not None and doy_gap >= 25:
        return _result(name, "explains",
                       f"steep ground (up to {slope_max:.0f} deg), darkening only, and the before and "
                       f"after images are {doy_gap:.0f} days apart in the season: terrain shadow", **evidence)
    if slope_max >= 25 and darkening_only:
        return _result(name, "inconclusive",
                       f"steep ground (up to {slope_max:.0f} deg) with darkening only: shadow possible",
                       **evidence)
    return _result(name, "does_not_explain", "not a steep-slope darkening pattern", **evidence)


def _widespread(candidate: Candidate) -> CheckResult:
    """Is the candidate one of many changes that hit its neighbourhood in the same year?"""
    name = "artefact:widespread_change"
    crowding = candidate.measurements.get("crowding")
    if crowding is None:
        return _result(name, "not_run", "no neighbourhood statistics on this candidate")
    if crowding >= 0.05:
        return _result(name, "inconclusive",
                       f"{crowding:.0%} of the surrounding 3 km also changed in the same year: "
                       "weather, a seasonal effect or an image-processing change is likely, "
                       "though a large site built in one year looks the same", crowding=crowding)
    return _result(name, "does_not_explain",
                   f"isolated: only {crowding:.1%} of the surrounding 3 km changed in the same year",
                   crowding=crowding)


#: A normalised-difference index lies in [-1, 1], so no real change of one
#: can exceed this; a larger value means a near-zero denominator.
INDEX_CHANGE_LIMIT = 2.0


def _index_range(candidate: Candidate) -> CheckResult:
    """A vegetation or burn index change beyond its physical range."""
    m = candidate.measurements
    name = "artefact:index_range"
    worst = max(abs(float(m.get(k, 0.0) or 0.0)) for k in ("d_ndvi", "d_nbr"))
    if worst > INDEX_CHANGE_LIMIT:
        return _result(name, "explains",
                       f"an index change of {worst:.2f} is outside the physical range of a normalised-difference "
                       f"index (at most {INDEX_CHANGE_LIMIT:.0f}): the denominator was near zero, which happens over "
                       "dark water, deep shadow, snow or a bad pixel, not over a real surface change",
                       worst_index_change=worst)
    return _result(name, "does_not_explain", f"index changes within range (largest {worst:.2f})",
                   worst_index_change=worst)


def check_artefacts(candidate: Candidate) -> list[CheckResult]:
    """Umbrella "artefact_screen" plus its sub-results (names start "artefact:").

    "explains" when any sub-test demonstrates an artefact; "inconclusive" when
    any is inconclusive; "does_not_explain" when at least the per-scene test
    ran and nothing was found; "not_run" when the per-scene test could not run.
    """
    subs = [_per_scene_support(candidate), _observation_count(candidate),
            _terrain_shadow(candidate), _widespread(candidate), _index_range(candidate)]
    statuses = {s.check: s.status for s in subs}
    explaining = [s for s in subs if s.status == "explains"]
    if explaining:
        status, detail = "explains", explaining[0].detail
    elif statuses["artefact:per_scene_support"] == "not_run":
        status, detail = "not_run", "per-scene support could not be tested: " + subs[0].detail
    elif any(s.status == "inconclusive" for s in subs):
        status = "inconclusive"
        detail = "; ".join(s.detail for s in subs if s.status == "inconclusive")
    else:
        status, detail = "does_not_explain", subs[0].detail
    umbrella = CheckResult(check="artefact_screen", category="artefact", status=status,  # type: ignore[arg-type]
                           detail=detail, source=SOURCE, evidence={"sub_checks": statuses})
    return [umbrella, *subs]
