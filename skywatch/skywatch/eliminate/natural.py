"""Ordinary natural processes that produce abrupt surface change.

Each sub-test states its thresholds in its detail text and returns the
numbers it used. Thresholds are deliberately generous towards the mundane
explanation: a candidate must survive all of them to stay unexplained.
"""
from __future__ import annotations

from typing import Any, Callable

import numpy as np

from ..core.models import Candidate, CheckResult

SOURCE = "Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM"


def _result(name: str, status: str, detail: str, **evidence: Any) -> CheckResult:
    return CheckResult(check=name, category="natural", status=status,  # type: ignore[arg-type]
                       detail=detail, source=SOURCE, evidence=evidence)


class _Context:
    """Lazily gathered land cover and terrain for one candidate."""

    def __init__(self, candidate: Candidate) -> None:
        self.c = candidate
        self.m = candidate.measurements
        self.shape = candidate.shape or {}
        self.radius = max(float(np.sqrt(max(candidate.area_m2, 1.0) / np.pi)), 30.0)
        self._landcover: dict[str, float] | None = None
        self._landcover_wide: dict[str, float] | None = None
        self._terrain: dict[str, Any] | None = None
        self.errors: dict[str, str] = {}

    def landcover(self, wide: bool = False) -> dict[str, float] | None:
        attr = "_landcover_wide" if wide else "_landcover"
        if getattr(self, attr) is None and ("landcover" not in self.errors):
            try:
                from .landcover import landcover_fractions
                radius = self.radius * 4 if wide else self.radius
                setattr(self, attr, landcover_fractions(self.c.lat, self.c.lon, max(radius, 60.0)))
            except Exception as exc:
                self.errors["landcover"] = type(exc).__name__
        return getattr(self, attr)

    def terrain(self) -> dict[str, Any] | None:
        if self._terrain is None and "terrain" not in self.errors:
            try:
                from ..detect.terrain import terrain_context
                self._terrain = terrain_context(self.c.lat, self.c.lon, max(self.radius, 90.0))
            except Exception as exc:
                self.errors["terrain"] = type(exc).__name__
        return self._terrain

    def d(self, key: str) -> float:
        return float(self.m.get(key, 0.0) or 0.0)


def _agriculture(x: _Context) -> CheckResult:
    name = "natural:agriculture"
    diameter = float(x.shape.get("equivalent_diameter_m", 0.0))
    circular = float(x.shape.get("circularity", 0.0))
    lc = x.landcover()
    crop = (lc or {}).get("cropland", 0.0)
    crop_near = (x.landcover(wide=True) or {}).get("cropland", 0.0)
    evidence = dict(diameter_m=diameter, circularity=circular, d_ndvi=x.d("d_ndvi"),
                    cropland_fraction=crop, cropland_nearby_fraction=crop_near)
    if lc is not None and crop >= 0.3:
        return _result(name, "explains", f"{crop:.0%} of the footprint is mapped cropland", **evidence)
    if 250 <= diameter <= 1100 and circular >= 0.8 and abs(x.d("d_ndvi")) >= 0.08:
        return _result(name, "explains",
                       f"a near-perfect disc {diameter:.0f} m across with a vegetation change: "
                       "the size and shape of a centre-pivot irrigation field", **evidence)
    if lc is not None and crop_near >= 0.15 and abs(x.d("d_ndvi")) >= 0.08:
        return _result(name, "inconclusive",
                       f"vegetation change with {crop_near:.0%} cropland in the surroundings", **evidence)
    if lc is None:
        return _result(name, "not_run", "land cover unavailable: " + x.errors.get("landcover", ""), **evidence)
    return _result(name, "does_not_explain", "no cropland and not a pivot-sized disc", **evidence)


def _seasonal(x: _Context) -> CheckResult:
    name = "natural:recurring_cycle"
    series = x.m.get("series")
    if not series or len(series.get("dates", [])) < 8:
        return _result(name, "not_run", "no per-scene series to test for a recurring cycle")
    flips = x.m.get("onset_flips")
    note = x.m.get("onset_note", "")
    evidence = dict(flips=flips, onset_note=note, n_scenes=len(series["dates"]))
    if flips is not None and flips >= 5:
        return _result(name, "explains",
                       f"the feature switches state {flips} times in the scene-by-scene record: "
                       "a recurring (seasonal or wetting) cycle, not a single event", **evidence)
    if (flips is not None and flips >= 3) or "not a single clean transition" in note:
        return _result(name, "inconclusive", "the scene-by-scene record is not a single transition", **evidence)
    return _result(name, "does_not_explain", "the record shows one transition, not a cycle", **evidence)


