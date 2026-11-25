"""Human context: is ordinary human activity already present around the candidate?

A change beside a road, near buildings or in a farming area is far more
likely to be someone's routine work than anything else, even when the exact
feature is not on any map. This check never explains a candidate; it marks
it "inconclusive" so that only genuinely remote changes can reach tier T3.
"""
from __future__ import annotations

from typing import Any

from ..core.models import Candidate, CheckResult

#: Distances and fractions beyond which a place counts as remote.
ROAD_NEAR_M = 300.0
BUILDING_NEAR_M = 1000.0
CONTEXT_RADIUS_M = 1500.0
CROPLAND_SHARE = 0.03
BUILTUP_SHARE = 0.005


def check_context(candidate: Candidate) -> list[CheckResult]:
    """One result, check name "human_context", category "infrastructure".

    Uses the distances already measured by the "osm_infrastructure" check
    (nearest mapped road or track, nearest mapped building) and the land
    cover within 1.5 km. "inconclusive" when a road lies within 300 m, a
    building within 1 km, or the surroundings hold at least 3 % cropland or
    0.5 % built-up land. "does_not_explain" when the place is remote on every
    measure that could be read. "not_run" when none could be read.
    """
    evidence: dict[str, Any] = {}
    reasons: list[str] = []
    measured = 0
    osm = next((c for c in candidate.checks if c.check == "osm_infrastructure"), None)
    if osm is not None and osm.status != "not_run":
        measured += 1
        road = osm.evidence.get("nearest_road_m")
        building = osm.evidence.get("nearest_building_m")
        evidence.update(nearest_road_m=road, nearest_building_m=building,
                        mapped_features_nearby=osm.evidence.get("n_tagged_features"))
        if isinstance(road, (int, float)) and road <= ROAD_NEAR_M:
            reasons.append(f"a mapped road or track is {road:.0f} m away")
        if isinstance(building, (int, float)) and building <= BUILDING_NEAR_M:
            reasons.append(f"a mapped building is {building:.0f} m away")
    try:
        from .landcover import landcover_fractions
        cover = landcover_fractions(candidate.lat, candidate.lon, CONTEXT_RADIUS_M)
        measured += 1
        evidence.update(cropland_share=cover.get("cropland", 0.0), builtup_share=cover.get("builtup", 0.0))
        if cover.get("cropland", 0.0) >= CROPLAND_SHARE:
            reasons.append(f"{cover['cropland']:.0%} of the land within 1.5 km is cropland")
        if cover.get("builtup", 0.0) >= BUILTUP_SHARE:
            reasons.append(f"{cover['builtup']:.1%} of the land within 1.5 km is built-up")
    except Exception as exc:
        evidence["landcover_error"] = type(exc).__name__
    source = "OpenStreetMap distances; ESA WorldCover 2021"
    if not measured:
        return [CheckResult("human_context", "infrastructure", "not_run",
                            "neither map distances nor land cover could be read", source, evidence)]
    if reasons:
        return [CheckResult("human_context", "infrastructure", "inconclusive",
                            "ordinary human activity is present nearby: " + "; ".join(reasons),
                            source, evidence)]
    return [CheckResult("human_context", "infrastructure", "does_not_explain",
                        "remote: no mapped road within 300 m, no mapped building within 1 km, "
                        "and no farmland or built-up land within 1.5 km (maps are incomplete in "
                        "remote regions)", source, evidence)]
