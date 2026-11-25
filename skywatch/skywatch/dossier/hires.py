"""High-resolution imagery for VIEWING finalist candidates.

Esri World Imagery tiles and its dated Wayback versions are fetched for a
handful of finalists only: never in bulk and never as detector input, so this
imagery does not count as an independent sensor. Every candidate is limited to
``MAX_TILES_PER_CANDIDATE`` image tiles, and all responses are cached on disk.

A Wayback release date is the day Esri PUBLISHED that version of the mosaic.
It is not the day the picture was taken, and every label says so.
"""
from __future__ import annotations

import io as _stdio
import json
import logging
import math
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path
from typing import Any, Iterator
from xml.etree import ElementTree

import numpy as np
import requests
from PIL import Image

from skywatch.core import config
from skywatch.core.models import BBox

_log = logging.getLogger(__name__)

WORLD_IMAGERY = "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer"
WAYBACK_CAPABILITIES = ("https://wayback.maptiles.arcgis.com/arcgis/rest/services/"
                        "World_Imagery/MapServer/WMTS/1.0.0/WMTSCapabilities.xml")
#: Tile matrix set of the Wayback service that matches the standard web-mercator pyramid.
WAYBACK_MATRIX_SET = "default028mm"

ATTRIBUTION = ("Esri World Imagery. Source: Esri, Maxar, Earthstar Geographics, "
               "and the GIS User Community")
RELEASE_DATE_MEANING = ("date Esri published this version of the mosaic, "
                        "NOT the date the picture was taken")

#: Hard limit on image tiles used for one candidate (chip plus Wayback series).
MAX_TILES_PER_CANDIDATE = 60
#: Share of the limit a single ``hires_chip`` call may use.
CHIP_TILE_CAP = 36
#: Share of the limit a single ``wayback_series`` call may use (all releases together).
SERIES_TILE_CAP = 24

TILE_PX = 256
MAX_ZOOM = 19
#: Live-mosaic responses are re-fetched after this many days; Wayback releases never change.
LIVE_CACHE_DAYS = 14.0
CAPABILITIES_CACHE_DAYS = 7.0

#: Cache root; a module attribute so tests can redirect it.
CACHE_DIR: Path = config.CACHE / "dossier"

_TIMEOUT = 30.0
_RETRIES = 3
_BACKOFF = 1.5
_RETRY_STATUS = frozenset({HTTPStatus.TOO_MANY_REQUESTS, HTTPStatus.INTERNAL_SERVER_ERROR,
                           HTTPStatus.BAD_GATEWAY, HTTPStatus.SERVICE_UNAVAILABLE,
                           HTTPStatus.GATEWAY_TIMEOUT})
_FETCH_THREADS = 4
_MAX_CHAIN_PROBES = 40
_EQUATOR_RES = 156543.03392804097  # metres per pixel at zoom 0 on the equator
_MAX_LAT = 85.0
_MIN_CHIP_PX = 32
_local = threading.local()


class HiresError(RuntimeError):
    """High-resolution imagery could not be obtained (network, coverage, decode)."""


class TileCapExceeded(HiresError):
    """A request would exceed the per-candidate tile limit."""


# --------------------------------------------------------------------------
# Tile budget
# --------------------------------------------------------------------------

@dataclass
class TileBudget:
    """Counts image tiles used for one candidate against a hard limit."""

    limit: int
    used: int = 0

    @property
    def remaining(self) -> int:
        return max(self.limit - self.used, 0)

    def charge(self, tiles: int) -> None:
        """Reserve ``tiles``; raise ``TileCapExceeded`` rather than overdraw."""
        if tiles > self.remaining:
            raise TileCapExceeded(
                f"{tiles} tiles requested but only {self.remaining} of {self.limit} remain")
        self.used += tiles


_BUDGET: ContextVar[TileBudget | None] = ContextVar("skywatch_dossier_tile_budget", default=None)


@contextmanager
def tile_budget(limit: int = MAX_TILES_PER_CANDIDATE) -> Iterator[TileBudget]:
    """Share one tile budget between all hires calls made for one candidate.

    ``limit`` can only lower the per-candidate limit, never raise it. Cached
    tiles count too, so the same request always yields the same imagery.
    """
    budget = TileBudget(max(0, min(int(limit), MAX_TILES_PER_CANDIDATE)))
    token = _BUDGET.set(budget)
    try:
        yield budget
    finally:
        _BUDGET.reset(token)