def _water(x: _Context) -> CheckResult:
    name = "natural:surface_water"
    lc = x.landcover()
    terrain = x.terrain()
    wet = ((lc or {}).get("water", 0.0) + (lc or {}).get("wetland", 0.0))
    d_bri, d_swir, d_ndvi = x.d("d_brightness"), x.d("d_swir"), x.d("d_ndvi")
    wetting = d_bri < -0.03 and d_swir < -0.05 and d_ndvi < 0.08
    drying = d_bri > 0.03 and d_swir > 0.05 and d_ndvi < 0.05
    slope = float((terrain or {}).get("slope_deg", 99.0) or 99.0)
    basin = terrain is not None and slope < 1.5 and float(terrain.get("tpi", 0.0) or 0.0) <= 0.5
    evidence = dict(water_fraction=wet, d_brightness=d_bri, d_swir=d_swir, slope_deg=slope,
                    flat_basin=basin, wetting_signature=wetting, drying_signature=drying)
    if lc is not None and wet >= 0.2:
        return _result(name, "explains", f"{wet:.0%} of the footprint is mapped water or wetland: "
                       "water-level change", **evidence)
    # Water comes and goes and has ragged edges. A change that has persisted
    # for years or has a geometric outline is not accepted as water: solar
    # panels and paving darken the same bands.
    short_lived = x.m.get("kind") in ("transient", "latest_year", "event_window") \
        or float(x.m.get("recovery_fraction", 0.0) or 0.0) >= 0.5
    ragged = float(x.shape.get("regularity", 0.0)) < 0.5
    evidence.update(short_lived=short_lived, ragged_outline=ragged)
    if (wetting or drying) and basin and short_lived and ragged:
        return _result(name, "explains",
                       "visible and short-wave infrared changed together on a flat basin floor, "
                       "with a ragged outline and no lasting persistence: the signature of an "
                       "ephemeral lake or playa " + ("flooding" if wetting else "drying"),
                       **evidence)
    if wetting or drying:
        return _result(name, "inconclusive", "moisture-like spectral change (wetting or drying)", **evidence)
    if lc is None and terrain is None:
        return _result(name, "not_run", "land cover and terrain unavailable", **evidence)
    return _result(name, "does_not_explain", "no water mapped and no moisture signature", **evidence)


def _snow(x: _Context) -> CheckResult:
    name = "natural:snow_ice"
    lc = x.landcover()
    terrain = x.terrain()
    snow = (lc or {}).get("snow", 0.0)
    d_bri, d_swir = x.d("d_brightness"), x.d("d_swir")
    signature = (d_bri > 0.08 and d_swir < -0.02) or (d_bri < -0.08 and d_swir > 0.02)
    elevation = float((terrain or {}).get("elevation_m", 0.0) or 0.0)
    cold_place = abs(x.c.lat) >= 55 or elevation >= 3000
    evidence = dict(snow_fraction=snow, d_brightness=d_bri, d_swir=d_swir, elevation_m=elevation,
                    latitude=x.c.lat, snow_signature=signature)
    if lc is not None and snow >= 0.2:
        return _result(name, "explains", f"{snow:.0%} of the footprint is mapped snow or ice", **evidence)
    if signature and cold_place:
        return _result(name, "explains",
                       "brightness and short-wave infrared moved in opposite directions (snow is "
                       "bright in visible light and dark in short-wave infrared) at high latitude "
                       "or altitude: a snow or ice patch appearing or melting", **evidence)
    if signature:
        return _result(name, "inconclusive", "snow-like spectral signature", **evidence)
    return _result(name, "does_not_explain", "no snow mapped and no snow signature", **evidence)


def _mass_movement(x: _Context) -> CheckResult:
    name = "natural:mass_movement"
    terrain = x.terrain()
    if terrain is None:
        return _result(name, "not_run", "terrain unavailable: " + x.errors.get("terrain", ""))
    slope = float(terrain.get("slope_deg", 0.0) or 0.0)
    slope_max = float(terrain.get("slope_max_deg", slope) or slope)
    elongation = float(x.shape.get("elongation", 1.0))
    evidence = dict(slope_deg=slope, slope_max_deg=slope_max, elongation=elongation)
    if slope >= 25 and elongation >= 2:
        return _result(name, "explains",
                       f"an elongated scar on a {slope:.0f} degree slope: landslide, rockfall, "
                       "avalanche or debris flow", **evidence)
    if slope_max >= 25:
        return _result(name, "inconclusive", f"slopes up to {slope_max:.0f} degrees in the footprint", **evidence)
    return _result(name, "does_not_explain", f"gentle ground ({slope:.0f} degrees)", **evidence)


