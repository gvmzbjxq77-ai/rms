"""Mapped-infrastructure check: is the candidate on or beside something OpenStreetMap knows?

Data comes from the official OSM API ``map`` call, which is meant for light
use. Every response is cached on disk, requests are serialised and spaced at
least one second apart across threads and processes, and only one small box
around a candidate is ever requested (never a sweep over a region).
"""
from __future__ import annotations

import fcntl
import gzip
import io as _stdio
import math
import os
import threading
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import lru_cache
from http import HTTPStatus
from pathlib import Path
from typing import Any

import numpy as np
import requests
import shapely
from shapely.errors import GEOSException
from shapely.geometry import GeometryCollection, LineString, MultiLineString, Point, Polygon, box
from shapely.geometry.base import BaseGeometry
from shapely.ops import polygonize, unary_union

from ..core import config
from ..core.models import BBox, Candidate, CheckResult

API_URL = "https://api.openstreetmap.org/api/0.6/map"
CHECK_NAME = "osm_infrastructure"
SOURCE = "OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL)"
#: Response cache and rate-limit lock file. Looked up at call time.
CACHE_DIR: Path = config.CACHE / "osm"

DEFAULT_RADIUS_M = 3000.0
#: Smallest box tried when the API refuses a dense area (over 50000 nodes).
MIN_RADIUS_M = 300.0
#: Largest box ever requested, in square degrees (the API itself allows 0.25).
MAX_BOX_DEG2 = 0.04
#: Minimum spacing between two requests, across threads and processes.
MIN_INTERVAL_S = 1.0
#: A feature explains a candidate when it is within the footprint size,
#: clipped to this range, of the footprint edge.
TOLERANCE_RANGE_M = (100.0, 300.0)

_TIMEOUT = (10.0, 90.0)
_RETRIES = 3
_BANDWIDTH_EXCEEDED = 509  # OSM-specific "downloaded too much" status
_THREAD_LOCK = threading.Lock()

#: Tags that make a mapped feature a plausible mundane cause of a surface
#: change, in priority order. ``None`` accepts any value except "no".
_EXPLAINING: dict[str, frozenset[str] | None] = {
    "military": None,
    "aeroway": None,
    "landuse": frozenset({
        "quarry", "industrial", "construction", "military", "landfill", "farmland",
        "reservoir", "farmyard", "orchard", "vineyard", "greenhouse_horticulture",
        "brownfield", "basin", "salt_pond", "aquaculture", "commercial", "residential",
        "retail", "railway"}),
    "man_made": frozenset({
        "mineshaft", "adit", "works", "petroleum_well", "pipeline", "tower", "mast",
        "wastewater_plant", "storage_tank", "silo", "water_works", "water_well",
        "tailings_pond", "spoil_heap", "communications_tower", "antenna", "flare",
        "pumping_station", "chimney", "kiln", "cutline", "clearcut", "telescope",
        "monitoring_station", "bunker_silo", "gasometer"}),
    "power": frozenset({"plant", "generator", "substation", "line", "minor_line",
                        "cable", "tower"}),
    "historic": frozenset({"archaeological_site", "mine", "mine_shaft", "aircraft",
                           "wreck", "ruins", "battlefield", "bomb_crater"}),
    "waterway": frozenset({"dam", "weir"}),
    "natural": frozenset({"sinkhole", "volcano", "hot_spring", "geyser", "fumarole"}),
    "highway": frozenset({"construction"}),
    "railway": frozenset({"construction"}),
    "industrial": None,
    "leisure": frozenset({"pitch", "track", "golf_course", "stadium"}),
    "building": None,
}
#: Lifecycle prefixes: a disused or razed feature still marks past activity.
_LIFECYCLE = ("", "disused:", "abandoned:", "construction:", "ruins:", "razed:",
              "demolished:", "removed:", "was:")
_NEGATIVE = frozenset({"no", "none"})
#: Motor-vehicle ways counted as road access (paths and footways are not).
_ROADS = frozenset({
    "motorway", "trunk", "primary", "secondary", "tertiary", "unclassified",
    "residential", "service", "track", "road", "living_street", "motorway_link",
    "trunk_link", "primary_link", "secondary_link", "tertiary_link"})
