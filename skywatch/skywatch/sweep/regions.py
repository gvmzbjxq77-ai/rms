"""Where the pilot sweep looks: blind regions and control regions.

Coverage honesty: the blind regions together cover a few tens of thousands
of square kilometres, a tiny share of Earth's roughly 149 million km2 of
land (see ``coverage``). This is a pilot sample, not a global search.

Blind regions are remote places chosen with no prior hypothesis. Control
regions hold known, conventional, datable features that a working pipeline
must find and then explain, plus "pristine" places declared in advance to
contain nothing, which measure the raw false-positive rate. Seeded regions
come from witness reports (``skywatch.reports.ingest.seeded_regions``).

Detectable window: yearly composites run from 2018 and a step needs two
years on each side, so persistent changes can be dated from 2020 to 2025,
single-year changes from 2019, and changes in the newest year are reported
with unknown persistence. Dated sites (seeded and some controls) are also
examined with the event-window detector around their date.
"""
from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from ..core import io
from ..core.models import Candidate, Region

EARTH_LAND_KM2 = 149.0e6


def _box(lat: float, lon: float, half_km: float = 20.0) -> tuple[float, float, float, float]:
    return io.point_bbox(lat, lon, half_km * 1000.0)


def _blind(rid: str, name: str, lat: float, lon: float, season: tuple[str, str],
           biome: str, notes: str = "") -> Region:
    return Region(id=rid, name=name, bbox=_box(lat, lon), kind="blind", biome=biome,
                  season=season, notes=notes)


def _control(rid: str, name: str, lat: float, lon: float, half_km: float,
             season: tuple[str, str], biome: str, expected: str,
             expect: dict[str, Any]) -> Region:
    return Region(id=rid, name=name, bbox=_box(lat, lon, half_km), kind="control",
                  biome=biome, season=season, expected=expected, expect=expect)


_AUTUMN = ("10-01", "11-30")      # Sahara / Arabia: clear, low dust
_NH_SUMMER = ("07-01", "09-15")
_ARCTIC = ("07-10", "08-31")
_SH_WINTER = ("06-15", "09-15")   # southern dry season