def _sand(x: _Context) -> CheckResult:
    name = "natural:wind_blown_sand"
    lc = x.landcover()
    if lc is None:
        return _result(name, "not_run", "land cover unavailable")
    bare = lc.get("bare", 0.0)
    regular = float(x.shape.get("regularity", 0.0))
    brightness_only = abs(x.d("d_brightness")) >= 0.03 and abs(x.d("d_ndvi")) < 0.03
    evidence = dict(bare_fraction=bare, regularity=regular, brightness_only=brightness_only)
    if bare >= 0.8 and brightness_only and regular < 0.5:
        return _result(name, "inconclusive",
                       "an irregular brightness-only change on bare ground: moving sand, dust or a "
                       "wetted surface is the likely cause", **evidence)
    return _result(name, "does_not_explain", "not an irregular brightness-only change on bare ground", **evidence)


def _periglacial(x: _Context) -> CheckResult:
    name = "natural:permafrost_or_lake_drainage"
    terrain = x.terrain()
    elevation = float((terrain or {}).get("elevation_m", 0.0) or 0.0)
    cold = abs(x.c.lat) >= 60 or elevation >= 4000
    lc = x.landcover(wide=True)
    water_near = ((lc or {}).get("water", 0.0) + (lc or {}).get("wetland", 0.0))
    evidence = dict(latitude=x.c.lat, elevation_m=elevation, water_nearby_fraction=water_near)
    if not cold:
        return _result(name, "does_not_explain", "not a permafrost latitude or altitude", **evidence)
    if lc is None:
        return _result(name, "not_run", "land cover unavailable in a permafrost region", **evidence)
    if water_near >= 0.05:
        return _result(name, "inconclusive",
                       f"permafrost terrain with {water_near:.0%} water or wetland around the footprint: "
                       "lake drainage, thaw slump or shoreline change is likely", **evidence)
    return _result(name, "does_not_explain", "permafrost region but no water around the footprint", **evidence)


def _fluvial(x: _Context) -> CheckResult:
    name = "natural:river_or_coast"
    lc = x.landcover(wide=True)
    if lc is None:
        return _result(name, "not_run", "land cover unavailable")
    water_near = lc.get("water", 0.0) + lc.get("wetland", 0.0) + lc.get("mangrove", 0.0)
    elongation = float(x.shape.get("elongation", 1.0))
    evidence = dict(water_nearby_fraction=water_near, elongation=elongation)
    if water_near >= 0.15:
        return _result(name, "explains" if elongation >= 2.5 else "inconclusive",
                       f"{water_near:.0%} of the surroundings is water: channel migration, flood "
                       "deposit or shoreline change", **evidence)
    return _result(name, "does_not_explain", "no significant water around the footprint", **evidence)


def _volcanic(x: _Context) -> CheckResult:
    """Fresh lava, ash or fumarole activity near a catalogued volcano."""
    name = "natural:volcanic"
    wikidata = next((c for c in x.c.checks if c.check == "wikidata_nearby"), None)
    if wikidata is None or wikidata.status == "not_run":
        return _result(name, "not_run", "no catalogue of volcanoes was consulted")
    volcanoes = [item for item in (wikidata.evidence.get("nearest") or [])
                 if item.get("category") == "volcano_or_geothermal"]
    volcanoes += [item for item in (wikidata.evidence.get("explaining") or [])
                  if item.get("category") == "volcano_or_geothermal"]
    if not volcanoes:
        return _result(name, "does_not_explain", "no catalogued volcano within 10 km")
    nearest = min(volcanoes, key=lambda item: item.get("distance_km", 99.0))
    distance = float(nearest.get("distance_km", 99.0))
    lc = x.landcover()
    bare = (lc or {}).get("bare", 0.0)
    d_bri = x.d("d_brightness")
    evidence = dict(volcano=nearest.get("label"), distance_km=distance, bare_fraction=bare, d_brightness=d_bri)
    if distance <= 15.0 and bare >= 0.6 and d_bri <= -0.03:
        return _result(name, "explains",
                       f"a darkening on bare ground {distance:.1f} km from {nearest.get('label')}: "
                       "fresh lava or scoria", **evidence)
    if distance <= 15.0:
        return _result(name, "inconclusive",
                       f"{nearest.get('label')} is {distance:.1f} km away: volcanic activity "
                       "(lava, ash, fumaroles, salt crusts) is likely", **evidence)
    return _result(name, "does_not_explain", f"nearest volcano {distance:.1f} km away", **evidence)


