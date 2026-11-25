"""Wikidata catalogue check: known places and recorded events near a candidate.

``nearby_items`` lists Wikidata items with coordinates around a point and
maps their instance-of classes to coarse categories; ``check_wikidata`` turns
that list into the ``wikidata_nearby`` elimination check. The endpoint is
queried at most once per second, with a disk cache, timeouts and retries.
A failed query raises ``WikidataError`` (and yields ``not_run``): it is never
reported as "nothing found".
"""
from __future__ import annotations

import calendar
import hashlib
import json
import math
import re
import threading
import time
from datetime import date, timedelta
from typing import Any, Iterable, Mapping, Sequence

import requests

from skywatch.core import config
from skywatch.core.models import Candidate, CheckResult

ENDPOINT = "https://query.wikidata.org/sparql"
CHECK_NAME = "wikidata_nearby"
SOURCE = "Wikidata SPARQL endpoint (query.wikidata.org)"
CACHE_DIR = config.CACHE / "wikidata"
CACHE_TTL_S = 30 * 86400
#: Minimum spacing between live requests (the service asks for <= 1 per second).
MIN_INTERVAL_S = 1.1
#: Pauses before the second and third attempt of a failing request.
RETRY_SLEEPS: tuple[float, ...] = (2.0, 6.0)
TIMEOUT_S: tuple[float, float] = (10.0, 60.0)
#: Nearest items returned per query; a full page means the list was truncated.
MAX_ITEMS = 1000
#: Radius retried when the requested radius times out (dense areas).
FALLBACK_RADIUS_KM = 3.0
#: After a connection-level failure, live queries fail fast for this long.
BREAKER_S = 120.0

CATEGORIES = ("mine_or_quarry", "airport", "military", "power_or_industry",
              "dam_or_reservoir", "volcano_or_geothermal", "impact_crater",
              "archaeological_site", "aviation_accident", "meteorite",
              "oil_gas_field", "research_station", "settlement",
              "protected_area", "other")
#: Order used to pick one primary category when an item matches several.
PRIORITY = ("aviation_accident", "meteorite", "impact_crater",
            "volcano_or_geothermal", "mine_or_quarry", "oil_gas_field",
            "military", "airport", "power_or_industry", "dam_or_reservoir",
            "research_station", "archaeological_site", "settlement",
            "protected_area", "other")
#: Dated point events: they explain only when the date fits the onset window.
EVENT_CATEGORIES = ("aviation_accident", "meteorite")
#: Largest item-to-candidate distance (km) at which a category may explain,
#: before the candidate footprint is added. Settlements, protected areas and
#: "other" are deliberately absent: they never explain on their own.
EXPLAIN_KM: dict[str, float] = {
    "mine_or_quarry": 2.0, "airport": 2.0, "military": 2.0,
    "power_or_industry": 1.0, "dam_or_reservoir": 2.0,
    "volcano_or_geothermal": 2.0, "impact_crater": 2.0,
    "archaeological_site": 1.0, "aviation_accident": 2.0, "meteorite": 2.0,
    "oil_gas_field": 2.0, "research_station": 1.0,
}
#: Limit for site items with no human-written Wikipedia page
#: (``notable_sitelinks`` == 0). Bulk-imported minor features (single adits,
#: barrows, ponds) are so dense in places that a 2 km rule would "explain" a
#: large share of all points around them.
MINOR_SITE_KM = 0.5
#: The candidate footprint radius added to ``EXPLAIN_KM`` is capped at this.
FOOTPRINT_CAP_KM = 1.0
#: Causal items beyond the limit but this close are listed as near misses.
NEAR_MISS_KM = 5.0