def _budget_for(call_cap: int) -> tuple[TileBudget, int]:
    """Budget to charge and the tile cap that applies to this call."""
    shared = _BUDGET.get()
    if shared is None:
        return TileBudget(call_cap), call_cap
    return shared, min(call_cap, shared.remaining)


# --------------------------------------------------------------------------
# HTTP and cache
# --------------------------------------------------------------------------

def _session() -> requests.Session:
    session = getattr(_local, "session", None)
    if session is None:
        session = _local.session = requests.Session()
        session.headers["User-Agent"] = config.USER_AGENT
    return session


def _http_get(url: str, params: dict[str, Any] | None = None) -> bytes:
    """GET with timeout and backoff; ``HiresError`` when the host cannot serve it."""
    last: object = None
    for attempt in range(_RETRIES):
        try:
            response = _session().get(url, params=params, timeout=_TIMEOUT)
        except requests.RequestException as exc:
            last = exc
        else:
            if response.status_code == HTTPStatus.OK:
                return response.content
            last = f"HTTP {response.status_code}"
            if response.status_code not in _RETRY_STATUS:
                break
        if attempt + 1 < _RETRIES:
            time.sleep(_BACKOFF * (attempt + 1))
    raise HiresError(f"request failed: {url}: {last!r}")


def _cached_get(path: Path, url: str, max_age_days: float | None,
                params: dict[str, Any] | None = None) -> bytes:
    """Return a cached response, fetching it when absent or older than allowed.

    A stale copy is still returned when the refresh fails.
    """
    if path.exists():
        age_days = (time.time() - path.stat().st_mtime) / 86400.0
        if max_age_days is None or age_days < max_age_days:
            return path.read_bytes()
    try:
        data = _http_get(url, params)
    except HiresError:
        if path.exists():
            return path.read_bytes()
        raise
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{threading.get_ident()}.tmp")
    tmp.write_bytes(data)
    tmp.replace(path)
    return data


def _tilemap(path: Path, url: str, max_age_days: float | None) -> dict[str, Any] | None:
    """Tile availability record, or None when it cannot be obtained."""
    try:
        info = json.loads(_cached_get(path, url, max_age_days))
    except (HiresError, ValueError):
        return None
    return info if isinstance(info, dict) and isinstance(info.get("data"), list) else None


# --------------------------------------------------------------------------
# Web-mercator tile arithmetic
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class _Plan:
    """Pixel window of a chip in the global pixel space of one zoom level."""

    zoom: int
    left: int
    top: int
    size: int
    tx0: int
    ty0: int
    tx1: int
    ty1: int

    @property
    def n_tiles(self) -> int:
        return max(self.tx1 - self.tx0 + 1, 0) * max(self.ty1 - self.ty0 + 1, 0)

    def tiles(self) -> list[tuple[int, int]]:
        return [(tx, ty) for ty in range(self.ty0, self.ty1 + 1)
                for tx in range(self.tx0, self.tx1 + 1)]


def ground_resolution(lat: float, zoom: int) -> float:
    """Metres per tile pixel at a latitude and zoom level."""
    return _EQUATOR_RES * math.cos(math.radians(lat)) / (2 ** zoom)


def _global_px(lat: float, lon: float, zoom: int) -> tuple[float, float]:
    world = TILE_PX * (2 ** zoom)
    lat = max(min(lat, _MAX_LAT), -_MAX_LAT)
    x = (lon + 180.0) / 360.0 * world
    y = (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * world
    return x, y


def _px_to_lonlat(px: float, py: float, zoom: int) -> tuple[float, float]:
    world = TILE_PX * (2 ** zoom)
    lon = px / world * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1.0 - 2.0 * py / world))))
    return lon, lat