def _regional_pattern(x: _Context) -> CheckResult:
    """Same signature, same year, several unrelated places in the region.

    Reads the census ``regional.annotate_siblings`` stored. Explains with
    ``EXPLAIN_SIBLINGS`` or more others unless the outline is regular (a
    rectilinear footprint may be one of several built things); suggestive from
    ``SUGGEST_SIBLINGS``.
    """
    from .regional import EXPLAIN_SIBLINGS, MAGNITUDE_RATIO, MIN_COSINE, SUGGEST_SIBLINGS

    info = x.m.get("regional_siblings")
    if not info:
        return _result("natural:regional_pattern", "not_run",
                       "no region-wide sibling census (not a yearly optical candidate, or census not computed)")
    n, compared, year, spread = int(info["count"]), int(info["compared"]), info.get("year"), info.get("spread_km", 0.0)
    regular = float(x.shape.get("rectangularity", 0.0)) >= 0.8 and float(x.shape.get("straight_edge_fraction", 0.0)) >= 0.6
    same = (f"{n} of {compared} other yearly candidates in this region changed the same way in {year} "
            f"(spectral direction within cosine {MIN_COSINE}, size within {MAGNITUDE_RATIO}x), spread over {spread} km")
    if n >= EXPLAIN_SIBLINGS and not regular:
        return _result("natural:regional_pattern", "explains",
                       f"regional pattern: {same}; a change that recurs across a region is a regional process "
                       "(rain, greening, blown sand, moisture or the sensor), not a local event",
                       siblings=n, compared=compared, year=year, spread_km=spread, ids=info.get("ids", []))
    if n >= SUGGEST_SIBLINGS:
        why = "; its regular outline kept it from being explained by that alone" if regular else ""
        return _result("natural:regional_pattern", "inconclusive", f"possible regional pattern: {same}{why}",
                       siblings=n, compared=compared, year=year, spread_km=spread, ids=info.get("ids", []))
    return _result("natural:regional_pattern", "does_not_explain", same, siblings=n, compared=compared, year=year)


_SUBTESTS: tuple[Callable[[_Context], CheckResult], ...] = (
    _agriculture, _seasonal, _water, _snow, _mass_movement, _sand, _periglacial, _fluvial, _volcanic,
    _regional_pattern)


def check_natural(candidate: Candidate) -> list[CheckResult]:
    """Umbrella "natural_process" plus one result per sub-test ("natural:...").

    "explains" when any sub-test explains; "inconclusive" when any is
    suggestive; "does_not_explain" when at least four sub-tests ran and all
    were clean; otherwise "not_run".
    """
    context = _Context(candidate)
    subs: list[CheckResult] = []
    for test in _SUBTESTS:
        try:
            subs.append(test(context))
        except Exception as exc:
            subs.append(_result("natural:" + test.__name__.strip("_"), "not_run",
                                f"{type(exc).__name__}: {str(exc)[:120]}"))
    statuses = {s.check: s.status for s in subs}
    ran = [s for s in subs if s.status != "not_run"]
    explaining = [s for s in subs if s.status == "explains"]
    if explaining:
        status, detail = "explains", explaining[0].detail
    elif any(s.status == "inconclusive" for s in subs):
        status = "inconclusive"
        detail = "; ".join(s.detail for s in subs if s.status == "inconclusive")
    elif len(ran) >= 4:
        status, detail = "does_not_explain", f"{len(ran)} natural-process tests ran clean"
    else:
        status, detail = "not_run", f"only {len(ran)} of {len(subs)} natural-process tests could run"
    umbrella = CheckResult(check="natural_process", category="natural", status=status,  # type: ignore[arg-type]
                           detail=detail, source=SOURCE,
                           evidence={"sub_checks": statuses, "data_errors": context.errors})
    return [umbrella, *subs]
