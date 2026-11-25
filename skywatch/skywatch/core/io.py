"""Catalogue search and pixel access for every sensor, on one common grid.

All detectors work on a ``Grid``: a north-up UTM raster covering a WGS84
bounding box at a fixed resolution. ``read_to_grid`` warps any remote asset
(including GCP-georeferenced Sentinel-1) onto it, reading only the bytes
needed, so arrays from different sensors align pixel for pixel.
"""
from __future__ import annotations

import hashlib
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Sequence

import numpy as np
import planetary_computer
import rasterio
from affine import Affine
from pyproj import Transformer
from pystac import Item
from pystac_client import Client
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
from rasterio.warp import reproject
from scipy import ndimage

from . import config
from .models import BBox

#: Sentinel-2 scene-classification values treated as unusable.
S2_BAD_SCL = (0, 1, 3, 8, 9, 10)
#: Earth Search asset keys for the Sentinel-2 bands the pipeline uses.
S2_BANDS = ("blue", "green", "red", "nir", "swir16", "swir22")

_READ_THREADS = 8
_local = threading.local()


@dataclass(frozen=True)
class Grid:
    """A north-up UTM raster definition shared by all sensors for one area."""

    crs: str
    transform: Affine
    width: int
    height: int
    res: float

    @property
    def shape(self) -> tuple[int, int]:
        return (self.height, self.width)

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        """Projected bounds: left, bottom, right, top."""
        left, top = self.transform * (0, 0)
        right, bottom = self.transform * (self.width, self.height)
        return (left, bottom, right, top)

    def xy_to_lonlat(self, col: float, row: float) -> tuple[float, float]:
        """Pixel centre (col, row) to WGS84 (lon, lat)."""
        x, y = self.transform * (col + 0.5, row + 0.5)
        lon, lat = _transformer(self.crs, "EPSG:4326").transform(x, y)
        return float(lon), float(lat)

    def lonlat_to_xy(self, lon: float, lat: float) -> tuple[float, float]:
        """WGS84 (lon, lat) to fractional pixel (col, row)."""
        x, y = _transformer("EPSG:4326", self.crs).transform(lon, lat)
        col, row = ~self.transform * (x, y)
        return float(col), float(row)

    def bbox_wgs84(self) -> BBox:
        left, bottom, right, top = self.bounds
        tr = _transformer(self.crs, "EPSG:4326")
        xs, ys = tr.transform([left, left, right, right], [bottom, top, bottom, top])
        return (min(xs), min(ys), max(xs), max(ys))


@lru_cache(maxsize=64)
def _transformer(src: str, dst: str) -> Transformer:
    return Transformer.from_crs(src, dst, always_xy=True)


def utm_crs(lon: float, lat: float) -> str:
    """EPSG code of the UTM zone containing a point (polar stereo near poles)."""
    if lat > 84:
        return "EPSG:3413"
    if lat < -80:
        return "EPSG:3031"
    zone = int((lon + 180) // 6) % 60 + 1
    return f"EPSG:{(32600 if lat >= 0 else 32700) + zone}"


def make_grid(bbox: BBox, res: float = 10.0) -> Grid:
    """Build the UTM grid covering ``bbox`` at ``res`` metres per pixel."""
    west, south, east, north = bbox
    crs = utm_crs((west + east) / 2, (south + north) / 2)
    tr = _transformer("EPSG:4326", crs)
    xs, ys = tr.transform([west, west, east, east], [south, north, south, north])
    left = np.floor(min(xs) / res) * res
    top = np.ceil(max(ys) / res) * res
    width = int(np.ceil((max(xs) - left) / res))
    height = int(np.ceil((top - min(ys)) / res))
    return Grid(crs, Affine(res, 0, left, 0, -res, top), width, height, res)


def point_bbox(lat: float, lon: float, half_size_m: float) -> BBox:
    """WGS84 box of roughly ``2 * half_size_m`` metres centred on a point."""
    dlat = half_size_m / 111_320.0
    dlon = half_size_m / (111_320.0 * max(np.cos(np.radians(lat)), 0.05))
    return (lon - dlon, lat - dlat, lon + dlon, lat + dlat)


# --------------------------------------------------------------------------
# Catalogue search
# --------------------------------------------------------------------------

def _client(source: str) -> Client:
    cache = getattr(_local, "clients", None)
    if cache is None:
        cache = _local.clients = {}
    if source not in cache:
        if source == "pc":
            cache[source] = Client.open(config.PLANETARY_COMPUTER)
        elif source == "es":
            cache[source] = Client.open(config.EARTH_SEARCH)
        else:
            raise ValueError(f"unknown STAC source {source!r}")
    return cache[source]


def stac_search(source: str, collection: str, bbox: BBox, datetime: str | None = None,
                query: dict[str, Any] | None = None, max_items: int = 300,
                retries: int = 4) -> list[Item]:
    """Search a STAC catalogue. ``source`` is ``"es"`` (Earth Search) or ``"pc"``.

    Earth Search holds Sentinel-2 L2A as fast public COGs. Planetary Computer
    holds landsat-c2-l2, sentinel-1-grd, aster-l1t, cop-dem-glo-30,
    modis-14A1-061, modis-64A1-061 and sentinel-2-l2a; its assets are signed
    automatically at read time by ``read_to_grid``.
    """
    kwargs: dict[str, Any] = {"collections": [collection], "bbox": list(bbox),
                              "max_items": max_items}
    if datetime:
        kwargs["datetime"] = datetime
    if query:
        kwargs["query"] = query
    last: Exception | None = None
    for attempt in range(retries):
        try:
            return list(_client(source).search(**kwargs).items())
        except Exception as exc:  # network and API errors are retried alike
            last = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"STAC search failed for {collection} after {retries} tries: {last!r}")