# Class-label patterns per category (lower-case English labels of P31 classes).
_KEYWORDS: dict[str, tuple[str, ...]] = {
    "aviation_accident": (r"aviation (?:accident|incident|occurrence)s?", r"(?:plane|aircraft|air|helicopter|airliner|airship) (?:crash|accident|shootdown|disaster)",
                          r"mid-?air collision", r"controlled flight into terrain", r"airliner bombing"),
    "meteorite": (r"meteorites?", r"meteorite falls?", r"bolide", r"meteor air ?burst", r"strewn field"),
    "impact_crater": (r"impact (?:crater|structure)s?", r"meteorite craters?", r"astrobleme"),
    "volcano_or_geothermal": (r"\w*volcan\w*", r"calderas?", r"lava \w+", r"fumaroles?", r"geysers?", r"hot springs?", r"thermal springs?",
                              r"geothermal \w+", r"maars?", r"cinder cones?", r"scoria cones?", r"tuff (?:cone|ring)s?", r"solfataras?", r"lava"),
    "mine_or_quarry": (r"mines?", r"mining", r"quarr(?:y|ies)", r"open[- ]?(?:pit|cast)(?: mine)?", r"collier(?:y|ies)", r"tailings(?: \w+)?",
                       r"spoil (?:tip|heap)s?", r"(?:gravel|sand|clay|borrow) pits?", r"mine shafts?", r"adits?", r"slag heaps?"),
    "oil_gas_field": (r"oil ?fields?", r"gas ?fields?", r"(?:oil|gas|petroleum) wells?", r"oil and gas (?:field|well|deposit)s?",
                      r"(?:petroleum|hydrocarbon|natural gas) (?:field|well|reservoir|deposit|accumulation|production \w+)s?", r"oil platforms?",
                      r"oil sands?", r"drilling rigs?", r"well pads?"),
    "military": (r"military (?:base|facilit(?:y|ies)|installation|air ?field|air ?base|aerodrome|air ?port|camp|training \w+|range|site|"
                 r"reservation|area|station|outpost|post|depot|zone|compound|test\w*(?: \w+)?|garrison|exercise \w+)s?",
                 r"air ?bases?", r"air force (?:base|station|range)s?", r"army (?:base|camp|post|depot|air ?field|installation)s?",
                 r"naval (?:base|station|air station)s?", r"missile (?:base|silo|range|test\w*|launch\w*|site|complex|defen[cs]e \w+)(?: \w+)?",
                 r"(?:firing|bombing|gunnery|artillery|weapons|test) ranges?", r"proving grounds?", r"nuclear (?:weapons? )?test\w*(?: \w+)?",
                 r"nuclear explosions?", r"barracks", r"bunkers?", r"radar stations?", r"troop training (?:area|ground)s?", r"garrisons?",
                 r"arsenals?", r"spaceports?", r"cosmodromes?", r"(?:rocket )?launch (?:site|pad|complex|facilit(?:y|ies))s?",
                 r"rocket (?:launch\w*|test\w*|range)(?: \w+)?", r"ammunition (?:depot|dump|plant|storage)s?",
                 r"weapons? (?:test\w*|depot|storage)(?: \w+)?"),
    "airport": (r"airports?", r"aerodromes?", r"airfields?", r"airstrips?", r"heliports?", r"landing strips?", r"runways?", r"gliderports?"),
    "power_or_industry": (r"power (?:station|plant)s?", r"\w* ?power (?:station|plant)s?", r"solar (?:park|farm|power \w+)s?", r"photovoltaic \w+(?: \w+)?",
                          r"wind (?:farm|park|turbine)s?", r"(?:electrical )?substations?", r"factor(?:y|ies)", r"refiner(?:y|ies)", r"smelters?",
                          r"steel ?(?:mill|works|plant)s?",
                          r"industrial (?:zone|park|area|estate|site|facilit(?:y|ies)|complex|plant|district|building)s?", r"(?:cement|chemical|manufacturing|processing|treatment|desalination) (?:plant|works)s?",
                          r"nuclear reactors?", r"landfills?",
                          r"waste (?:dump|disposal|treatment|management|processing|incinerat\w+)(?: \w+)?", r"sewage \w+", r"pipelines?", r"pumping stations?",
                          r"salt (?:works|pans?|evaporation ponds?)", r"evaporation ponds?", r"data cent(?:er|re)s?", r"transmitters?",
                          r"greenhouses?", r"feedlots?", r"construction sites?"),
    "dam_or_reservoir": (r"dams?", r"reservoirs?", r"weirs?", r"barrages?", r"retention basins?", r"artificial lakes?", r"embankments?"),
    "research_station": (r"research (?:station|facilit(?:y|ies)|base)s?", r"\w* ?observator(?:y|ies)", r"\w* ?telescopes?", r"(?:weather|field|polar|antarctic|arctic|seismic|seismological|tracking|ground) stations?",
                         r"antenna arrays?", r"test (?:site|facilit(?:y|ies))s?"),
    "archaeological_site": (r"archa?eological \w+", r"ruins?", r"tumul(?:us|i)", r"burial mounds?", r"hill ?forts?", r"geoglyphs?", r"petroglyphs?",
                            r"megalith\w*", r"ancient \w+", r"kurgans?", r"prehistoric \w+", r"pyramids?", r"stone circles?", r"earthworks?",
                            r"necropol(?:is|es)", r"rock art(?: \w+)?", r"dolmens?", r"menhirs?", r"nuraghes?", r"cairns?", r"barrows?",
                            r"deserted (?:medieval )?villages?", r"tells?", r"mounds?"),
    "settlement": (r"\w* ?settlements?", r"cit(?:y|ies)", r"towns?", r"villages?", r"hamlets?", r"municipalit(?:y|ies)", r"communes?", r"localit(?:y|ies)",
                   r"neighbou?rhoods?", r"suburbs?", r"census-designated places?", r"townships?", r"populated places?", r"ghost towns?",
                   r"boroughs?", r"farms?", r"ranch(?:es)?", r"homesteads?", r"unincorporated communit(?:y|ies)", r"kibbutz\w*", r"oas[ei]s"),
    "protected_area": (r"protected \w+", r"(?:national|state|regional|provincial|nature|natural) parks?", r"nature reserves?", r"\w* ?reserves?", r"wildlife \w+",
                       r"\w* ?sanctuar(?:y|ies)", r"national (?:monument|forest|preserve|grassland)s?", r"conservation \w+", r"wilderness(?: \w+)?",
                       r"biosphere reserves?", r"natura 2000 \w+", r"sites? of special scientific interest", r"ramsar \w+", r"game reserves?",
                       r"\w* ?refuges?", r"world heritage sites?"),
}
_PATTERNS: dict[str, re.Pattern[str]] = {
    cat: re.compile(r"(?<![a-z])(?:" + "|".join(parts) + r")(?![a-z])") for cat, parts in _KEYWORDS.items()
}
# Phrases removed before matching because they contain a misleading keyword.
_STOP_PHRASES = re.compile(r"(?:naval|land|sea|anti-tank) mines?|minefields?|mining (?:town|communit(?:y|ies)|compan(?:y|ies))|"
                           r"airport (?:rail link|station|terminal)s?|power station (?:unit)|city (?:gate|hall|park|wall)s?|"
                           r"town (?:hall|gate|wall)s?|village (?:hall|green)s?|farm ?(?:house|stead)s?")