def _plan(lat: float, lon: float, size_m: float, zoom: int) -> _Plan:
    """Square chip of ``size_m`` centred on the point; tiles clamped to the world."""
    res = ground_resolution(max(min(lat, _MAX_LAT), -_MAX_LAT), zoom)
    size = max(1, int(round(size_m / res)))
    cx, cy = _global_px(lat, lon, zoom)
    left, top = int(round(cx - size / 2.0)), int(round(cy - size / 2.0))
    last = 2 ** zoom - 1
    return _Plan(zoom, left, top, size,
                 max(0, left // TILE_PX), max(0, top // TILE_PX),
                 min(last, (left + size - 1) // TILE_PX), min(last, (top + size - 1) // TILE_PX))


def _zoom_for_cap(lat: float, lon: float, size_m: float, cap: int, z_hi: int) -> int:
    """Highest zoom not above ``z_hi`` whose chip needs at most ``cap`` tiles.

    A chip narrower than ``_MIN_CHIP_PX`` shows nothing, so the search stops
    there and raises instead of returning a picture of a whole continent.
    """
    for zoom in range(max(min(z_hi, MAX_ZOOM), 0), -1, -1):
        plan = _plan(lat, lon, size_m, zoom)
        if plan.size < _MIN_CHIP_PX:
            break
        if plan.n_tiles <= cap:
            return zoom
    raise TileCapExceeded(f"no usable zoom level fits a {size_m:.0f} m chip into {cap} tile(s)")


def _plan_bbox(plan: _Plan) -> BBox:
    west, north = _px_to_lonlat(plan.left, plan.top, plan.zoom)
    east, south = _px_to_lonlat(plan.left + plan.size, plan.top + plan.size, plan.zoom)
    return (west, south, east, north)


def chip_xy(meta: dict[str, Any], lat: float, lon: float) -> tuple[float, float]:
    """Fractional (col, row) of a WGS84 point in a chip described by ``meta``."""
    px, py = _global_px(lat, lon, int(meta["zoom"]))
    left, top = meta["origin_px"]
    return px - float(left), py - float(top)


def _check_point(lat: float, lon: float, size_m: float) -> None:
    if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError(f"invalid coordinates: lat={lat!r} lon={lon!r}")
    if not (math.isfinite(size_m) and size_m > 0):
        raise ValueError(f"invalid chip size: {size_m!r}")


# --------------------------------------------------------------------------
# Mosaics
# --------------------------------------------------------------------------

def _decode(data: bytes, where: str) -> np.ndarray:
    try:
        with Image.open(_stdio.BytesIO(data)) as img:
            arr = np.asarray(img.convert("RGB"))
    except Exception as exc:  # PIL raises several unrelated types on bad data
        raise HiresError(f"tile is not a readable image: {where}: {exc!r}") from exc
    if arr.shape != (TILE_PX, TILE_PX, 3):
        raise HiresError(f"unexpected tile shape {arr.shape}: {where}")
    return arr


def _mosaic(plan: _Plan, url_template: str, cache_sub: str,
            max_age_days: float | None) -> np.ndarray:
    """Fetch the tiles of ``plan`` and crop them to the chip; any failed tile is fatal.

    A partly filled picture could be mistaken for a real surface feature, so a
    missing tile raises instead of leaving a hole.
    """
    def one(tile: tuple[int, int]) -> np.ndarray:
        tx, ty = tile
        path = CACHE_DIR / "tiles" / cache_sub / str(plan.zoom) / str(ty) / f"{tx}.jpg"
        url = url_template.format(z=plan.zoom, y=ty, x=tx)
        try:
            return _decode(_cached_get(path, url, max_age_days), url)
        except HiresError:
            path.unlink(missing_ok=True)  # never keep an undecodable response
            raise

    tiles = plan.tiles()
    if not tiles:
        raise HiresError("chip lies outside the tiled world")
    with ThreadPoolExecutor(_FETCH_THREADS) as pool:
        arrays = list(pool.map(one, tiles))
    cols = plan.tx1 - plan.tx0 + 1
    rows = plan.ty1 - plan.ty0 + 1
    canvas = np.zeros((rows * TILE_PX, cols * TILE_PX, 3), dtype="uint8")
    for (tx, ty), arr in zip(tiles, arrays):
        r0, c0 = (ty - plan.ty0) * TILE_PX, (tx - plan.tx0) * TILE_PX
        canvas[r0:r0 + TILE_PX, c0:c0 + TILE_PX] = arr
    out = np.zeros((plan.size, plan.size, 3), dtype="uint8")
    # Window of the chip inside the canvas; parts beyond the world edge stay black.
    off_x, off_y = plan.left - plan.tx0 * TILE_PX, plan.top - plan.ty0 * TILE_PX
    src_x0, src_y0 = max(off_x, 0), max(off_y, 0)
    src_x1 = min(off_x + plan.size, canvas.shape[1])
    src_y1 = min(off_y + plan.size, canvas.shape[0])
    if src_x1 > src_x0 and src_y1 > src_y0:
        out[src_y0 - off_y:src_y1 - off_y, src_x0 - off_x:src_x1 - off_x] = \
            canvas[src_y0:src_y1, src_x0:src_x1]
    return out


# --------------------------------------------------------------------------
# Current World Imagery
# --------------------------------------------------------------------------

def _world_available(plan: _Plan) -> bool | None:
    """Whether every tile of the plan holds real imagery; None when unknown."""
    cols, rows = plan.tx1 - plan.tx0 + 1, plan.ty1 - plan.ty0 + 1
    name = f"{plan.zoom}_{plan.ty0}_{plan.tx0}_{cols}x{rows}.json"
    url = f"{WORLD_IMAGERY}/tilemap/{plan.zoom}/{plan.ty0}/{plan.tx0}/{cols}/{rows}"
    info = _tilemap(CACHE_DIR / "tilemap" / "world_imagery" / name, url, LIVE_CACHE_DAYS)
    if info is None:
        return None
    data = info["data"]
    return len(data) >= cols * rows and all(bool(v) for v in data)


def _acquisition(lat: float, lon: float, zoom: int) -> dict[str, Any]:
    """Esri's own record of the picture under the centre point (best effort)."""
    out: dict[str, Any] = {"acquisition_date": None, "sensor": None, "provider": None,
                           "source_resolution_m": None,
                           "note": "acquisition metadata unavailable"}
    params = {"geometry": f"{lon:.6f},{lat:.6f}", "geometryType": "esriGeometryPoint",
              "sr": 4326, "layers": "all", "tolerance": 1,
              "mapExtent": f"{lon - 0.01:.6f},{lat - 0.01:.6f},{lon + 0.01:.6f},{lat + 0.01:.6f}",
              "imageDisplay": "400,400,96", "returnGeometry": "false", "f": "json"}
    path = CACHE_DIR / "identify" / f"{lat:.5f}_{lon:.5f}.json"
    try:
        results = json.loads(_cached_get(path, f"{WORLD_IMAGERY}/identify",
                                         LIVE_CACHE_DAYS, params)).get("results", [])
    except (HiresError, ValueError, AttributeError) as exc:
        out["note"] = f"acquisition metadata unavailable: {exc!r}"[:200]
        return out
    best: dict[str, Any] | None = None
    for result in results if isinstance(results, list) else []:
        attrs = result.get("attributes", {}) if isinstance(result, dict) else {}
        raw = str(attrs.get("DATE (YYYYMMDD)", ""))
        if not re.fullmatch(r"\d{8}", raw):
            continue
        try:
            in_level = int(attrs.get("MinMapLevel", 0)) <= zoom <= int(attrs.get("MaxMapLevel", 99))
        except (TypeError, ValueError):
            in_level = False
        if best is None or (in_level and not best["in_level"]):
            best = {"attrs": attrs, "raw": raw, "in_level": in_level}
    if best is None:
        out["note"] = "Esri lists no dated source image at this point"
        return out
    attrs, raw = best["attrs"], best["raw"]
    try:
        resolution: float | None = float(attrs.get("RESOLUTION (M)"))
    except (TypeError, ValueError):
        resolution = None
    out.update({
        "acquisition_date": f"{raw[:4]}-{raw[4:6]}-{raw[6:]}",
        "sensor": attrs.get("DESCRIPTION"), "provider": attrs.get("SOURCE"),
        "source_resolution_m": resolution,
        "note": ("per Esri metadata at the centre point of the live mosaic"
                 + ("" if best["in_level"] else "; listed for a different zoom range")),
    })
    return out


def hires_chip(lat: float, lon: float, size_m: float = 1200.0,
               zoom: int | None = None) -> tuple[np.ndarray, dict[str, Any]]:
    """North-up RGB mosaic of Esri World Imagery centred on a point, for viewing.

    Uses the highest zoom (at most ``zoom`` when given) at which every tile
    holds real imagery and the chip needs no more than ``CHIP_TILE_CAP`` tiles
    (less when a shared ``tile_budget`` is nearly spent). Returns the
    ``(size, size, 3)`` uint8 image and metadata: zoom, ground_res_m, source,
    attribution, bbox, origin_px, tiles, imagery_verified and Esri's
    acquisition record for the centre point. Raises ``HiresError`` when the
    imagery cannot be fetched and ``ValueError`` on invalid input.
    """
    _check_point(lat, lon, size_m)
    budget, cap = _budget_for(CHIP_TILE_CAP)
    if cap < 1:
        raise TileCapExceeded("tile budget for this candidate is spent")
    level = _zoom_for_cap(lat, lon, size_m, cap, MAX_ZOOM if zoom is None else int(zoom))
    verified: bool = False
    while True:
        plan = _plan(lat, lon, size_m, level)
        available = _world_available(plan)
        if available is None:
            break
        if available:
            verified = True
            break
        if level == 0:
            raise HiresError("Esri World Imagery reports no imagery at this location")
        level -= 1
    budget.charge(plan.n_tiles)
    template = WORLD_IMAGERY + "/tile/{z}/{y}/{x}"
    image = _mosaic(plan, template, "world_imagery", LIVE_CACHE_DAYS)
    meta: dict[str, Any] = {
        "source": "Esri World Imagery (live mosaic)",
        "attribution": ATTRIBUTION,
        "lat": lat, "lon": lon, "size_m": size_m,
        "zoom": plan.zoom,
        "zoom_requested": zoom,
        "ground_res_m": round(ground_resolution(lat, plan.zoom), 4),
        "shape": [plan.size, plan.size],
        "bbox": list(_plan_bbox(plan)),
        "origin_px": [plan.left, plan.top],
        "tiles": plan.n_tiles,
        "tile_url": template,
        "imagery_verified": verified,
        "retrieved": time.strftime("%Y-%m-%d", time.gmtime()),
        "use": "viewing only; not a detector input and not an independent sensor",
    }
    meta.update(_acquisition(lat, lon, plan.zoom))
    return image, meta


# --------------------------------------------------------------------------
# Wayback
# --------------------------------------------------------------------------

def _parse_capabilities(xml: bytes) -> list[dict[str, Any]]:
    """Releases listed in a Wayback WMTS capabilities document, oldest first."""
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as exc:
        raise HiresError(f"Wayback capabilities are not valid XML: {exc}") from exc

    def local(tag: str) -> str:
        return tag.rsplit("}", 1)[-1]

    releases: list[dict[str, Any]] = []
    for layer in (el for el in root.iter() if local(el.tag) == "Layer"):
        title = ident = template = ""
        for child in layer:
            name = local(child.tag)
            if name == "Title":
                title = (child.text or "").strip()
            elif name == "Identifier":
                ident = (child.text or "").strip()
            elif name == "ResourceURL":
                template = child.get("template", "")
        date = re.search(r"(\d{4}-\d{2}-\d{2})", title)
        num = re.search(r"/tile/(\d+)/", template)
        if not (ident and date and num):
            continue
        url = (template.replace("{TileMatrixSet}", WAYBACK_MATRIX_SET)
               .replace("{TileMatrix}", "{z}").replace("{TileRow}", "{y}")
               .replace("{TileCol}", "{x}"))
        releases.append({"id": ident, "date": date.group(1), "num": int(num.group(1)),
                         "title": title, "tile_url": url,
                         "date_meaning": RELEASE_DATE_MEANING})
    releases.sort(key=lambda r: (r["date"], r["id"]))
    return releases


def wayback_releases() -> list[dict[str, Any]]:
    """Every Esri Wayback release, oldest first.

    Each dict holds ``id`` (e.g. ``WB_2020_R03``), ``date`` (ISO publication
    date of that mosaic version, not an acquisition date), ``num`` (release
    number used in tile URLs), ``title``, ``tile_url`` (template with
    ``{z}/{y}/{x}``) and ``date_meaning``. Raises ``HiresError`` when the
    list cannot be obtained.
    """
    xml = _cached_get(CACHE_DIR / "wayback_capabilities.xml", WAYBACK_CAPABILITIES,
                      CAPABILITIES_CACHE_DAYS)
    releases = _parse_capabilities(xml)
    if not releases:
        raise HiresError("Wayback capabilities list no releases")
    return releases


def _spread(dates: list[str], n: int) -> list[int]:
    """Indices of at most ``n`` dates spread evenly over time, ends included."""
    count = len(dates)
    if n <= 0 or count == 0:
        return []
    if count <= n:
        return list(range(count))
    if n == 1:
        return [count - 1]
    days = np.array([np.datetime64(d[:10]) for d in dates]).astype("datetime64[D]").astype(float)
    targets = np.linspace(days.min(), days.max(), n)
    chosen: list[int] = []
    for target in targets:
        order = np.argsort(np.abs(days - target), kind="stable")
        pick = next(int(i) for i in order if int(i) not in chosen)
        chosen.append(pick)
    return sorted(chosen)


def _version_chain(releases: list[dict[str, Any]], zoom: int, tx: int,
                   ty: int) -> list[int] | None:
    """Indices of the releases in which the tile actually changed, oldest first.

    Walks back from the newest release using the service's own record of which
    release last changed the tile. None when that record cannot be read; an
    empty list when the newest release has no imagery at this zoom.
    """
    by_num = {int(r["num"]): i for i, r in enumerate(releases)}
    chain: list[int] = []
    idx = len(releases) - 1
    for _ in range(_MAX_CHAIN_PROBES):
        if idx < 0:
            break
        num = int(releases[idx]["num"])
        url = releases[idx]["tile_url"].replace("/tile/", "/tilemap/", 1).format(
            z=zoom, y=ty, x=tx)
        info = _tilemap(CACHE_DIR / "tilemap" / "wayback" / f"{num}_{zoom}_{ty}_{tx}.json",
                        url, None)
        if info is None:
            return chain[::-1] if chain else None
        if not info["data"] or not info["data"][0]:
            break
        select = info.get("select")
        effective = idx
        if isinstance(select, list) and select:
            try:
                effective = min(by_num.get(int(select[0]), idx), idx)
            except (TypeError, ValueError):
                effective = idx
        chain.append(effective)
        idx = effective - 1
    return chain[::-1]


def wayback_series(lat: float, lon: float, size_m: float = 1200.0,
                   n: int = 6) -> list[dict[str, Any]]:
    """Chips from at most ``n`` Wayback releases spread over time, oldest first.

    Releases are chosen among those in which the centre tile changed, and
    consecutive chips with identical pixels are dropped (the earliest
    publication is kept), so each returned chip shows different imagery. All
    chips together use at most ``SERIES_TILE_CAP`` tiles, which usually means
    a coarser zoom than ``hires_chip``.

    Each dict holds ``image`` (uint8 RGB), ``release_id``, ``release_date``,
    ``release_num``, ``label``, ``date_meaning``, ``zoom``, ``ground_res_m``,
    ``bbox``, ``origin_px``, ``tiles``, ``tile_url``, ``source``,
    ``attribution`` and ``selection``. ``release_date`` is when Esri published
    that mosaic version, never when the picture was taken. Returns an empty
    list when no release has imagery; raises ``HiresError`` when the release
    list cannot be obtained.
    """
    _check_point(lat, lon, size_m)
    if n <= 0:
        return []
    budget, cap = _budget_for(SERIES_TILE_CAP)
    n = min(int(n), max(cap, 0))
    if n < 1:
        raise TileCapExceeded("tile budget for this candidate is spent")
    releases = wayback_releases()
    level = _zoom_for_cap(lat, lon, size_m, cap // n, MAX_ZOOM)
    selection = "releases in which the centre tile changed"
    chain: list[int] | None = None
    while True:
        plan = _plan(lat, lon, size_m, level)
        cx, cy = _global_px(lat, lon, level)
        chain = _version_chain(releases, level, int(cx // TILE_PX), int(cy // TILE_PX))
        if chain is None or chain or level == 0:
            break
        level -= 1  # the newest release holds no imagery this deep: look coarser
    if chain is None:
        # The change record is unreachable: sample the calendar evenly instead.
        selection = "evenly spaced releases (change record unavailable)"
        chain = list(range(len(releases)))
    if not chain:
        return []
    picked = [chain[i] for i in _spread([releases[i]["date"] for i in chain], n)]
    out: list[dict[str, Any]] = []
    for idx in picked:
        release = releases[idx]
        if plan.n_tiles > budget.remaining:
            _log.warning("wayback series stopped at %s: tile budget spent", release["id"])
            break
        budget.charge(plan.n_tiles)
        try:
            image = _mosaic(plan, release["tile_url"], f"wayback/{release['num']}", None)
        except HiresError as exc:
            _log.warning("wayback release %s skipped: %s", release["id"], exc)
            continue
        if out and np.array_equal(out[-1]["image"], image):
            continue
        out.append({
            "image": image,
            "release_id": release["id"],
            "release_date": release["date"],
            "release_num": release["num"],
            "label": f"Esri release {release['date']} (published; not the acquisition date)",
            "date_meaning": RELEASE_DATE_MEANING,
            "zoom": plan.zoom,
            "ground_res_m": round(ground_resolution(lat, plan.zoom), 4),
            "bbox": list(_plan_bbox(plan)),
            "origin_px": [plan.left, plan.top],
            "tiles": plan.n_tiles,
            "tile_url": release["tile_url"],
            "source": "Esri World Imagery Wayback",
            "attribution": ATTRIBUTION,
            "selection": selection,
        })
    return out