def sign(href: str) -> str:
    """Return a readable URL: Planetary Computer blobs need a short-lived token."""
    if ".blob.core.windows.net" in href and "sig=" not in href:
        return planetary_computer.sign(href)
    return href


# --------------------------------------------------------------------------
# Pixel access
# --------------------------------------------------------------------------

def read_to_grid(href: str, grid: Grid, band: int = 1,
                 resampling: Resampling = Resampling.bilinear,
                 retries: int = 4) -> np.ndarray:
    """Warp one band of a remote raster onto ``grid`` as float32.

    Source nodata (and areas outside the source) become NaN. Works for
    rasters with a CRS and for GCP-georeferenced Sentinel-1 GRD.
    """
    last: Exception | None = None
    for attempt in range(retries):
        try:
            with rasterio.open(sign(href)) as src:
                nodata = src.nodata
                if nodata is None and src.dtypes[band - 1].startswith("uint"):
                    nodata = 0
                if src.crs is None:
                    # Sentinel-1 GRD: located by ground control points only.
                    gcps, gcp_crs = src.gcps
                    if not gcps:
                        raise ValueError(f"raster has neither CRS nor GCPs: {href}")
                    out = np.full(grid.shape, np.nan, dtype="float32")
                    reproject(rasterio.band(src, band), out, gcps=gcps, src_crs=gcp_crs,
                              src_nodata=nodata, dst_transform=grid.transform,
                              dst_crs=grid.crs, dst_nodata=np.nan, resampling=resampling)
                    return out
                with WarpedVRT(src, src_nodata=nodata, nodata=np.nan, dtype="float32",
                               crs=grid.crs, transform=grid.transform, width=grid.width,
                               height=grid.height, resampling=resampling) as vrt:
                    return vrt.read(band).astype("float32", copy=False)
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"read failed after {retries} tries: {href.split('?')[0]}: {last!r}")


def read_many(hrefs: Sequence[str], grid: Grid,
              resampling: Resampling = Resampling.bilinear) -> list[np.ndarray | None]:
    """Read several rasters onto ``grid`` in parallel; a failed read is None."""
    def one(href: str) -> np.ndarray | None:
        try:
            return read_to_grid(href, grid, resampling=resampling)
        except Exception:
            return None
    with ThreadPoolExecutor(_READ_THREADS) as pool:
        return list(pool.map(one, hrefs))


# --------------------------------------------------------------------------
# Sentinel-2
# --------------------------------------------------------------------------

def s2_scenes(bbox: BBox, start: str, end: str, max_cloud: float = 20.0,
              max_items: int = 300) -> list[Item]:
    """Sentinel-2 L2A scenes over ``bbox`` between two ISO dates, clearest first."""
    items = stac_search("es", "sentinel-2-l2a", bbox, f"{start}/{end}",
                        query={"eo:cloud_cover": {"lt": max_cloud}}, max_items=max_items)
    return sorted(items, key=lambda it: it.properties.get("eo:cloud_cover", 100.0))


def _s2_offset(item: Item) -> float:
    """DN offset still present in the pixel data (baseline 04.00+ adds 1000)."""
    props = item.properties
    if props.get("earthsearch:boa_offset_applied"):
        return 0.0
    try:
        baseline = float(str(props.get("s2:processing_baseline", "0")))
    except ValueError:
        baseline = 0.0
    return 1000.0 if baseline >= 4.0 else 0.0