# Root classes checked with a P279* walk when no label pattern matches
# (QIDs verified against live labels on 2026-11-25).
_ROOTS: dict[str, tuple[str, ...]] = {
    "mine_or_quarry": ("Q820477", "Q188040"),
    "airport": ("Q1248784", "Q62447"),
    "military": ("Q245016", "Q1778846", "Q853409", "Q4940739", "Q53732481", "Q194188"),
    "power_or_industry": ("Q159719", "Q83405", "Q329683", "Q152810", "Q12353044", "Q1867977"),
    "dam_or_reservoir": ("Q12323", "Q131681"),
    "volcano_or_geothermal": ("Q8072", "Q177380", "Q83471", "Q159954", "Q105880", "Q488416"),
    "impact_crater": ("Q55818",),
    "archaeological_site": ("Q839954", "Q34023"),
    "aviation_accident": ("Q744913",),
    "meteorite": ("Q60186", "Q56458151"),
    "oil_gas_field": ("Q211748", "Q587682"),
    "research_station": ("Q195339", "Q62832", "Q1254933"),
    "settlement": ("Q486972",),
    "protected_area": ("Q473972",),
}
_ROOT_CATEGORY: dict[str, str] = {qid: cat for cat, qids in _ROOTS.items() for qid in qids}

_PRECISION_NAME = {11: "day", 10: "month", 9: "year", 8: "decade", 7: "century", 6: "millennium"}
_TIME_RE = re.compile(r"^([+-]?)(\d{1,})-(\d\d)-(\d\d)")
_QID_RE = re.compile(r"^Q\d+$")

_lock = threading.Lock()
_last_request = 0.0
_down_until = 0.0
_class_lock = threading.Lock()


class WikidataError(RuntimeError):
    """The Wikidata endpoint could not be queried.

    ``kind`` is "network" (unreachable), "timeout", "http" (429 or 5xx after
    retries), "client" (rejected query), "reply" (unreadable) or "breaker".
    """

    def __init__(self, message: str, kind: str = "network") -> None:
        super().__init__(message)
        self.kind = kind


def reset_breaker() -> None:
    """Allow live queries again immediately after a connection failure."""
    global _down_until
    _down_until = 0.0


# --------------------------------------------------------------------------
# Geometry and dates (shared with skywatch.eliminate.records)
# --------------------------------------------------------------------------

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two WGS84 points."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * 6371.0088 * math.asin(min(1.0, math.sqrt(a)))


def valid_point(lat: float, lon: float) -> bool:
    """True for finite coordinates inside the WGS84 range."""
    try:
        return bool(math.isfinite(lat) and math.isfinite(lon) and -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0)
    except TypeError:
        return False