REGIONS: list[Region] = [
    # ---- hyper-arid deserts -------------------------------------------------
    _blind("B01-TENERE", "Tenere, Niger", 18.5, 11.5, _AUTUMN, "desert"),
    _blind("B02-BILMA", "Erg of Bilma, Niger/Chad", 18.7, 15.3, _AUTUMN, "desert"),
    _blind("B03-GILF", "Gilf Kebir plateau, Egypt", 23.3, 25.9, _AUTUMN, "desert"),
    _blind("B04-TANEZROUFT", "Tanezrouft, Algeria", 22.8, 1.6, _AUTUMN, "desert"),
    _blind("B05-RUBALKHALI", "Rub al Khali, Saudi Arabia", 19.6, 49.6, _AUTUMN, "desert"),
    _blind("B06-LUT", "Dasht-e Lut, Iran", 30.4, 58.9, ("09-01", "10-31"), "desert"),
    _blind("B07-TAKLAMAKAN", "Western Taklamakan, China", 38.6, 80.9, _NH_SUMMER, "desert"),
    _blind("B08-GOBI", "Trans-Altai Gobi, Mongolia", 43.0, 98.5, _NH_SUMMER, "desert"),
    _blind("B09-GIBSON", "Gibson Desert, Australia", -24.5, 126.0, _SH_WINTER, "desert"),
    _blind("B10-SIMPSON", "Simpson Desert, Australia", -25.0, 137.5, _SH_WINTER, "desert"),
    _blind("B11-ATACAMA", "Atacama coastal range, Chile", -25.5, -69.9, ("03-01", "05-31"), "desert"),
    _blind("B12-NAMIB", "Namib sand sea, Namibia", -24.5, 15.3, ("05-01", "08-31"), "desert"),
    _blind("B13-MAPIMI", "Bolson de Mapimi, Mexico", 26.7, -103.7, ("03-15", "05-31"), "desert",
           "Area of long-standing local anomaly folklore ('Zone of Silence'); chosen as a blind region, not a seeded one."),
    _blind("B14-USTYURT", "Ustyurt plateau, Kazakhstan/Uzbekistan", 43.6, 56.2, ("06-01", "08-31"), "desert"),
    _blind("B15-BETPAKDALA", "Betpak-Dala steppe, Kazakhstan", 46.0, 69.5, ("06-01", "08-31"), "steppe"),
    _blind("B16-NULLARBOR", "Nullarbor Plain, Australia", -30.5, 127.5, _SH_WINTER, "desert"),
    _blind("B17-KALAHARI", "Central Kalahari, Botswana", -22.3, 23.8, ("06-01", "08-31"), "savanna"),
    # ---- high plateaus --------------------------------------------------------
    _blind("B18-CHANGTANG", "Changtang, northern Tibet", 35.0, 86.0, ("08-15", "10-15"), "plateau"),
    _blind("B19-PUNA", "Puna de Atacama, Argentina", -25.2, -67.6, ("04-01", "06-15"), "plateau"),
    _blind("B20-PAMIR", "Eastern Pamir, Tajikistan", 38.3, 73.9, ("08-01", "09-30"), "plateau"),
    # ---- tundra and polar margins --------------------------------------------
    _blind("B21-TAYMYR", "Taymyr Peninsula, Russia", 74.5, 98.0, _ARCTIC, "tundra"),
    _blind("B22-PUTORANA", "Putorana Plateau, Russia", 69.5, 96.0, _ARCTIC, "tundra"),
    _blind("B23-BARRENLANDS", "Barrenlands, Nunavut, Canada", 65.0, -100.0, _ARCTIC, "tundra"),
    _blind("B24-NORTHSLOPE", "North Slope interior, Alaska", 68.8, -156.0, ("07-01", "08-31"), "tundra"),
    _blind("B25-EASTGREENLAND", "Ice-free East Greenland", 72.5, -25.5, ("07-15", "08-31"), "polar"),
    _blind("B26-DEVON", "Devon Island, Canada (uninhabited)", 75.3, -87.0, ("07-15", "08-25"), "polar island"),
    # ---- forest and steppe ----------------------------------------------------
    _blind("B27-EVENKIA", "Evenkia taiga, Siberia", 64.0, 104.0, ("06-15", "08-31"), "taiga"),
    _blind("B28-AMAZON", "Jurua-Purus interfluve, Amazonas, Brazil", -5.5, -66.0, ("07-01", "09-15"), "rainforest"),
    _blind("B29-PATAGONIA", "Patagonian steppe, Santa Cruz, Argentina", -47.5, -70.5, ("12-15", "02-28"), "steppe"),

    # ---- controls with a known conventional feature ---------------------------
    _control("C01-BENBAN", "Benban solar park, Egypt", 24.456, 32.739, 9.0, ("06-01", "08-31"), "desert",
             "A 37 km2 solar park beside expanding irrigation farms. The park itself was built in 2018-2019, before the earliest change this detector can date (2020), so the test here is the later construction in and around it: it must be detected and explained as mapped infrastructure or farmland.",
             {"min_candidates": 1, "target": {"lat": 24.456, "lon": 32.739, "radius_m": 6000},
              "break_year": None, "explained_by": ["osm_infrastructure", "wikidata_nearby", "landcover"]}),
    _control("C02-OWEINAT", "Sharq El Owainat pivot farms, Egypt", 22.58, 28.72, 12.0, ("12-01", "02-28"), "desert",
             "Centre-pivot irrigation circles about 800 m across in open desert, with new circles added over the years. Must be explained as agriculture.",
             {"min_candidates": 1, "target": None, "break_year": None,
              "explained_by": ["landcover", "natural_process", "osm_infrastructure"]}),
    _control("C03-OYUTOLGOI", "Oyu Tolgoi copper mine, Mongolia", 43.01, 106.85, 12.0, _NH_SUMMER, "desert",
             "A large open-pit and underground mine whose pit, waste dumps and tailings grew through 2017-2025. Must be explained as a mapped mine.",
             {"min_candidates": 1, "target": {"lat": 43.01, "lon": 106.85, "radius_m": 9000},
              "break_year": None, "explained_by": ["osm_infrastructure", "wikidata_nearby"]}),
    _control("C04-DOMEFIRE", "Dome Fire scar, Mojave, USA", 35.30, -115.58, 12.0, ("09-01", "10-31"), "desert shrub",
             "A 175 km2 wildfire that burned Joshua-tree woodland from 15 August 2020. Must be detected with a 2020 break and explained by fire history.",
             {"min_candidates": 1, "target": {"lat": 35.30, "lon": -115.58, "radius_m": 9000},
              "break_year": [2020, 2021], "explained_by": ["fire_history"]}),
    _control("C05-YUCCAFLAT", "Yucca Flat crater field, Nevada, USA", 37.11, -116.05, 10.0, ("06-01", "08-31"), "desert",
             "Hundreds of subsidence craters from underground nuclear tests (static since 1992) inside an active test site. Any change found here must be explained by the test-range catalogue.",
             {"min_candidates": 0, "target": None, "break_year": None,
              "explained_by": ["military_or_rocket_range"]}),
    _control("C06-MU5735", "China Eastern 5735 crash site, Guangxi, China", 23.324, 111.112, 5.0, ("09-15", "12-31"), "forest",
             "A Boeing 737 struck a forested hillside on 21 March 2022, leaving a scar and a cleared recovery area. A real aircraft crash scar: must be detected with a 2022 break and explained by a public record of the crash (the accident catalogue, Wikidata, or the memorial mapped at the site in OpenStreetMap).",
             {"min_candidates": 1, "target": {"lat": 23.324, "lon": 111.112, "radius_m": 800},
              "break_year": [2022], "event_date": "2022-03-21", "detector": "optical_event",
              "explained_by": ["aviation_accident", "wikidata_nearby", "osm_infrastructure"]}),
    _control("C07-VOSTOCHNY", "Vostochny Cosmodrome, Russia", 51.88, 128.33, 12.0, ("06-15", "09-15"), "taiga",
             "A launch complex with a second pad built between 2019 and 2023. Must be explained by the launch-site catalogue.",
             {"min_candidates": 1, "target": {"lat": 51.88, "lon": 128.33, "radius_m": 10000},
              "break_year": None, "explained_by": ["military_or_rocket_range", "osm_infrastructure", "wikidata_nearby"]}),
    _control("C08-ERTAALE", "Erta Ale volcano, Ethiopia", 13.60, 40.66, 12.0, ("11-01", "01-31"), "volcanic desert",
             "An active shield volcano with a lava lake and lava flows erupted from 2017. Surface and thermal changes must be explained as volcanic.",
             {"min_candidates": 1, "target": {"lat": 13.60, "lon": 40.66, "radius_m": 12000},
              "break_year": None, "explained_by": ["wikidata_nearby", "osm_infrastructure", "natural_process"]}),
    # ---- pristine controls: declared in advance to contain nothing ------------
    _control("C09-SERIRTIBESTI", "Serir Tibesti gravel plain, Libya", 24.5, 17.5, 20.0, _AUTUMN, "desert",
             "A featureless gravel plain. Expect almost no candidates; every candidate here counts as a false positive of the detector.",
             {"min_candidates": 0, "max_candidates": 5, "target": None, "break_year": None, "explained_by": None}),
    _control("C10-NUBIAN", "Nubian Desert, northern Sudan", 20.5, 28.5, 20.0, _AUTUMN, "desert",
             "Remote rock and sand desert. Expect almost no candidates.",
             {"min_candidates": 0, "max_candidates": 5, "target": None, "break_year": None, "explained_by": None}),
    _control("C11-MAJABAT", "Majabat al-Koubra, Mauritania", 21.0, -7.5, 20.0, _AUTUMN, "desert",
             "One of the emptiest dune seas on Earth. Expect almost no candidates.",
             {"min_candidates": 0, "max_candidates": 5, "target": None, "break_year": None, "explained_by": None}),
]