def s2_read(item: Item, grid: Grid, bands: Sequence[str] = S2_BANDS,
            mask_dilate: int = 2) -> dict[str, np.ndarray]:
    """Read one Sentinel-2 scene onto ``grid`` as surface reflectance (0..1).

    Cloud, shadow, cirrus and nodata pixels are NaN in every band (using the
    scene classification, dilated by ``mask_dilate`` pixels). The result also
    holds ``"valid"``: a boolean mask of usable pixels.
    """
    hrefs = [item.assets[b].href for b in bands] + [item.assets["scl"].href]
    with ThreadPoolExecutor(_READ_THREADS) as pool:
        arrays = list(pool.map(
            lambda pair: read_to_grid(pair[0], grid, resampling=pair[1]),
            [(h, Resampling.bilinear) for h in hrefs[:-1]] + [(hrefs[-1], Resampling.nearest)]))
    scl = arrays[-1]
    bad = np.isnan(scl) | np.isin(scl, S2_BAD_SCL)
    if mask_dilate:
        bad = ndimage.binary_dilation(bad, iterations=mask_dilate)
    offset = _s2_offset(item)
    out: dict[str, np.ndarray] = {}
    for name, arr in zip(bands, arrays[:-1]):
        refl = (arr - offset) / 10000.0
        refl[bad | np.isnan(arr)] = np.nan
        out[name] = refl
        bad = bad | np.isnan(arr)
    out["valid"] = ~bad
    return out


def s2_composite(grid: Grid, start: str, end: str, bands: Sequence[str] = S2_BANDS,
                 max_scenes: int = 4, max_cloud: float = 20.0,
                 use_cache: bool = True) -> dict[str, Any] | None:
    """Median cloud-free Sentinel-2 composite on ``grid`` for a date window.

    Returns band arrays (reflectance, NaN where never clear), ``"count"``
    (clear observations per pixel), ``"dates"`` and ``"scene_ids"``; None when
    no usable scene exists. Results are cached on disk.
    """
    key = hashlib.sha1(json.dumps(
        [grid.crs, list(grid.transform)[:6], grid.width, grid.height, start, end,
         list(bands), max_scenes, max_cloud]).encode()).hexdigest()[:20]
    cache_file = config.CACHE / "s2_composite" / f"{key}.npz"
    if use_cache and cache_file.exists():
        with np.load(cache_file, allow_pickle=False) as data:
            out: dict[str, Any] = {b: data[b].astype("float32") for b in bands}
            out["count"] = data["count"]
            out["dates"] = [str(d) for d in data["dates"]]
            out["scene_ids"] = [str(s) for s in data["scene_ids"]]
            return out
    items = s2_scenes(grid.bbox_wgs84(), start, end, max_cloud=max_cloud)
    # Pick the clearest acquisition DATES and read every tile of each date, so
    # an area straddling several image tiles is covered completely.
    by_day: dict[str, list[Item]] = {}
    for item in items:
        by_day.setdefault(item.datetime.strftime("%Y-%m-%d"), []).append(item)
    days = sorted(by_day, key=lambda d: np.mean(
        [it.properties.get("eo:cloud_cover", 100.0) for it in by_day[d]]))[:max_scenes]
    chosen: list[Item] = []
    for day in days:
        tiles: dict[str, Item] = {}
        for item in by_day[day]:
            tiles.setdefault(item.properties.get("grid:code", item.id), item)
        chosen.extend(tiles.values())
    if not chosen:
        return None
    stacks: dict[str, list[np.ndarray]] = {b: [] for b in bands}
    count = np.zeros(grid.shape, dtype="uint8")
    used: list[Item] = []
    for item in chosen:
        try:
            scene = s2_read(item, grid, bands)
        except Exception:
            continue
        if scene["valid"].mean() < 0.02:
            continue
        used.append(item)
        count += scene["valid"].astype("uint8")
        for b in bands:
            stacks[b].append(scene[b])
    if not used:
        return None
    out = {}
    with np.errstate(all="ignore"):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            for b in bands:
                out[b] = np.nanmedian(np.stack(stacks[b]), axis=0).astype("float32")
    out["count"] = count
    out["dates"] = sorted({it.datetime.strftime("%Y-%m-%d") for it in used})
    out["scene_ids"] = [it.id for it in used]
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache_file, count=count, dates=np.array(out["dates"]),
                        scene_ids=np.array(out["scene_ids"]),
                        **{b: out[b].astype("float16") for b in bands})
    return out


def rgb_image(red: np.ndarray, green: np.ndarray, blue: np.ndarray,
              lo: float = 2.0, hi: float = 98.0,
              stretch: tuple[float, float] | None = None) -> np.ndarray:
    """Stretch three reflectance bands into a uint8 RGB image for viewing.

    Pass the same ``stretch`` (low, high reflectance) to two images to make a
    before/after pair directly comparable.
    """
    rgb = np.dstack([red, green, blue]).astype("float32")
    if stretch is None:
        finite = rgb[np.isfinite(rgb)]
        if finite.size == 0:
            return np.zeros(rgb.shape, dtype="uint8")
        stretch = (float(np.percentile(finite, lo)), float(np.percentile(finite, hi)))
    low, high = stretch
    scaled = np.clip((rgb - low) / max(high - low, 1e-6), 0, 1)
    scaled[~np.isfinite(scaled)] = 0
    return (scaled ** (1 / 1.4) * 255).astype("uint8")