def footprint_radius_km(candidate: Candidate) -> float:
    """Radius in km of a circle with the candidate area (bbox half-diagonal if no area)."""
    area = candidate.area_m2
    if isinstance(area, (int, float)) and math.isfinite(area) and area > 0:
        return math.sqrt(area / math.pi) / 1000.0
    try:
        west, south, east, north = (float(v) for v in candidate.bbox)
    except (TypeError, ValueError):
        return 0.0
    if not (valid_point(south, west) and valid_point(north, east)):
        return 0.0
    return haversine_km(south, west, north, east) / 2.0


def parse_iso_date(text: str | None) -> date | None:
    """Parse the leading YYYY-MM-DD of an ISO date or datetime; None if absent or invalid."""
    if not text or not isinstance(text, str):
        return None
    try:
        return date.fromisoformat(text.strip()[:10])
    except ValueError:
        return None


def onset_window(candidate: Candidate, pad_days: int = 0) -> tuple[date, date] | None:
    """The candidate onset window (absent_until, present_from), padded; None unless both dates exist."""
    start, end = parse_iso_date(candidate.absent_until), parse_iso_date(candidate.present_from)
    if start is None or end is None:
        return None
    if start > end:
        start, end = end, start
    pad = timedelta(days=pad_days)
    return start - pad, end + pad


def date_interval(iso: str | None, precision: str | None = "day") -> tuple[date, date] | None:
    """Calendar span covered by a date of the given precision; None if coarser than a year or unparseable."""
    day = parse_iso_date(iso)
    if day is None:
        return None
    if precision in (None, "day"):
        return day, day
    if precision == "month":
        return day.replace(day=1), day.replace(day=calendar.monthrange(day.year, day.month)[1])
    if precision == "year":
        return date(day.year, 1, 1), date(day.year, 12, 31)
    return None


def intervals_overlap(a: tuple[date, date], b: tuple[date, date]) -> bool:
    """True when two closed date intervals share at least one day."""
    return a[0] <= b[1] and b[0] <= a[1]


# --------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------

def classify_labels(labels: Iterable[str]) -> list[str]:
    """Coarse categories matched by instance-of labels, in ``PRIORITY`` order; empty if none."""
    found: set[str] = set()
    for label in labels:
        text = _STOP_PHRASES.sub(" ", str(label).lower())
        for category, pattern in _PATTERNS.items():
            if pattern.search(text):
                found.add(category)
    return [cat for cat in PRIORITY if cat in found]


def _class_cache_path() -> Any:
    return CACHE_DIR / "class_roots.json"


def _load_class_cache() -> dict[str, list[str]]:
    try:
        raw = json.loads(_class_cache_path().read_text())
    except (OSError, ValueError):
        return {}
    return {k: list(v) for k, v in raw.items() if isinstance(v, list)} if isinstance(raw, dict) else {}


def _resolve_class_roots(qids: Sequence[str]) -> dict[str, list[str]]:
    """Categories reached from each class by a subclass-of walk (cached per class forever).

    Best effort: classes that cannot be resolved because the endpoint fails
    are simply absent from the result (and are not cached).
    """
    wanted = sorted({q for q in qids if _QID_RE.match(q)})
    if not wanted:
        return {}
    with _class_lock:
        cache = _load_class_cache()
    out = {q: cache[q] for q in wanted if q in cache}
    missing = [q for q in wanted if q not in cache]
    for start in range(0, len(missing), 150):
        chunk = missing[start:start + 150]
        query = ("SELECT ?class ?root WHERE { VALUES ?class { %s } VALUES ?root { %s } ?class wdt:P279* ?root . }"
                 % (" ".join("wd:" + q for q in chunk), " ".join("wd:" + q for q in _ROOT_CATEGORY)))
        try:
            rows = sparql(query)
        except WikidataError:
            continue
        resolved: dict[str, set[str]] = {q: set() for q in chunk}
        for row in rows:
            cls = _qid(row.get("class", {}).get("value", ""))
            root = _qid(row.get("root", {}).get("value", ""))
            if cls in resolved and root in _ROOT_CATEGORY:
                resolved[cls].add(_ROOT_CATEGORY[root])
        with _class_lock:
            cache = _load_class_cache()
            for cls, cats in resolved.items():
                cache[cls] = [c for c in PRIORITY if c in cats]
                out[cls] = cache[cls]
            _write_json(_class_cache_path(), cache)
    return out


# --------------------------------------------------------------------------
# Endpoint access
# --------------------------------------------------------------------------

def _write_json(path: Any, payload: Any) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + f".{threading.get_ident()}.tmp")
        tmp.write_text(json.dumps(payload))
        tmp.replace(path)
    except OSError:
        pass  # the cache is an optimisation only