#: Keys that describe the edit, not the thing on the ground.
_META_KEYS = frozenset({"source", "created_by", "note", "fixme", "FIXME", "attribution",
                        "comment", "converted_by", "odbl", "odbl:note"})
_META_PREFIXES = ("source:", "note:", "fixme:", "tiger:", "gnis:", "nhd:", "import",
                  "check_date", "survey:")
_LINEAR_KEYS = ("highway", "barrier", "railway")
_LINEAR_VALUES = {"power": ("line", "minor_line", "cable"),
                  "man_made": ("pipeline", "cutline", "embankment")}
_AREA_RELATIONS = ("multipolygon", "boundary")
_KEPT_RELATIONS = ("multipolygon", "boundary", "site")


class OsmUnavailable(RuntimeError):
    """The OSM API could not supply data for the requested place."""


class _TooLarge(Exception):
    """The API refused a box for holding too many nodes or too much area."""

    def __init__(self, message: str, requests_made: int = 0) -> None:
        super().__init__(message)
        self.requests_made = requests_made


@dataclass
class _Parsed:
    nodes: dict[int, tuple[float, float]] = field(default_factory=dict)  # id -> lon, lat
    node_tags: dict[int, dict[str, str]] = field(default_factory=dict)
    ways: dict[int, tuple[list[int], dict[str, str]]] = field(default_factory=dict)
    relations: dict[int, tuple[list[tuple[str, int, str]], dict[str, str]]] = field(
        default_factory=dict)


@dataclass
class _Feature:
    osm_type: str
    osm_id: int
    tags: dict[str, str]
    geom: BaseGeometry          # local metres, origin at the query point
    lonlat: list[list[float]]
    kind: str | None            # explaining tag, see ``classify``


@dataclass
class _Extract:
    lat: float
    lon: float
    requested_radius_m: float
    covered_radius_m: float
    bbox: BBox
    fetched: str
    network_requests: int
    features: list[_Feature]


# --------------------------------------------------------------------------
# Tag interpretation
# --------------------------------------------------------------------------

def classify(tags: dict[str, str]) -> str | None:
    """Tag (``"key=value"``) that makes a feature a plausible mundane cause, else None.

    A plain road, track, path, fence or natural feature returns None.
    """
    for key, allowed in _EXPLAINING.items():
        for prefix in _LIFECYCLE:
            value = tags.get(prefix + key)
            if value is None or value in _NEGATIVE:
                continue
            if allowed is None or value in allowed:
                return f"{prefix}{key}={value}"
    return None


def is_road(tags: dict[str, str]) -> bool:
    """True for a way a motor vehicle can use, including unpaved tracks."""
    return tags.get("highway") in _ROADS


def is_building(tags: dict[str, str]) -> bool:
    return tags.get("building", "no") not in _NEGATIVE


def _meaningful(tags: dict[str, str]) -> bool:
    return any(k not in _META_KEYS and not k.startswith(_META_PREFIXES) for k in tags)


def _is_area(tags: dict[str, str]) -> bool:
    """Whether a closed way encloses an area rather than being a loop line."""
    area = tags.get("area")
    if area == "no":
        return False
    if area == "yes":
        return True
    if any(key in tags for key in _LINEAR_KEYS):
        return False
    return not any(tags.get(key) in values for key, values in _LINEAR_VALUES.items())


# --------------------------------------------------------------------------
# Download, rate limit and cache
# --------------------------------------------------------------------------

def _http_get(params: dict[str, str]) -> requests.Response:
    return requests.get(API_URL, params=params, timeout=_TIMEOUT,
                        headers={"User-Agent": config.USER_AGENT})


def _cache_file(bbox: BBox) -> Path:
    return CACHE_DIR / ("map_" + "_".join(f"{v:.5f}" for v in bbox) + ".xml.gz")


def _refusal_file(cache_file: Path) -> Path:
    return cache_file.with_name(cache_file.name.replace(".xml.gz", ".toolarge"))