def get_regions(kind: str | None = None) -> list[Region]:
    """All regions, or those of one kind ("blind" or "control")."""
    return [r for r in REGIONS if kind is None or r.kind == kind]


def region_by_id(region_id: str) -> Region:
    """Look a region up by id; raises KeyError when unknown."""
    for region in REGIONS:
        if region.id == region_id:
            return region
    raise KeyError(region_id)


def area_km2(region: Region) -> float:
    """Approximate area of a region's bounding box."""
    west, south, east, north = region.bbox
    height = (north - south) * 111.32
    width = (east - west) * 111.32 * np.cos(np.radians((south + north) / 2))
    return float(abs(height * width))


def coverage(regions: Sequence[Region] | None = None) -> dict[str, float]:
    """Total searched area and its share of Earth's land, for honest reporting."""
    chosen = list(regions) if regions is not None else get_regions("blind")
    total = sum(area_km2(r) for r in chosen)
    return {"regions": len(chosen), "area_km2": total,
            "share_of_land": total / EARTH_LAND_KM2}


def _distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = (np.sin((p2 - p1) / 2) ** 2
         + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2)
    return float(2 * 6371008.8 * np.arcsin(np.sqrt(a)))


def evaluate_expectation(region: Region, candidates: Sequence[Candidate]) -> dict[str, Any]:
    """Compare a control region's result with its declared expectation.

    Returns ``passed`` plus the individual findings: candidate count against
    the allowed range, whether a candidate lies within the target radius,
    whether its break year matches, and whether the checks that should
    explain it did. Only meaningful for control regions.
    """
    expect = region.expect or {}
    result: dict[str, Any] = {"region": region.id, "n_candidates": len(candidates), "reasons": []}
    ok = True
    if len(candidates) < expect.get("min_candidates", 0):
        ok = False
        result["reasons"].append(f"found {len(candidates)}, expected at least {expect['min_candidates']}")
    if expect.get("max_candidates") is not None:
        # Once the checks have run, what matters is how many detections
        # survive them; the raw detection count is reported alongside.
        checked = [c for c in candidates if c.checks]
        unexplained = [c for c in checked if c.tier != "T0"] if checked else list(candidates)
        weak = [c for c in unexplained if c.measurements.get("weak")]
        strong = [c for c in unexplained if not c.measurements.get("weak")]
        result["unexplained"] = len(unexplained)
        result["unexplained_weak"] = len(weak)
        if len(strong) > expect["max_candidates"]:
            ok = False
            result["reasons"].append(f"{len(strong)} unexplained of {len(candidates)} reviewed are above "
                                     f"the detection floor, expected at most {expect['max_candidates']}")
        elif weak:
            result["reasons"].append(f"{len(weak)} unexplained detections at the detection floor "
                                     "(small, low-amplitude changes)")
    relevant = list(candidates)
    if expect.get("detector"):
        relevant = [c for c in relevant if c.detector == expect["detector"]]
    target = expect.get("target")
    if target:
        relevant = [c for c in relevant
                    if _distance_m(c.lat, c.lon, target["lat"], target["lon"]) <= target["radius_m"]]
        result["target_hits"] = len(relevant)
        if not relevant:
            ok = False
            result["reasons"].append("no candidate within the target radius")
    if expect.get("break_year") and relevant:
        years = {c.measurements.get("break_year") for c in relevant}
        result["break_years_found"] = sorted(y for y in years if y)
        if not years & set(expect["break_year"]):
            ok = False
            result["reasons"].append(f"break years {sorted(y for y in years if y)} do not include {expect['break_year']}")
    if expect.get("explained_by") and relevant:
        checked = [c for c in relevant if c.checks]
        if checked:
            wanted = set(expect["explained_by"])
            explained = [c for c in checked
                         if any(k.status == "explains" for k in c.checks)]
            by_expected = [c for c in checked
                           if any(k.status == "explains" and k.check in wanted for k in c.checks)]
            result["explained_share"] = len(explained) / len(checked)
            result["explained_by_expected_share"] = len(by_expected) / len(checked)
            if not by_expected:
                ok = False
                result["reasons"].append("no target candidate was explained by the expected checks")
        else:
            result["reasons"].append("checks not yet run")
    result["passed"] = ok
    return result