def _qid(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def sparql(query: str, use_cache: bool = True) -> list[dict[str, Any]]:
    """Run a SPARQL query and return the JSON result bindings.

    Replies are cached on disk for ``CACHE_TTL_S``; live requests are spaced
    at least ``MIN_INTERVAL_S`` apart and retried on timeouts, connection
    errors, HTTP 429 and 5xx. Raises ``WikidataError`` when no valid reply
    is obtained; after a connection-level failure, uncached queries fail
    fast for ``BREAKER_S`` seconds instead of hammering a dead endpoint.
    """
    global _last_request, _down_until
    path = CACHE_DIR / (hashlib.sha1(query.encode("utf-8")).hexdigest() + ".json")
    if use_cache:
        try:
            cached = json.loads(path.read_text())
            if time.time() - float(cached["fetched"]) < CACHE_TTL_S:
                return list(cached["bindings"])
        except (OSError, ValueError, KeyError, TypeError):
            pass
    headers = {"User-Agent": config.USER_AGENT, "Accept": "application/sparql-results+json"}
    if time.monotonic() < _down_until:
        raise WikidataError("endpoint marked unreachable after a recent connection failure", kind="breaker")
    last_error, last_kind = "no attempt made", "network"
    for attempt in range(len(RETRY_SLEEPS) + 1):
        pause = 0.0
        with _lock:
            wait = MIN_INTERVAL_S - (time.monotonic() - _last_request)
            if wait > 0:
                time.sleep(wait)
            try:
                response = requests.get(ENDPOINT, params={"query": query, "format": "json"},
                                        headers=headers, timeout=TIMEOUT_S)
            except requests.RequestException as exc:
                response = None
                last_error = f"{type(exc).__name__}: {str(exc)[:200]}"
                last_kind = ("network" if isinstance(exc, requests.ConnectionError)
                             else "timeout" if isinstance(exc, requests.Timeout) else "network")
            finally:
                _last_request = time.monotonic()
        if response is not None:
            status = response.status_code
            if status == 200:
                try:
                    bindings = response.json()["results"]["bindings"]
                except (ValueError, KeyError, TypeError) as exc:
                    last_error, last_kind = f"unreadable reply ({type(exc).__name__})", "reply"
                else:
                    if use_cache:
                        _write_json(path, {"fetched": time.time(), "bindings": bindings})
                    return list(bindings)
            elif status == 429 or status >= 500:
                last_error, last_kind = f"HTTP {status}", "http"
                try:
                    pause = min(30.0, float(response.headers.get("Retry-After", "0")))
                except ValueError:
                    pause = 0.0
            else:
                raise WikidataError(f"HTTP {status}: {response.text[:200]!r}", kind="client")
        if attempt < len(RETRY_SLEEPS):
            time.sleep(max(pause, RETRY_SLEEPS[attempt]))
    if last_kind == "network":
        _down_until = time.monotonic() + BREAKER_S
    raise WikidataError(f"query failed after {len(RETRY_SLEEPS) + 1} attempts: {last_error}", kind=last_kind)


def _around_query(lat: float, lon: float, radius_km: float, limit: int) -> str:
    return (
        "SELECT ?item ?itemLabel ?dist ?loc ?links ?ceb ?sv ?class ?classLabel ?pit ?pitPrec ?inc ?incPrec WHERE {\n"
        "  { SELECT ?item (MIN(?d) AS ?dist) (SAMPLE(?l) AS ?loc) WHERE {\n"
        "      SERVICE wikibase:around {\n"
        "        ?item wdt:P625 ?l .\n"
        f"        bd:serviceParam wikibase:center \"Point({lon:.5f} {lat:.5f})\"^^geo:wktLiteral .\n"
        f"        bd:serviceParam wikibase:radius \"{radius_km:.3f}\" .\n"
        "        bd:serviceParam wikibase:distance ?d .\n"
        "      }\n"
        f"    }} GROUP BY ?item ORDER BY ?dist LIMIT {int(limit)} }}\n"
        "  OPTIONAL { ?item wikibase:sitelinks ?links . }\n"
        "  OPTIONAL { ?ceb schema:about ?item ; schema:isPartOf <https://ceb.wikipedia.org/> . }\n"
        "  OPTIONAL { ?sv schema:about ?item ; schema:isPartOf <https://sv.wikipedia.org/> . }\n"
        "  OPTIONAL { ?item wdt:P31 ?class . }\n"
        "  OPTIONAL { ?item p:P585/psv:P585 ?pv . ?pv wikibase:timeValue ?pit ; wikibase:timePrecision ?pitPrec . }\n"
        "  OPTIONAL { ?item p:P571/psv:P571 ?iv . ?iv wikibase:timeValue ?inc ; wikibase:timePrecision ?incPrec . }\n"
        "  SERVICE wikibase:label { bd:serviceParam wikibase:language \"en,mul,fr,es,de,ru,pt,zh,ar\". }\n"
        "}"
    )


def _parse_time(value: str | None, precision: str | None) -> tuple[str, str] | None:
    """Normalise a Wikidata time value to (ISO-like date string, precision name)."""
    if not value:
        return None
    match = _TIME_RE.match(value)
    if not match:
        return None
    sign, year, month, day = match.groups()
    iso = f"{'-' if sign == '-' else ''}{int(year):04d}-{max(1, int(month)):02d}-{max(1, int(day)):02d}"
    try:
        name = _PRECISION_NAME.get(int(float(precision)), "coarse") if precision is not None else "day"
    except ValueError:
        name = "day"
    return iso, name


def _parse_point(wkt: str | None) -> tuple[float | None, float | None]:
    match = re.search(r"Point\(([-+0-9.eE]+) ([-+0-9.eE]+)\)", wkt or "")
    if not match:
        return None, None
    return float(match.group(2)), float(match.group(1))


def _items_from_bindings(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Group SPARQL rows (one per item x class x date) into one record per item."""
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        qid = _qid(row.get("item", {}).get("value", ""))
        if not _QID_RE.match(qid):
            continue
        try:
            dist = float(row["dist"]["value"])
        except (KeyError, ValueError, TypeError):
            continue
        rec = grouped.setdefault(qid, {"qid": qid, "label": "", "distance_km": dist, "lat": None, "lon": None,
                                       "sitelinks": None, "_bot": set(), "_classes": {}, "_dates": set()})
        rec["distance_km"] = min(rec["distance_km"], dist)
        label = row.get("itemLabel", {}).get("value", "")
        if label and not rec["label"]:
            rec["label"] = label
        if rec["lat"] is None:
            rec["lat"], rec["lon"] = _parse_point(row.get("loc", {}).get("value"))
        if rec["sitelinks"] is None and "links" in row:
            try:
                rec["sitelinks"] = int(float(row["links"]["value"]))
            except (KeyError, ValueError, TypeError):
                pass
        rec["_bot"].update(key for key in ("ceb", "sv") if key in row)
        cls = _qid(row.get("class", {}).get("value", ""))
        if _QID_RE.match(cls):
            rec["_classes"][cls] = row.get("classLabel", {}).get("value", cls)
        for prop, key, prec_key in (("P585", "pit", "pitPrec"), ("P571", "inc", "incPrec")):
            parsed = _parse_time(row.get(key, {}).get("value"), row.get(prec_key, {}).get("value"))
            if parsed:
                rec["_dates"].add((prop, parsed[0], parsed[1]))
    return sorted(grouped.values(), key=lambda r: (r["distance_km"], r["qid"]))


def _finalise(records: list[dict[str, Any]], class_roots: Mapping[str, Sequence[str]]) -> list[dict[str, Any]]:
    rank = {"day": 0, "month": 1, "year": 2, "decade": 3, "century": 4, "millennium": 5, "coarse": 6}
    items: list[dict[str, Any]] = []
    for rec in records:
        classes: dict[str, str] = rec.pop("_classes")
        dates: set[tuple[str, str, str]] = rec.pop("_dates")
        bot: set[str] = rec.pop("_bot")
        # Lsjbot wrote Cebuano (and paired Swedish) stubs for every GeoNames feature: not a sign of notability.
        stubs = (1 + ("sv" in bot)) if "ceb" in bot else 0
        notable = None if rec["sitelinks"] is None else max(0, rec["sitelinks"] - stubs)
        found: set[str] = set()
        for cls, label in classes.items():
            found.update(classify_labels([label]))
            found.update(class_roots.get(cls, ()))
        categories = [c for c in PRIORITY if c in found] or ["other"]
        # Point in time (P585) wins over inception (P571); then the most precise, then the earliest.
        best = min(dates, key=lambda d: (d[0] != "P585", rank.get(d[2], 9), d[1])) if dates else None
        items.append({
            "qid": rec["qid"],
            "label": rec["label"] or rec["qid"],
            "instance_of": sorted(set(classes.values())),
            "instance_of_qids": sorted(classes),
            "category": categories[0],
            "categories": categories,
            "distance_km": round(float(rec["distance_km"]), 3),
            "lat": rec["lat"],
            "lon": rec["lon"],
            "date": best[1] if best else None,
            "date_precision": best[2] if best else None,
            "date_property": best[0] if best else None,
            "sitelinks": rec["sitelinks"],
            "notable_sitelinks": notable,
            "url": "https://www.wikidata.org/wiki/" + rec["qid"],
        })
    return items


def _query_nearby(lat: float, lon: float, radius_km: float) -> tuple[list[dict[str, Any]], bool]:
    """Items around a point plus a flag telling whether the list hit ``MAX_ITEMS``."""
    if not valid_point(lat, lon):
        raise ValueError(f"invalid coordinates: lat={lat!r}, lon={lon!r}")
    if not (isinstance(radius_km, (int, float)) and math.isfinite(radius_km) and 0 < radius_km <= 100):
        raise ValueError(f"radius_km must be in (0, 100], got {radius_km!r}")
    rows = sparql(_around_query(float(lat), float(lon), float(radius_km), MAX_ITEMS))
    records = _items_from_bindings(rows)
    unmatched = sorted({cls for rec in records for cls, label in rec["_classes"].items()
                        if not classify_labels([label])})
    roots = _resolve_class_roots(unmatched) if unmatched else {}
    return _finalise(records, roots), len(records) >= MAX_ITEMS


def nearby_items(lat: float, lon: float, radius_km: float = 10.0) -> list[dict[str, Any]]:
    """Wikidata items with coordinates within ``radius_km`` of a point, nearest first.

    Each dict has: ``qid``, ``label``, ``instance_of`` (class labels),
    ``instance_of_qids``, ``category`` (one of ``CATEGORIES``), ``categories``
    (all matches, most specific first), ``distance_km``, ``lat``, ``lon``,
    ``date`` (ISO date from point in time P585, else inception P571, else
    None), ``date_precision`` ("day", "month", "year", ... or None),
    ``date_property``, ``sitelinks`` (number of Wikipedia-family pages),
    ``notable_sitelinks`` (the same without bot-written Cebuano/Swedish
    geography stubs; a notability proxy, None if unknown) and ``url``. At most ``MAX_ITEMS`` nearest items are
    returned. Raises ``WikidataError`` if the endpoint fails and ``ValueError``
    for invalid arguments; an empty list always means "nothing catalogued".
    """
    return _query_nearby(lat, lon, radius_km)[0]


# --------------------------------------------------------------------------
# Elimination check
# --------------------------------------------------------------------------

def _brief(item: Mapping[str, Any]) -> dict[str, Any]:
    return {key: item.get(key) for key in ("qid", "label", "category", "instance_of", "distance_km", "date",
                                           "date_precision", "notable_sitelinks")}


def _limit_km(item: Mapping[str, Any], category: str, foot: float) -> float:
    """Explanation distance for one item in one causal category."""
    links = item.get("notable_sitelinks")
    minor = links is not None and int(links) < 1 and category not in EVENT_CATEGORIES
    return (min(EXPLAIN_KM[category], MINOR_SITE_KM) if minor else EXPLAIN_KM[category]) + foot


def _name(item: Mapping[str, Any]) -> str:
    return f"{item.get('label')} ({item.get('qid')}, {item.get('category')}) at {float(item.get('distance_km', float('nan'))):.2f} km"


def evaluate_items(candidate: Candidate, items: Sequence[Mapping[str, Any]], searched_radius_km: float,
                   truncated: bool = False) -> CheckResult:
    """Decide the ``wikidata_nearby`` status from an already fetched item list.

    ``explains``: an item of a causal category lies within ``EXPLAIN_KM`` plus
    the footprint radius (capped); site items with no human-written
    Wikipedia page only count within ``MINOR_SITE_KM``; aviation accidents and meteorites must also
    carry a date overlapping the onset window padded by 30 days when the
    candidate has one. ``inconclusive``: only undated accident/meteorite items
    are in range of a dated candidate, or the item list was truncated before
    the explanation distance. Otherwise ``does_not_explain``.
    """
    foot = min(footprint_radius_km(candidate), FOOTPRINT_CAP_KM)
    window = onset_window(candidate, pad_days=30)
    explaining: list[dict[str, Any]] = []
    undated: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    near_miss: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for item in items:
        counts[str(item.get("category"))] = counts.get(str(item.get("category")), 0) + 1
        dist = float(item.get("distance_km", math.inf))
        causal = [c for c in item.get("categories", [item.get("category")]) if c in EXPLAIN_KM]
        if not causal:
            continue
        in_range = [c for c in causal if dist <= _limit_km(item, c, foot)]
        if not in_range:
            if dist <= NEAR_MISS_KM:
                near_miss.append(_brief(item))
            continue
        sites = [c for c in in_range if c not in EVENT_CATEGORIES]
        brief = _brief(item)
        if sites or window is None:
            brief["explains_as"] = (sites or in_range)[0]
            brief["limit_km"] = round(_limit_km(item, brief["explains_as"], foot), 3)
            explaining.append(brief)
            continue
        span = date_interval(item.get("date"), item.get("date_precision"))
        if span is None:
            brief["reason"] = "event item has no usable date to compare with the onset window"
            undated.append(brief)
        elif intervals_overlap(span, window):
            brief["explains_as"] = in_range[0]
            brief["limit_km"] = round(_limit_km(item, in_range[0], foot), 3)
            explaining.append(brief)
        else:
            brief["reason"] = "event date outside the onset window padded by 30 days"
            rejected.append(brief)
    max_limit = max(EXPLAIN_KM.values()) + foot
    covered = max((float(i.get("distance_km", 0.0)) for i in items), default=0.0) if truncated else float(searched_radius_km)
    evidence: dict[str, Any] = {
        "searched_radius_km": searched_radius_km,
        "n_items": len(items),
        "truncated": truncated,
        "covered_radius_km": round(covered, 3),
        "footprint_radius_km": round(foot, 3),
        "onset_window_padded": [window[0].isoformat(), window[1].isoformat()] if window else None,
        "category_counts": counts,
        "nearest": [_brief(i) for i in items[:10]],
        "explaining": explaining,
        "undated_events_in_range": undated,
        "events_outside_window": rejected,
        "causal_near_misses": near_miss[:10],
    }
    nearest_txt = "; ".join(_name(i) for i in items[:3]) or "none"
    if explaining:
        best = explaining[0]
        detail = (f"{best['label']} ({best['qid']}, {best['explains_as']}) is catalogued {best['distance_km']:.2f} km away, "
                  f"within the {best['limit_km']:.1f} km limit for that category"
                  + (f"; date {best['date']} fits the onset window" if best["explains_as"] in EVENT_CATEGORIES and window and best.get("date") else "")
                  + (f" ({len(explaining) - 1} more explaining item(s))" if len(explaining) > 1 else ""))
        return CheckResult(CHECK_NAME, "infrastructure", "explains", detail, SOURCE, evidence)
    if undated:
        detail = (f"{_name(undated[0])} is a recorded event in range but has no date in Wikidata, "
                  "so it cannot be compared with the onset window")
        return CheckResult(CHECK_NAME, "infrastructure", "inconclusive", detail, SOURCE, evidence)
    if truncated and covered < max_limit:
        detail = (f"catalogue too dense: the {len(items)} nearest items only reach {covered:.2f} km, "
                  f"short of the {max_limit:.1f} km explanation distance")
        return CheckResult(CHECK_NAME, "infrastructure", "inconclusive", detail, SOURCE, evidence)
    detail = (f"no causally plausible catalogued item within the explanation distance "
              f"({len(items)} item(s) within {covered:.1f} km; nearest: {nearest_txt})")
    if near_miss:
        detail += f"; nearest causal item beyond the limit: {_name(near_miss[0])}"
    if rejected:
        detail += f"; {_name(rejected[0])} is in range but dated {rejected[0].get('date')}, outside the onset window"
    return CheckResult(CHECK_NAME, "infrastructure", "does_not_explain", detail, SOURCE, evidence)


def check_wikidata(candidate: Candidate, radius_km: float = 10.0) -> list[CheckResult]:
    """Run the ``wikidata_nearby`` check for one candidate (always one result).

    Returns ``not_run`` with the reason when the endpoint cannot be queried or
    the candidate coordinates are invalid; see ``evaluate_items`` for the
    decision rule. If the requested radius times out or is refused by the
    server, a ``FALLBACK_RADIUS_KM`` query is tried and the radius actually searched is recorded in evidence.
    """
    used = radius_km
    try:
        try:
            items, truncated = _query_nearby(candidate.lat, candidate.lon, radius_km)
        except WikidataError as exc:
            if exc.kind not in ("timeout", "http") or radius_km <= FALLBACK_RADIUS_KM:
                raise
            used = FALLBACK_RADIUS_KM
            items, truncated = _query_nearby(candidate.lat, candidate.lon, used)
    except WikidataError as exc:
        return [CheckResult(CHECK_NAME, "infrastructure", "not_run", f"Wikidata endpoint unavailable: {exc}", SOURCE,
                            {"error": str(exc), "requested_radius_km": radius_km})]
    except (ValueError, TypeError) as exc:
        return [CheckResult(CHECK_NAME, "infrastructure", "not_run", f"cannot query: {exc}", SOURCE, {"error": str(exc)})]
    result = evaluate_items(candidate, items, used, truncated)
    result.evidence["requested_radius_km"] = radius_km
    return [result]