def _rate_limited_get(params: dict[str, str], cache_file: Path) -> requests.Response | None:
    """Send one request while holding the cross-process lock.

    The lock file stores the end time of the previous request; the next one
    starts at least ``MIN_INTERVAL_S`` later. Returns None when another thread
    or process cached this box while we waited for the lock.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fd = os.open(CACHE_DIR / "rate.lock", os.O_RDWR | os.O_CREAT, 0o644)
    with _THREAD_LOCK, os.fdopen(fd, "r+") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            if cache_file.exists() or _refusal_file(cache_file).exists():
                return None
            try:
                last = float(handle.read().strip() or 0.0)
            except ValueError:
                last = 0.0
            wait = min(max(last + MIN_INTERVAL_S - time.time(), 0.0), MIN_INTERVAL_S)
            if wait > 0:
                time.sleep(wait)
            try:
                return _http_get(params)
            finally:
                handle.seek(0)
                handle.truncate()
                handle.write(f"{time.time():.3f}")
                handle.flush()
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def _write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def _fetch_box(bbox: BBox) -> tuple[Path, int]:
    """Make sure the map XML for ``bbox`` is cached; return its file and requests made.

    Raises ``_TooLarge`` when the API refuses the box (the refusal is cached
    too) and ``OsmUnavailable`` on any other failure. Failures are never cached.
    """
    cache_file = _cache_file(bbox)
    refusal = _refusal_file(cache_file)
    params = {"bbox": ",".join(f"{v:.5f}" for v in bbox)}
    made = 0
    last = "no attempt"
    for attempt in range(_RETRIES):
        if cache_file.exists():
            return cache_file, made
        if refusal.exists():
            raise _TooLarge(refusal.read_text()[:200], made)
        if attempt:
            time.sleep(2.0 * 2 ** (attempt - 1))
        try:
            resp = _rate_limited_get(params, cache_file)
        except requests.RequestException as exc:
            made += 1
            last = type(exc).__name__
            continue
        if resp is None:
            continue
        made += 1
        code = resp.status_code
        if code == HTTPStatus.OK:
            _write_atomic(cache_file, gzip.compress(resp.content, compresslevel=5))
            return cache_file, made
        text = " ".join(resp.text[:200].split())
        if code == HTTPStatus.BAD_REQUEST:
            low = text.lower()
            if "too many nodes" in low or "maximum bbox size" in low:
                _write_atomic(refusal, text.encode())
                raise _TooLarge(text, made)
            raise OsmUnavailable(f"OSM API refused the request (HTTP 400): {text}")
        if code in (HTTPStatus.TOO_MANY_REQUESTS, _BANDWIDTH_EXCEEDED):
            raise OsmUnavailable(f"OSM API rate limit reached (HTTP {code}); not retried")
        if code < HTTPStatus.INTERNAL_SERVER_ERROR:
            raise OsmUnavailable(f"OSM API answered HTTP {code}: {text}")
        last = f"HTTP {code}"
    raise OsmUnavailable(f"OSM API unreachable after {_RETRIES} tries ({last})")


# --------------------------------------------------------------------------
# Parsing and geometry
# --------------------------------------------------------------------------

def parse_osm_xml(xml: bytes) -> _Parsed:
    """Parse an OSM API ``map`` response into nodes, ways and relations."""
    parsed = _Parsed()
    for _, elem in ET.iterparse(_stdio.BytesIO(xml), events=("end",)):
        name = elem.tag
        if name not in ("node", "way", "relation"):
            continue
        osm_id = int(elem.attrib["id"])
        tags = {t.attrib["k"]: t.attrib.get("v", "") for t in elem.iterfind("tag")}
        if name == "node":
            if "lon" in elem.attrib and "lat" in elem.attrib:
                parsed.nodes[osm_id] = (float(elem.attrib["lon"]), float(elem.attrib["lat"]))
                if tags:
                    parsed.node_tags[osm_id] = tags
        elif name == "way":
            parsed.ways[osm_id] = ([int(n.attrib["ref"]) for n in elem.iterfind("nd")], tags)
        else:
            members = [(m.attrib.get("type", ""), int(m.attrib["ref"]), m.attrib.get("role", ""))
                       for m in elem.iterfind("member")]
            parsed.relations[osm_id] = (members, tags)
        elem.clear()
    return parsed


@lru_cache(maxsize=4)
def _parsed_file(path: str, mtime_ns: int) -> _Parsed:
    with gzip.open(path, "rb") as handle:
        return parse_osm_xml(handle.read())


def _metres_per_degree(lat: float) -> tuple[float, float]:
    """Metres per degree of longitude and latitude at ``lat`` (WGS84 series)."""
    phi = math.radians(lat)
    ky = 111132.92 - 559.82 * math.cos(2 * phi) + 1.175 * math.cos(4 * phi)
    kx = 111412.84 * math.cos(phi) - 93.5 * math.cos(3 * phi) + 0.118 * math.cos(5 * phi)
    return max(kx, 1000.0), ky


def _way_geometry(local: list[tuple[float, float]], tags: dict[str, str]) -> BaseGeometry:
    if len(local) == 1:
        return Point(local[0])
    if len(local) >= 4 and local[0] == local[-1] and _is_area(tags):
        poly: BaseGeometry = Polygon(local)
        if not poly.is_valid:
            poly = shapely.make_valid(poly)
        if not poly.is_empty:
            return poly
    return LineString(local)


def _build_features(parsed: _Parsed, lat0: float, lon0: float) -> list[_Feature]:
    """Turn tagged elements into geometries in local metres around a point."""
    kx, ky = _metres_per_degree(lat0)
    way_cache: dict[int, tuple[list[tuple[float, float]], list[list[float]]]] = {}

    def to_local(lon: float, lat: float) -> tuple[float, float]:
        return ((lon - lon0) * kx, (lat - lat0) * ky)

    def way_points(way_id: int) -> tuple[list[tuple[float, float]], list[list[float]]]:
        if way_id not in way_cache:
            pts = [parsed.nodes[r] for r in parsed.ways[way_id][0] if r in parsed.nodes]
            way_cache[way_id] = ([to_local(lo, la) for lo, la in pts],
                                 [[round(lo, 7), round(la, 7)] for lo, la in pts])
        return way_cache[way_id]

    out: list[_Feature] = []
    for node_id, tags in parsed.node_tags.items():
        if not _meaningful(tags):
            continue
        lon, lat = parsed.nodes[node_id]
        out.append(_Feature("node", node_id, tags, Point(to_local(lon, lat)),
                            [[round(lon, 7), round(lat, 7)]], classify(tags)))
    for way_id, (_, tags) in parsed.ways.items():
        if not _meaningful(tags):
            continue
        local, lonlat = way_points(way_id)
        if not local:
            continue
        out.append(_Feature("way", way_id, tags, _way_geometry(local, tags), lonlat,
                            classify(tags)))
    for rel_id, (members, tags) in parsed.relations.items():
        if not _meaningful(tags):
            continue
        kind = classify(tags)
        rel_type = tags.get("type", "")
        if kind is None and rel_type not in _KEPT_RELATIONS:
            continue  # routes, turn restrictions: their ways are already features
        outers: list[LineString] = []
        inners: list[LineString] = []
        points: list[Point] = []
        lonlat = []
        for member_type, ref, role in members:
            if member_type == "way" and ref in parsed.ways:
                local, pts = way_points(ref)
                if len(local) >= 2:
                    (inners if role == "inner" else outers).append(LineString(local))
                    lonlat.extend(pts)
            elif member_type == "node" and ref in parsed.nodes:
                lon, lat = parsed.nodes[ref]
                points.append(Point(to_local(lon, lat)))
                lonlat.append([round(lon, 7), round(lat, 7)])
        parts: list[BaseGeometry] = [*outers, *inners, *points]
        if not parts:
            continue  # no member of the relation lies in the extract
        if rel_type in _AREA_RELATIONS and outers:
            try:
                rings = list(polygonize(outers))
                if rings:
                    area = unary_union(rings)
                    holes = list(polygonize(inners)) if inners else []
                    if holes:
                        area = area.difference(unary_union(holes))
                    if not area.is_empty:
                        parts.append(area)  # inside the area the distance is zero
            except GEOSException:
                pass  # keep the outline only
        geom: BaseGeometry = (MultiLineString(parts) if len(parts) == len(outers) + len(inners)
                              else GeometryCollection(parts))
        out.append(_Feature("relation", rel_id, tags, geom, lonlat, kind))
    return out


# --------------------------------------------------------------------------
# Query
# --------------------------------------------------------------------------

def _validate(lat: float, lon: float) -> None:
    if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError(f"invalid coordinates lat={lat!r} lon={lon!r}")


def _query_box(lat: float, lon: float, radius_m: float) -> BBox:
    """Box around a point, snapped outward to a coarse grid.

    Snapping makes neighbouring candidates share one cached response.
    """
    kx, ky = _metres_per_degree(lat)
    step = 0.01 if radius_m >= 2000 else 0.005 if radius_m >= 800 else 0.002
    dlon, dlat = radius_m / kx, radius_m / ky
    west = max(math.floor((lon - dlon) / step) * step, -180.0)
    east = min(math.ceil((lon + dlon) / step) * step, 180.0)
    south = max(math.floor((lat - dlat) / step) * step, -90.0)
    north = min(math.ceil((lat + dlat) / step) * step, 90.0)
    return (round(west, 5), round(south, 5), round(east, 5), round(north, 5))


def _box_area(bbox: BBox) -> float:
    return (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])


def _load(lat: float, lon: float, radius_m: float) -> _Extract:
    """Fetch (or read from cache) and parse the OSM extract around a point.

    When the API refuses the box as too dense, a box of half the radius is
    tried, down to ``MIN_RADIUS_M``; ``covered_radius_m`` reports what the
    extract really covers.
    """
    _validate(lat, lon)
    if not (math.isfinite(radius_m) and radius_m > 0):
        raise ValueError(f"invalid radius {radius_m!r}")
    radius = float(radius_m)
    while _box_area(_query_box(lat, lon, radius)) > MAX_BOX_DEG2 and radius > MIN_RADIUS_M:
        radius *= 0.8
    made = 0
    while True:
        bbox = _query_box(lat, lon, radius)
        try:
            cache_file, count = _fetch_box(bbox)
            made += count
            break
        except _TooLarge as exc:
            made += exc.requests_made
            if radius <= MIN_RADIUS_M:
                raise OsmUnavailable(
                    f"OSM API refuses even a {MIN_RADIUS_M:.0f} m box here (too many nodes)") from exc
            radius = max(radius / 2.0, MIN_RADIUS_M)
    try:
        stat = cache_file.stat()
        parsed = _parsed_file(str(cache_file), stat.st_mtime_ns)
    except (ET.ParseError, OSError, EOFError, KeyError, ValueError) as exc:
        cache_file.unlink(missing_ok=True)
        raise OsmUnavailable(f"OSM response unreadable ({type(exc).__name__}); cache entry dropped") from exc
    kx, ky = _metres_per_degree(lat)
    covered = min((lon - bbox[0]) * kx, (bbox[2] - lon) * kx,
                  (lat - bbox[1]) * ky, (bbox[3] - lat) * ky)
    fetched = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")
    return _Extract(lat, lon, float(radius_m), float(max(covered, 0.0)), bbox, fetched, made,
                    _build_features(parsed, lat, lon))


def _distances(features: list[_Feature], target: BaseGeometry) -> np.ndarray:
    if not features:
        return np.zeros(0, dtype="float64")
    return np.asarray(shapely.distance(np.array([f.geom for f in features], dtype=object), target),
                      dtype="float64")


def osm_query(lat: float, lon: float, radius_m: float = DEFAULT_RADIUS_M) -> dict[str, Any]:
    """Tagged OSM features around a point, with what the extract really covers.

    Returns ``features`` (see ``osm_features``), ``covered_radius_m`` (smaller
    than ``requested_radius_m`` when the API refused a dense area and a smaller
    box was used), ``bbox`` of the extract, ``fetched`` (UTC date the response
    was downloaded) and ``network_requests`` (0 when served from cache).
    Raises ``OsmUnavailable`` when the API fails and ``ValueError`` on invalid input.
    """
    extract = _load(lat, lon, radius_m)
    dist = _distances(extract.features, Point(0.0, 0.0))
    limit = min(float(radius_m), extract.covered_radius_m)
    features = [
        {"osm_type": f.osm_type, "osm_id": f.osm_id, "tags": dict(f.tags),
         "geometry": f.lonlat, "distance_m": round(float(d), 1),
         "geom_type": f.geom.geom_type, "explains": f.kind,
         "is_road": is_road(f.tags), "is_building": is_building(f.tags)}
        for f, d in sorted(zip(extract.features, dist), key=lambda pair: pair[1]) if d <= limit]
    return {"features": features, "requested_radius_m": extract.requested_radius_m,
            "covered_radius_m": round(extract.covered_radius_m, 1), "bbox": list(extract.bbox),
            "fetched": extract.fetched, "network_requests": extract.network_requests}


def osm_features(lat: float, lon: float, radius_m: float = DEFAULT_RADIUS_M) -> list[dict[str, Any]]:
    """Tagged OSM nodes, ways and relations within ``radius_m`` of a point, nearest first.

    Each dict has ``osm_type``, ``osm_id``, ``tags``, ``geometry`` (list of
    ``[lon, lat]`` vertices; for a relation the vertices of its member ways
    present in the extract, concatenated), ``distance_m`` from the point to the
    nearest part of the geometry (0 inside a mapped area), ``geom_type``,
    ``explains`` (the tag that makes it a plausible mundane cause, or None),
    ``is_road`` and ``is_building``. Raises ``OsmUnavailable`` when the API
    fails. Use ``osm_query`` to learn the radius the extract really covers.
    """
    features: list[dict[str, Any]] = osm_query(lat, lon, radius_m)["features"]
    return features


# --------------------------------------------------------------------------
# Check
# --------------------------------------------------------------------------

def _footprint(candidate: Candidate) -> tuple[BaseGeometry, float, float, str]:
    """Footprint in local metres, its size, its reach from the centre and its origin."""
    lat, lon = float(candidate.lat), float(candidate.lon)
    kx, ky = _metres_per_degree(lat)
    area = float(candidate.area_m2) if candidate.area_m2 else 0.0
    area = area if math.isfinite(area) and area > 0 else 0.0
    try:
        west, south, east, north = (float(v) for v in candidate.bbox)
        ok = all(math.isfinite(v) for v in (west, south, east, north)) and west < east and south < north
    except (TypeError, ValueError):
        ok = False
    if ok:
        x0, x1, y0, y1 = (west - lon) * kx, (east - lon) * kx, (south - lat) * ky, (north - lat) * ky
        width, height = x1 - x0, y1 - y0
        centred = x0 - 1000 <= 0 <= x1 + 1000 and y0 - 1000 <= 0 <= y1 + 1000
        if centred and max(width, height) <= 20000:
            reach = max(math.hypot(x, y) for x in (x0, x1) for y in (y0, y1))
            return box(x0, y0, x1, y1), max(width, height, math.sqrt(area)), reach, "bbox"
    radius = math.sqrt(area / math.pi)
    if radius > 0:
        return Point(0.0, 0.0).buffer(radius), 2 * radius, radius, "area_disc"
    return Point(0.0, 0.0), 0.0, 0.0, "point"


def _describe(feature: _Feature, distance: float) -> dict[str, Any]:
    left, bottom, right, top = feature.geom.bounds
    out: dict[str, Any] = {"osm_type": feature.osm_type, "osm_id": feature.osm_id,
                           "kind": feature.kind, "distance_m": round(distance, 1),
                           "extent_m": round(math.hypot(right - left, top - bottom), 1)}
    for key in ("name", "highway"):
        if key in feature.tags:
            out[key] = feature.tags[key]
    return out


def _nearest(features: list[_Feature], dist: np.ndarray, keep: list[bool]) -> tuple[float | None, dict[str, Any] | None]:
    idx = [i for i, flag in enumerate(keep) if flag]
    if not idx:
        return None, None
    best = min(idx, key=lambda i: dist[i])
    return round(float(dist[best]), 1), _describe(features[best], float(dist[best]))


def _evaluate(extract: _Extract, footprint: BaseGeometry, size_m: float, reach_m: float,
              footprint_source: str) -> CheckResult:
    """Decide the check from an extract. Pure: no network, no clock."""
    tolerance = float(np.clip(size_m, *TOLERANCE_RANGE_M))
    features = extract.features
    dist = _distances(features, footprint)
    # Everything within ``reliable`` of the footprint edge is sure to be in the
    # extract; a feature seen farther out is only an upper bound on "nearest".
    reliable = max(extract.covered_radius_m - reach_m, 0.0)
    road_seen, road = _nearest(features, dist, [f.osm_type == "way" and is_road(f.tags) for f in features])
    building_seen, _ = _nearest(features, dist, [is_building(f.tags) for f in features])
    road_m = road_seen if road_seen is not None and road_seen <= reliable else None
    building_m = building_seen if building_seen is not None and building_seen <= reliable else None
    order = sorted((i for i, f in enumerate(features) if f.kind), key=lambda i: dist[i])
    explaining = [_describe(features[i], float(dist[i])) for i in order if dist[i] <= tolerance]
    nearby = [_describe(features[i], float(dist[i])) for i in order
              if tolerance < dist[i] <= reliable]
    needed = reach_m + tolerance
    evidence: dict[str, Any] = {
        "nearest_road_m": road_m, "nearest_building_m": building_m,
        "nearest_road": road if road_m is not None else None,
        "nearest_road_seen_m": road_seen, "nearest_building_seen_m": building_seen,
        "tolerance_m": round(tolerance, 1), "footprint_source": footprint_source,
        "search_radius_m": round(reliable, 1),
        "covered_radius_m": round(extract.covered_radius_m, 1),
        "n_tagged_features": len(features), "explaining": explaining[:5],
        "nearby_beyond_tolerance": nearby[:5], "osm_fetched": extract.fetched,
        "network_requests": extract.network_requests,
        "distance_reference": "footprint edge (0 = intersects)",
    }
    access = (f"nearest road or track {road_m:.0f} m" if road_m is not None
              else f"no road or track within {evidence['search_radius_m']:.0f} m")
    if explaining:
        top = explaining[0]
        label = f"{top['kind']} ({top['osm_type']} {top['osm_id']}" + (
            f", {top['name']}" if "name" in top else "") + ")"
        where = "intersects" if top["distance_m"] == 0 else f"is {top['distance_m']:.0f} m from"
        detail = (f"Footprint {where} mapped {label}; {len(explaining)} explaining feature(s) "
                  f"within {tolerance:.0f} m; {access}.")
        return CheckResult(CHECK_NAME, "infrastructure", "explains", detail, SOURCE, evidence)
    if extract.covered_radius_m < needed:
        detail = (f"OSM extract covers only {extract.covered_radius_m:.0f} m around the point "
                  f"but {needed:.0f} m is needed to judge this footprint (the API refused a "
                  f"larger box as too dense or the box was clipped); nothing explaining was "
                  f"found in the part covered.")
        return CheckResult(CHECK_NAME, "infrastructure", "not_run", detail, SOURCE, evidence)
    what = (f"OpenStreetMap has no tagged feature within {evidence['search_radius_m']:.0f} m"
            if not features else
            f"No mapped quarry, industry, military, aviation, power, building or similar feature "
            f"within {tolerance:.0f} m of the footprint ({len(features)} tagged features in the "
            f"extract; {access}"
            + (f"; nearest building {building_m:.0f} m" if building_m is not None else "")
            + (f"; nearest candidate cause {nearby[0]['kind']} at {nearby[0]['distance_m']:.0f} m"
               if nearby else "") + ")")
    detail = (what + ". OpenStreetMap coverage in remote regions is incomplete, so the absence "
              "of a mapped feature is weak evidence.")
    return CheckResult(CHECK_NAME, "infrastructure", "does_not_explain", detail, SOURCE, evidence)


def check_osm(candidate: Candidate) -> list[CheckResult]:
    """Test whether mapped infrastructure explains a candidate.

    Returns one ``CheckResult`` named ``"osm_infrastructure"``: ``explains``
    when the footprint intersects, or lies within 100-300 m (scaled to its
    size) of, a mapped feature that plausibly causes surface change;
    ``does_not_explain`` when the extract was read and holds none;
    ``not_run`` when the API failed or could not cover the footprint. A plain
    road never explains, but ``evidence`` always carries ``nearest_road_m``
    and ``nearest_building_m``, measured from the footprint edge (None when
    none lies within ``search_radius_m``; ``nearest_road_seen_m`` then gives
    an upper bound if a road was seen farther out).
    """
    try:
        lat, lon = float(candidate.lat), float(candidate.lon)
        _validate(lat, lon)
        footprint, size_m, reach_m, how = _footprint(candidate)
        extract = _load(lat, lon, max(DEFAULT_RADIUS_M, reach_m + 1000.0))
        return [_evaluate(extract, footprint, size_m, reach_m, how)]
    except Exception as exc:  # a failed lookup must never read as "nothing mapped"
        reason = str(exc) if isinstance(exc, (OsmUnavailable, ValueError)) else type(exc).__name__
        return [CheckResult(CHECK_NAME, "infrastructure", "not_run",
                            f"OpenStreetMap could not be queried: {reason}", SOURCE,
                            {"nearest_road_m": None, "nearest_building_m": None,
                             "error": type(exc).__name__})]
