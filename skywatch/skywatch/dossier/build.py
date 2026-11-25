"""Evidence dossiers: one folder per candidate that a sceptical human can audit.

A dossier shows the pictures, the measurements and every conventional
explanation that was tried, including the ones that could not be run. It
records an unexplained observation at most and never states an origin.
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import re
import textwrap
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

import matplotlib

matplotlib.use("Agg")

import numpy as np  # noqa: E402
from matplotlib import patheffects  # noqa: E402
from matplotlib.backends.backend_agg import FigureCanvasAgg  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import Polygon, Rectangle  # noqa: E402
from PIL import Image  # noqa: E402

from skywatch.core import config, io  # noqa: E402
from skywatch.core.models import MANDATORY_CHECKS, Candidate, assign_tier  # noqa: E402

from . import hires as hires_mod  # noqa: E402

_log = logging.getLogger(__name__)

#: Fixed closing statement printed at the end of every dossier.
CLOSING_STATEMENT = (
    "This dossier records, at most, an unexplained observation: a surface feature that the "
    "checks listed above did not account for. It makes no claim about what caused the feature "
    "or where it came from. An unexplained observation is not evidence of any particular "
    "origin: checks that were not run, gaps in the data and errors in this pipeline all remain "
    "possible explanations.")

S2_ATTRIBUTION = "Contains modified Copernicus Sentinel data {years} (Sentinel-2 L2A via Earth Search)"
ESRI_NOTE = "Shown for viewing only: not used for detection and not counted as an independent sensor."

MAX_PNG_BYTES = 400_000
S2_FIRST_DAY = date(2015, 7, 1)
WINDOW_DAYS = 365
CONTEXT_HALF_M = 5000.0
WAYBACK_PANELS = 6

_PANEL_FILES = ("before.png", "after.png", "current.png", "falsecolor_before.png",
                "falsecolor_after.png", "falsecolor_current.png", "difference.png",
                "context.png", "timeseries.png", "hires.png", "wayback_strip.png",
                "dossier.json", "dossier.md")
_INSIDE_COLOUR = "#d55e00"
_RING_COLOUR = "#0072b2"
_OUTLINE_COLOUR = "#ffe600"
_STROKE = [patheffects.withStroke(linewidth=2.2, foreground="black")]
#: Colours of outlines, lines and text that must survive palette reduction.
_KEY_COLOURS = (255, 230, 0, 255, 255, 255, 0, 0, 0, 213, 94, 0, 0, 114, 178, 64, 64, 64,
                153, 153, 153, 217, 217, 217)

_SIGNATURE_WORDS = {
    "crash": "a scar resembling an impact or crash mark",
    "landing_trace": "a mark resembling a landing trace",
    "installation": "a structure or installation that the detector flagged",
    "thermal": "a persistent thermal anomaly",
    "unknown": "a surface anomaly of unclassified kind",
}
_STATUS_WORDS = {
    "explains": "EXPLAINS the feature (a sufficient conventional cause was found)",
    "does_not_explain": "ran and did not explain the feature",
    "inconclusive": "ran but was INCONCLUSIVE",
    "not_run": "NOT RUN",
}
_TIER_WORDS = {
    "T0": "explained by a conventional cause",
    "T1": "seen in one sensor only",
    "T2": "confirmed in two independent sensors, but the evidence is incomplete",
    "T3": "dated abrupt onset, and every mandatory check ran without explaining it",
    "T4": "as T3, and an independent report matches in time and place",
}


@dataclass
class _Build:
    """Running record of one dossier build."""

    candidate: Candidate
    folder: Path
    files: dict[str, str] = field(default_factory=dict)
    missing: list[dict[str, str]] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    stats: dict[str, Any] = field(default_factory=dict)

    def skip(self, panel: str, reason: str) -> None:
        self.missing.append({"panel": panel, "reason": reason})
        _log.info("dossier %s: %s omitted: %s", self.candidate.id, panel, reason)

    def attempt(self, panel: str, description: str, make: Callable[[Path], None]) -> bool:
        """Run one panel builder; a failure becomes a note, never an exception."""
        path = self.folder / panel
        try:
            make(path)
        except Exception as exc:  # one broken panel must not sink the dossier
            path.unlink(missing_ok=True)
            self.skip(panel, f"{type(exc).__name__}: {exc}"[:300])
            return False
        self.files[panel] = description
        return True


# --------------------------------------------------------------------------
# Geometry and dates
# --------------------------------------------------------------------------

def _safe_id(candidate_id: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", str(candidate_id)).strip("._")
    return cleaned or "candidate"


def _footprint(candidate: Candidate) -> tuple[float, float, float, float, float, float]:
    """Usable footprint: centre lat, centre lon, bbox; falls back to the point."""
    lat, lon = float(candidate.lat), float(candidate.lon)
    try:
        west, south, east, north = (float(v) for v in candidate.bbox)
        ok = all(math.isfinite(v) for v in (west, south, east, north)) and east > west and north > south
    except (TypeError, ValueError):
        ok = False
    if not ok:
        if not (math.isfinite(lat) and math.isfinite(lon)):
            raise ValueError("candidate has neither a valid bbox nor a valid position")
        west, south, east, north = io.point_bbox(lat, lon, 50.0)
    return ((south + north) / 2.0, (west + east) / 2.0, west, south, east, north)


def _extent_m(candidate: Candidate) -> float:
    lat, _, west, south, east, north = _footprint(candidate)
    width = (east - west) * 111_320.0 * max(math.cos(math.radians(lat)), 0.05)
    return max(width, (north - south) * 111_320.0)


def detail_grid(candidate: Candidate) -> io.Grid:
    """Small Sentinel-2 grid around the footprint (about three footprints wide)."""
    lat, lon, *_ = _footprint(candidate)
    extent = _extent_m(candidate)
    half = min(max(1.5 * extent, 750.0), 6000.0)
    if extent > 8000.0:
        half = 0.75 * extent
    res = 10.0 * max(1, math.ceil(2.0 * half / 12_000.0))
    return io.make_grid(io.point_bbox(lat, lon, half), res=res)


def _context_grid(candidate: Candidate) -> io.Grid:
    lat, lon, *_ = _footprint(candidate)
    half = max(CONTEXT_HALF_M, 1.5 * _extent_m(candidate))
    res = 20.0 * max(1, math.ceil(2.0 * half / 12_000.0))
    return io.make_grid(io.point_bbox(lat, lon, half), res=res)


def _outline_px(candidate: Candidate, to_xy: Callable[[float, float], tuple[float, float]]) -> np.ndarray:
    """Footprint corners as (col, row) pixel coordinates."""
    _, _, west, south, east, north = _footprint(candidate)
    return np.array([to_xy(lon, lat) for lon, lat in
                     ((west, north), (east, north), (east, south), (west, south))], dtype="float64")


def _inside_mask(shape: tuple[int, int], outline: np.ndarray) -> np.ndarray:
    """Pixels inside the footprint rectangle."""
    mask = np.zeros(shape, dtype=bool)
    c0, c1 = int(np.floor(outline[:, 0].min())), int(np.ceil(outline[:, 0].max()))
    r0, r1 = int(np.floor(outline[:, 1].min())), int(np.ceil(outline[:, 1].max()))
    mask[max(r0, 0):max(r1, 0), max(c0, 0):max(c1, 0)] = True
    return mask


def _parse_day(value: Any) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _today() -> date:
    return datetime.now(timezone.utc).date()


def _windows(candidate: Candidate, today: date) -> dict[str, tuple[date, date]]:
    """Composite windows: before/after for a dated onset, otherwise the last year."""
    absent, present = _parse_day(candidate.absent_until), _parse_day(candidate.present_from)
    if absent and present:
        return {"before": (absent - timedelta(days=WINDOW_DAYS), absent),
                "after": (present, min(present + timedelta(days=WINDOW_DAYS), today))}
    return {"current": (today - timedelta(days=WINDOW_DAYS), today)}


# --------------------------------------------------------------------------
# Rasters
# --------------------------------------------------------------------------

def _composite(grid: io.Grid, window: tuple[date, date], today: date) -> dict[str, Any]:
    """Sentinel-2 median composite for a window; raises with a plain reason."""
    start, end = window
    if end < S2_FIRST_DAY or start > today or end < start:
        raise LookupError(f"window {start} to {end} lies outside the Sentinel-2 record "
                          f"({S2_FIRST_DAY} to {today})")
    comp = io.s2_composite(grid, max(start, S2_FIRST_DAY).isoformat(), end.isoformat())
    if comp is None:
        raise LookupError(f"no usable Sentinel-2 scene between {start} and {end}")
    if not any(np.isfinite(comp[b]).any() for b in ("red", "green", "blue")):
        raise LookupError(f"no clear Sentinel-2 pixel between {start} and {end}")
    return comp


def _scene_record(comp: dict[str, Any], window: tuple[date, date], grid: io.Grid) -> dict[str, Any]:
    ids = [str(s) for s in comp.get("scene_ids", [])]
    count = np.asarray(comp.get("count", np.zeros(grid.shape)))
    return {
        "window": [window[0].isoformat(), window[1].isoformat()],
        "acquisition_dates": [str(d) for d in comp.get("dates", [])],
        "scene_ids": ids,
        "scene_urls": [f"{config.EARTH_SEARCH}/collections/sentinel-2-l2a/items/{s}" for s in ids],
        "method": "per-pixel median of the clearest dates, cloud and shadow masked",
        "clear_fraction": round(float((count > 0).mean()), 4) if count.size else 0.0,
        "grid": {"crs": grid.crs, "res_m": grid.res, "shape": list(grid.shape),
                 "bounds": [round(v, 2) for v in grid.bounds],
                 "bbox_wgs84": [round(v, 6) for v in grid.bbox_wgs84()]},
    }


def _stretch(comps: Sequence[dict[str, Any] | None], bands: Sequence[str]) -> tuple[float, float]:
    """One low/high reflectance pair for several composites, so they compare."""
    values = [comp[b][np.isfinite(comp[b])] for comp in comps if comp is not None for b in bands]
    pooled = np.concatenate(values) if values else np.empty(0, dtype="float32")
    if pooled.size == 0:
        return (0.0, 0.3)
    low, high = (float(v) for v in np.percentile(pooled, (2.0, 98.0)))
    return (low, high) if high - low > 1e-4 else (low, low + 0.05)


def _indices(comp: dict[str, Any]) -> dict[str, np.ndarray]:
    """Brightness, NDVI and NBR from a composite."""
    with np.errstate(divide="ignore", invalid="ignore"):
        red, nir, swir = comp["red"], comp["nir"], comp["swir22"]
        return {
            "brightness": (comp["red"] + comp["green"] + comp["blue"]) / 3.0,
            "ndvi": np.where(nir + red != 0, (nir - red) / (nir + red), np.nan),
            "nbr": np.where(nir + swir != 0, (nir - swir) / (nir + swir), np.nan),
        }


def _mean(arr: np.ndarray, mask: np.ndarray) -> float | None:
    values = arr[mask]
    values = values[np.isfinite(values)]
    return round(float(values.mean()), 4) if values.size else None


def _zone_stats(comp: dict[str, Any], inside: np.ndarray) -> dict[str, Any]:
    idx = _indices(comp)
    return {"inside": {k: _mean(v, inside) for k, v in idx.items()},
            "surroundings": {k: _mean(v, ~inside) for k, v in idx.items()}}


# --------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------

def _save_png(img: Image.Image, path: Path, max_bytes: int = MAX_PNG_BYTES) -> int:
    """Write a PNG no larger than ``max_bytes``: palette first, then smaller."""
    img = img.convert("RGB")
    img.save(path, format="PNG", optimize=True)
    if path.stat().st_size <= max_bytes:
        return path.stat().st_size
    work = img
    keys = len(_KEY_COLOURS) // 3
    while True:
        # Median-cut palette of the picture plus the fixed annotation colours,
        # so a thin outline is not repainted in the nearest terrain colour.
        base = work.quantize(colors=256 - keys, method=Image.Quantize.MEDIANCUT,
                             dither=Image.Dither.NONE)
        holder = Image.new("P", (1, 1))
        holder.putpalette(list(base.getpalette() or [])[:(256 - keys) * 3] + list(_KEY_COLOURS))
        work.quantize(palette=holder, dither=Image.Dither.NONE).save(
            path, format="PNG", optimize=True)
        if path.stat().st_size <= max_bytes or min(work.size) < 200:
            return path.stat().st_size
        work = work.resize((max(int(work.width * 0.85), 1), max(int(work.height * 0.85), 1)),
                           Image.Resampling.LANCZOS)


def _save_figure(fig: Figure, path: Path) -> None:
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    _save_png(Image.fromarray(np.asarray(canvas.buffer_rgba())[..., :3].copy()), path)


def _nice_length(target_m: float) -> float:
    exponent = 10.0 ** math.floor(math.log10(max(target_m, 1e-6)))
    for factor in (5.0, 2.0, 1.0):
        if factor * exponent <= target_m:
            return factor * exponent
    return exponent


def _decorate(ax: Any, width: int, height: int, res_m: float,
              outlines: Sequence[tuple[np.ndarray, str, str]] = ()) -> None:
    """Footprint outlines, scale bar and north arrow on an image axis."""
    for xy, colour, style in outlines:
        patch = Polygon(xy, closed=True, fill=False, edgecolor=colour, linewidth=1.4,
                        linestyle=style)
        if colour != "black":
            patch.set_path_effects([patheffects.withStroke(linewidth=2.8, foreground="black")])
        ax.add_patch(patch)
    length_m = _nice_length(0.25 * width * res_m)
    bar_px = length_m / res_m
    x0, y0 = 0.04 * width, 0.955 * height
    ax.add_patch(Rectangle((x0, y0), bar_px, 0.012 * height, facecolor="white",
                           edgecolor="black", linewidth=0.8))
    label = f"{length_m / 1000:g} km" if length_m >= 1000 else f"{length_m:g} m"
    ax.text(x0 + bar_px / 2, y0 - 0.008 * height, label, color="white", fontsize=8,
            ha="center", va="bottom", path_effects=_STROKE)
    ax.annotate("N", xy=(0.955, 0.975), xytext=(0.955, 0.875), xycoords="axes fraction",
                color="white", fontsize=9, ha="center", va="center", path_effects=_STROKE,
                arrowprops={"arrowstyle": "-|>", "color": "white", "linewidth": 1.4,
                            "path_effects": _STROKE})
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)


def _image_figure(path: Path, rgb: np.ndarray, title: str, attribution: str, res_m: float,
                  outlines: Sequence[tuple[np.ndarray, str, str]] = ()) -> None:
    height, width = rgb.shape[:2]
    fig = Figure(figsize=(6.6, 6.6 * height / max(width, 1) * 0.9 + 1.0), dpi=100)
    ax = fig.add_axes((0.02, 0.06, 0.96, 0.82))
    ax.imshow(rgb, extent=(0, width, height, 0), interpolation="nearest")
    ax.set_axis_off()
    _decorate(ax, width, height, res_m, outlines)
    fig.text(0.5, 0.985, title, ha="center", va="top", fontsize=9)
    fig.text(0.02, 0.012, textwrap.fill(attribution, 135), ha="left", va="bottom",
             fontsize=6.5, color="0.25")
    _save_figure(fig, path)


def _years(dates: Sequence[str]) -> str:
    years = sorted({str(d)[:4] for d in dates})
    return ", ".join(years) if years else "(year unknown)"


def _chip_title(kind: str, phase: str, comp: dict[str, Any], window: tuple[date, date],
                res: float) -> str:
    dates = [str(d) for d in comp.get("dates", [])]
    return (f"{phase}: Sentinel-2 {kind} ({res:g} m, north up), median of {len(dates)} clear "
            f"acquisition date(s)\nacquired {', '.join(dates) or 'unknown'} "
            f"(window {window[0]} to {window[1]})")


def _difference_figure(path: Path, before: dict[str, Any], after: dict[str, Any],
                       outline: np.ndarray, res: float) -> None:
    b, a = _indices(before), _indices(after)
    panels = (("brightness", "Visible brightness change (reflectance)", "RdBu_r", 0.05),
              ("ndvi", "NDVI change (vegetation index)", "BrBG", 0.10))
    height, width = before["red"].shape
    fig = Figure(figsize=(9.2, 4.6 * height / max(width, 1) + 1.5), dpi=100)
    for i, (key, label, cmap_name, floor) in enumerate(panels):
        delta = a[key] - b[key]
        finite = np.abs(delta[np.isfinite(delta)])
        limit = max(float(np.percentile(finite, 98.0)) if finite.size else 0.0, floor)
        # Stepped colours: honest about the precision shown, and they compress
        # without the palette reduction that would band a smooth colour bar.
        cmap = matplotlib.colormaps[cmap_name].resampled(15).with_extremes(bad="0.6")
        ax = fig.add_axes((0.02 + 0.49 * i, 0.19, 0.47, 0.68))
        shown = ax.imshow(np.ma.masked_invalid(delta), cmap=cmap, vmin=-limit, vmax=limit,
                          extent=(0, width, height, 0), interpolation="nearest")
        ax.set_axis_off()
        ax.set_title(label, fontsize=9)
        _decorate(ax, width, height, res, [(outline, "black", "-")])
        cax = fig.add_axes((0.06 + 0.49 * i, 0.12, 0.39, 0.025))
        bar = fig.colorbar(shown, cax=cax, orientation="horizontal")
        bar.ax.tick_params(labelsize=7)
    fig.text(0.5, 0.985, "Difference: after minus before (grey = no clear pixel in one of the two)",
             ha="center", va="top", fontsize=10)
    dates = list(before.get("dates", [])) + list(after.get("dates", []))
    fig.text(0.02, 0.015, S2_ATTRIBUTION.format(years=_years(dates)), fontsize=6.5, color="0.25")
    _save_figure(fig, path)


def _series_arrays(series: Any) -> tuple[list[str], dict[str, dict[str, np.ndarray]]]:
    """Validate the detector's series; raises ``ValueError`` when unusable."""
    if not isinstance(series, dict) or not series.get("dates"):
        raise ValueError("series holds no dates")
    dates = [str(d) for d in series["dates"]]
    out: dict[str, dict[str, np.ndarray]] = {}
    for zone in ("inside", "ring"):
        raw = series.get(zone)
        if not isinstance(raw, dict):
            raise ValueError(f"series lacks the '{zone}' group")
        out[zone] = {}
        for key in ("brightness", "ndvi", "nbr"):
            values = np.array([np.nan if v is None else float(v) for v in raw.get(key, [])],
                              dtype="float64")
            padded = np.full(len(dates), np.nan)
            padded[:min(len(dates), values.size)] = values[:len(dates)]
            out[zone][key] = padded
    if not any(np.isfinite(v).any() for zone in out.values() for v in zone.values()):
        raise ValueError("series holds no finite value")
    return dates, out


def _timeseries_figure(path: Path, candidate: Candidate) -> None:
    dates, zones = _series_arrays(candidate.measurements.get("series"))
    try:
        x: np.ndarray = np.array([np.datetime64(d[:10]) for d in dates]).astype("datetime64[D]")
        dated = True
    except ValueError:
        x, dated = np.arange(len(dates)), False
    fig = Figure(figsize=(7.4, 6.4), dpi=100)
    axes = fig.subplots(3, 1, sharex=True)
    fig.subplots_adjust(left=0.11, right=0.97, top=0.88, bottom=0.11, hspace=0.12)
    absent, present = _parse_day(candidate.absent_until), _parse_day(candidate.present_from)
    for ax, key, label in zip(axes, ("brightness", "ndvi", "nbr"),
                              ("Brightness", "NDVI", "NBR")):
        if dated and absent and present:
            ax.axvspan(np.datetime64(absent), np.datetime64(present), color="0.85", zorder=0,
                       label="onset window (last absent to first present)")
        ax.plot(x, zones["inside"][key], color=_INSIDE_COLOUR, marker="o", markersize=3.5,
                linewidth=1.4, label="inside footprint")
        ax.plot(x, zones["ring"][key], color=_RING_COLOUR, marker="s", markersize=3,
                linewidth=1.2, linestyle="--", label="surrounding ring")
        ax.set_ylabel(label, fontsize=9)
        ax.tick_params(labelsize=8)
        ax.grid(True, color="0.9", linewidth=0.6)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.54, 0.945),
               frameon=False, ncols=3)
    if not dated:
        axes[-1].set_xlabel("observation number (dates could not be parsed)", fontsize=8)
    note = "" if (absent and present) else " (no dated onset window to shade)"
    fig.text(0.5, 0.975, f"Time series inside the footprint versus the surrounding ring{note}",
             ha="center", va="top", fontsize=10)
    fig.text(0.02, 0.012, f"Series as recorded by detector '{candidate.detector}'. "
             + S2_ATTRIBUTION.format(years=_years(dates)), fontsize=6.5, color="0.25")
    _save_figure(fig, path)


def _fit(image: np.ndarray, max_px: int) -> tuple[np.ndarray, float]:
    """Shrink an image to at most ``max_px`` on its long side; returns the scale."""
    long_side = max(image.shape[:2])
    if long_side <= max_px:
        return image, 1.0
    scale = max_px / long_side
    size = (max(int(round(image.shape[1] * scale)), 1), max(int(round(image.shape[0] * scale)), 1))
    return np.asarray(Image.fromarray(image).resize(size, Image.Resampling.LANCZOS)), scale


def _hires_figure(path: Path, candidate: Candidate, image: np.ndarray, meta: dict[str, Any]) -> None:
    shown, scale = _fit(image, 720)
    outline = _outline_px(candidate, lambda lon, lat: hires_mod.chip_xy(meta, lat, lon)) * scale
    acquired = meta.get("acquisition_date")
    when = (f"picture taken {acquired} ({meta.get('sensor') or 'sensor not stated'}), "
            f"{meta.get('note', '')}" if acquired else "acquisition date not available")
    title = (f"High-resolution view: Esri World Imagery, zoom {meta['zoom']}, "
             f"{meta['ground_res_m']:.2f} m per pixel at source, north up\n{when}")
    _image_figure(path, shown, title, f"{hires_mod.ATTRIBUTION}. {ESRI_NOTE}",
                  float(meta["ground_res_m"]) / scale, [(outline, _OUTLINE_COLOUR, "-")])


def _wayback_figure(path: Path, candidate: Candidate, series: list[dict[str, Any]]) -> None:
    cols = min(len(series), 3)
    rows = math.ceil(len(series) / cols)
    fig = Figure(figsize=(3.0 * cols + 0.2, 3.25 * rows + 0.9), dpi=100)
    top, bottom = 1.0 - 0.55 / fig.get_figheight(), 0.45 / fig.get_figheight()
    cell_h = (top - bottom) / rows
    for i, chip in enumerate(series):
        row, col = divmod(i, cols)
        ax = fig.add_axes((0.01 + col / cols * 0.98, top - (row + 1) * cell_h,
                           0.98 / cols - 0.01, cell_h * 0.86))
        shown, scale = _fit(chip["image"], 300)
        height, width = shown.shape[:2]
        ax.imshow(shown, extent=(0, width, height, 0), interpolation="nearest")
        ax.set_axis_off()
        outline = _outline_px(candidate, lambda lon, lat, c=chip: hires_mod.chip_xy(c, lat, lon))
        _decorate(ax, width, height, float(chip["ground_res_m"]) / scale,
                  [(outline * scale, _OUTLINE_COLOUR, "-")])
        ax.set_title(f"published {chip['release_date']} ({chip['release_id']})", fontsize=8)
    fig.text(0.5, 1.0 - 0.06 / fig.get_figheight(),
             "Esri Wayback: successive published versions of the World Imagery mosaic",
             ha="center", va="top", fontsize=10)
    fig.text(0.01, 0.012, "Dates are when Esri PUBLISHED each version of the mosaic, NOT when the "
             f"pictures were taken.\n{hires_mod.ATTRIBUTION}. {ESRI_NOTE}",
             fontsize=6.5, color="0.25", va="bottom")
    _save_figure(fig, path)


# --------------------------------------------------------------------------
# Panels
# --------------------------------------------------------------------------

def _load_composites(build: _Build, grid: io.Grid, today: date) -> dict[str, dict[str, Any]]:
    """Read the before/after (or current) composites, noting each failure."""
    comps: dict[str, dict[str, Any]] = {}
    build.provenance["sentinel2"] = {}
    for phase, window in _windows(build.candidate, today).items():
        try:
            comp = _composite(grid, window, today)
        except Exception as exc:  # network, catalogue and coverage failures alike
            for panel in (f"{phase}.png", f"falsecolor_{phase}.png"):
                build.skip(panel, f"{type(exc).__name__}: {exc}"[:300])
            continue
        comps[phase] = comp
        build.provenance["sentinel2"][phase] = _scene_record(comp, window, grid)
    return comps


def _optical_panels(build: _Build, today: date) -> None:
    candidate = build.candidate
    grid = detail_grid(candidate)
    windows = _windows(candidate, today)
    comps = _load_composites(build, grid, today)
    outline = _outline_px(candidate, grid.lonlat_to_xy)
    inside = _inside_mask(grid.shape, outline)
    marks = [(outline, _OUTLINE_COLOUR, "-")]
    true_stretch = _stretch(list(comps.values()), ("red", "green", "blue"))
    false_stretch = _stretch(list(comps.values()), ("swir16", "nir", "red"))
    phase_words = {"before": "BEFORE onset", "after": "AFTER onset",
                   "current": "CURRENT (no dated onset)"}
    for phase, comp in comps.items():
        build.stats.setdefault("footprint_vs_surroundings", {})[phase] = _zone_stats(comp, inside)
        attribution = S2_ATTRIBUTION.format(years=_years(comp.get("dates", [])))
        attribution += ". Yellow outline: candidate footprint (bbox)."
        build.attempt(
            f"{phase}.png", f"Sentinel-2 true colour, {phase_words[phase]}",
            lambda path, c=comp, p=phase, a=attribution: _image_figure(
                path, io.rgb_image(c["red"], c["green"], c["blue"], stretch=true_stretch),
                _chip_title("true colour", phase_words[p], c, windows[p], grid.res),
                a, grid.res, marks))
        build.attempt(
            f"falsecolor_{phase}.png",
            f"Sentinel-2 false colour (SWIR1, NIR, red), {phase_words[phase]}",
            lambda path, c=comp, p=phase, a=attribution: _image_figure(
                path, io.rgb_image(c["swir16"], c["nir"], c["red"], stretch=false_stretch),
                _chip_title("false colour (SWIR1, NIR, red)", phase_words[p], c, windows[p],
                            grid.res),
                a, grid.res, marks))
    if "before" in comps and "after" in comps:
        build.attempt("difference.png", "After minus before: brightness and NDVI change",
                      lambda path: _difference_figure(path, comps["before"], comps["after"],
                                                      outline, grid.res))
    elif "current" in windows:
        build.skip("difference.png", "no dated onset window, so there is no before/after pair")
    else:
        build.skip("difference.png", "needs both the before and the after composite")


def _context_panel(build: _Build, today: date) -> None:
    candidate = build.candidate
    windows = _windows(candidate, today)
    phase = "after" if "after" in windows else "current"

    def make(path: Path) -> None:
        grid = _context_grid(candidate)
        comp = _composite(grid, windows[phase], today)
        build.provenance["sentinel2"]["context"] = _scene_record(comp, windows[phase], grid)
        detail = detail_grid(candidate)
        left, bottom, right, top = detail.bounds
        inv = ~grid.transform
        box = np.array([inv @ (left, top), inv @ (right, top), inv @ (right, bottom),
                        inv @ (left, bottom)], dtype="float64")
        dates = [str(d) for d in comp.get("dates", [])]
        width_km = grid.width * grid.res / 1000.0
        title = (f"Context: about {width_km:.0f} km across, Sentinel-2 true colour "
                 f"({grid.res:g} m, north up)\nacquired {', '.join(dates) or 'unknown'}")
        attribution = (S2_ATTRIBUTION.format(years=_years(dates))
                       + ". Yellow: footprint. Dashed white: area of the detail panels.")
        _image_figure(path, io.rgb_image(comp["red"], comp["green"], comp["blue"]), title,
                      attribution, grid.res,
                      [(box, "white", "--"),
                       (_outline_px(candidate, grid.lonlat_to_xy), _OUTLINE_COLOUR, "-")])

    build.provenance.setdefault("sentinel2", {})
    build.attempt("context.png", "Wider setting with the footprint marked", make)


def _timeseries_panel(build: _Build) -> None:
    if "series" not in build.candidate.measurements:
        build.skip("timeseries.png", "the detector recorded no time series "
                                     "(measurements['series'] is absent)")
        return
    build.attempt("timeseries.png", "Brightness, NDVI and NBR inside the footprint versus the ring",
                  lambda path: _timeseries_figure(path, build.candidate))


def _hires_panels(build: _Build) -> None:
    candidate = build.candidate
    lat, lon, *_ = _footprint(candidate)
    extent = _extent_m(candidate)
    record: dict[str, Any] = {"note": ESRI_NOTE}
    build.provenance["esri"] = record
    with hires_mod.tile_budget() as budget:
        def chip(path: Path) -> None:
            image, meta = hires_mod.hires_chip(lat, lon, size_m=min(max(1.4 * extent, 800.0), 4000.0))
            record["hires"] = meta
            _hires_figure(path, candidate, image, meta)

        def strip(path: Path) -> None:
            series = hires_mod.wayback_series(lat, lon, size_m=min(max(1.3 * extent, 600.0), 3000.0),
                                              n=WAYBACK_PANELS)
            if not series:
                raise LookupError("no Wayback release holds imagery here")
            record["wayback"] = [{k: v for k, v in item.items() if k != "image"}
                                 for item in series]
            _wayback_figure(path, candidate, series)

        build.attempt("hires.png", "Esri World Imagery view (viewing only)", chip)
        build.attempt("wayback_strip.png",
                      "Esri Wayback versions; dates are publication dates, not acquisition dates",
                      strip)
        record["tiles_used"] = budget.used
        record["tile_limit"] = budget.limit


# --------------------------------------------------------------------------
# Text
# --------------------------------------------------------------------------

def _clean(value: Any) -> Any:
    """JSON-safe copy: numpy types unwrapped, non-finite numbers as null."""
    if isinstance(value, dict):
        return {str(k): _clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_clean(v) for v in value]
    if isinstance(value, np.ndarray):
        return _clean(value.tolist())
    if isinstance(value, np.generic):
        return _clean(value.item())
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    return str(value)


def _one_line(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text)).strip()


def _fmt(value: Any) -> str:
    if isinstance(value, bool) or value is None:
        return str(value)
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)):
        number = float(value)
        return f"{number:,.0f}" if math.isfinite(number) and abs(number) >= 1000 else f"{number:.4g}"
    if isinstance(value, (dict, list, tuple)):
        text = json.dumps(_clean(value), default=str)
        return text if len(text) <= 300 else text[:297] + "..."
    return _one_line(value)


def _tier(candidate: Candidate) -> dict[str, Any]:
    """Recorded tier, with a recomputation from the recorded evidence."""
    computed, reason = assign_tier(candidate)
    record: dict[str, Any] = {"recomputed_tier": computed, "recomputed_reason": reason}
    if candidate.tier:
        record.update({"tier": candidate.tier, "reason": candidate.tier_reason,
                       "source": "recorded on the candidate",
                       "consistent": candidate.tier == computed})
    else:
        record.update({"tier": computed, "reason": reason, "consistent": True,
                       "source": "computed from the recorded evidence when the dossier was built"})
    return record


def _not_run(candidate: Candidate) -> list[dict[str, str]]:
    """Checks that did not run, including mandatory checks never attempted."""
    out = [{"check": c.check, "reason": _one_line(c.detail) or "no reason recorded",
            "mandatory": str(c.check in MANDATORY_CHECKS).lower()}
           for c in candidate.checks if c.status == "not_run"]
    seen = {c.check for c in candidate.checks}
    out += [{"check": name, "reason": "never attempted: no result is recorded for this check",
             "mandatory": "true"} for name in MANDATORY_CHECKS if name not in seen]
    return out


def _markdown(build: _Build, tier: dict[str, Any], not_run: list[dict[str, str]]) -> str:
    c = build.candidate
    lat, lon, west, south, east, north = _footprint(c)
    absent, present = _parse_day(c.absent_until), _parse_day(c.present_from)
    lines: list[str] = [f"# Dossier: candidate {c.id}", ""]
    add = lines.append

    add("## What was detected")
    add(f"The detector `{c.detector}` flagged {_SIGNATURE_WORDS.get(c.signature, 'a surface anomaly')} "
        f"(signature class `{c.signature}`). The class describes what the mark looks like in the "
        "imagery; it is not a statement about what made it.")
    add("")
    add(f"Detector score: {_fmt(c.score)} on a 0 to 1 scale. This is the detector's own measure of "
        "how strong the signal is, not a probability of anything.")
    if c.notes:
        add("")
        add(f"Notes: {_one_line(c.notes)}")
    add("")

    add("## Where")
    add(f"- Position: {c.lat:.5f} N, {c.lon:.5f} E (WGS84; negative values mean south or west)")
    add(f"- Footprint (west, south, east, north): {west:.5f}, {south:.5f}, {east:.5f}, {north:.5f}; "
        f"centre {lat:.5f}, {lon:.5f}")
    add(f"- Area: {_fmt(c.area_m2)} m2")
    add(f"- Search region: `{c.region_id}`")
    add("")

    add("## When")
    if absent and present:
        add(f"The feature is absent in imagery up to {absent} and present from {present}. "
            "It appeared at some time between those two dates; the pipeline cannot say when "
            "within that window.")
    else:
        add("No dated onset: the pipeline has no pair of dates bracketing the appearance "
            f"(absent_until = {c.absent_until!r}, present_from = {c.present_from!r}). "
            "Only a current view is shown.")
    add("")

    add("## Measurements")
    add(f"- Sensor families in which the feature is seen: {', '.join(c.sensors) or 'none recorded'}")
    for name, value in c.measurements.items():
        if name == "series" and isinstance(value, dict):
            add(f"- series: time series with {len(value.get('dates', []))} dates "
                "(plotted in timeseries.png when usable; full values in dossier.json)")
        else:
            add(f"- {name}: {_fmt(value)}")
    for name, value in c.shape.items():
        add(f"- shape.{name}: {_fmt(value)}")
    if not c.measurements and not c.shape:
        add("- The detector recorded no further measurements.")
    zones = build.stats.get("footprint_vs_surroundings", {})
    if zones:
        add("")
        add("Mean values in the dossier's own Sentinel-2 composites (inside the footprint / "
            "rest of the detail panel):")
        for phase, zone in zones.items():
            parts = [f"{key} {_fmt(zone['inside'][key])} / {_fmt(zone['surroundings'][key])}"
                     for key in ("brightness", "ndvi", "nbr")]
            add(f"- {phase}: " + "; ".join(parts))
    add("")

    add("## Conventional explanations tested")
    if not c.checks:
        add("No check result is recorded for this candidate. Nothing has been ruled out.")
    for check in c.checks:
        add(f"- **{check.check}** ({check.category}): {_STATUS_WORDS.get(check.status, check.status)}. "
            f"{_one_line(check.detail) or 'No detail recorded.'}"
            + (f" Source: {_one_line(check.source)}." if check.source else ""))
    add("")

    add("## Checks that were NOT run")
    if not_run:
        add("A check that did not run rules nothing out. These explanations remain open:")
        for item in not_run:
            flag = " (mandatory)" if item["mandatory"] == "true" else ""
            add(f"- **{item['check']}**{flag}: {item['reason']}")
    else:
        add("Every recorded check ran, and every mandatory check has a result.")
    add("")

    add("## Evidence tier")
    add(f"**{tier['tier']}**: {_TIER_WORDS.get(str(tier['tier']), 'unknown tier')}.")
    add("")
    add(f"Reason: {_one_line(tier['reason']) or 'none recorded'} ({tier['source']}).")
    add("")
    if not tier["consistent"]:
        add(f"Warning: recomputing the tier from the recorded evidence gives "
            f"{tier['recomputed_tier']} ({tier['recomputed_reason']}), which differs from the "
            "recorded tier. Treat the lower of the two as the valid one.")
        add("")
    add("The tier ladder measures how much of the evidence is in place. Its top means "
        "\"unexplained after every check\", never \"identified\".")
    add("")

    if c.reports:
        add("## Witness reports matched in place and time")
        for report in c.reports:
            add(f"- {_fmt(report)}")
        add("")

    add("## Figures")
    for name, description in build.files.items():
        if name.endswith(".png"):
            add(f"- `{name}`: {description}")
    esri = build.provenance.get("esri", {})
    if "hires" in esri:
        acquired = esri["hires"].get("acquisition_date")
        add("- The Esri picture in `hires.png` "
            + (f"was taken on {acquired} according to Esri's metadata for the centre point."
               if acquired else "has no known acquisition date.")
            + " Compare that date with the onset window before reading anything into it.")
    if "wayback" in esri:
        add("- The dates in `wayback_strip.png` are the dates on which Esri published each "
            "version of its mosaic. They are NOT the dates on which the pictures were taken; "
            "a picture can be months or years older than its publication.")
    if esri:
        add(f"- {ESRI_NOTE}")
    add("")

    add("## Panels that could not be produced")
    if build.missing:
        for item in build.missing:
            add(f"- `{item['panel']}`: {item['reason']}")
    else:
        add("None: every panel was produced.")
    add("")

    add("## Data provenance")
    for phase, record in build.provenance.get("sentinel2", {}).items():
        add(f"- Sentinel-2 `{phase}` composite, window {record['window'][0]} to "
            f"{record['window'][1]}: scenes {', '.join(record['scene_ids']) or 'none'}")
    if not build.provenance.get("sentinel2"):
        add("- No Sentinel-2 composite could be read.")
    add("- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.")
    add("")

    add("## Closing statement")
    add(CLOSING_STATEMENT)
    add("")
    return "\n".join(lines)


def _file_records(build: _Build) -> list[dict[str, Any]]:
    records = []
    for name, description in build.files.items():
        path = build.folder / name
        if path.exists():
            records.append({"name": name, "description": description,
                            "bytes": path.stat().st_size,
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return records


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def build_dossier(candidate: Candidate, out_dir: Path | None = None, hires: bool = True) -> Path:
    """Write the evidence folder for one candidate and return its path.

    The folder is ``<out_dir>/<candidate id>/`` with ``out_dir`` defaulting to
    ``config.OUTPUT / "dossiers"`` (unsafe characters in the id become ``_``).
    It always holds ``dossier.json`` and ``dossier.md``; each figure is
    written when its data can be read, and every figure that could not be
    made is listed with the reason in both documents. Network and data
    failures never raise. The candidate is not modified, and Esri imagery
    (``hires=True``) is for viewing only: it adds no sensor.
    """
    root = Path(out_dir) if out_dir is not None else config.OUTPUT / "dossiers"
    folder = root / _safe_id(candidate.id)
    folder.mkdir(parents=True, exist_ok=True)
    for name in _PANEL_FILES:  # a rebuild must not leave panels from an older run
        (folder / name).unlink(missing_ok=True)
    build = _Build(candidate, folder)
    today = _today()
    steps: list[tuple[str, Callable[[], None]]] = [
        ("Sentinel-2 detail panels", lambda: _optical_panels(build, today)),
        ("context.png", lambda: _context_panel(build, today)),
        ("timeseries.png", lambda: _timeseries_panel(build)),
    ]
    if hires:
        steps.append(("hires.png and wayback_strip.png", lambda: _hires_panels(build)))
    else:
        build.skip("hires.png", "high-resolution imagery was not requested (hires=False)")
        build.skip("wayback_strip.png", "high-resolution imagery was not requested (hires=False)")
    for name, step in steps:
        try:
            step()
        except Exception as exc:  # the dossier text must be written whatever happens
            build.skip(name, f"{type(exc).__name__}: {exc}"[:300])

    tier = _tier(candidate)
    not_run = _not_run(candidate)
    (folder / "dossier.md").write_text(_markdown(build, tier, not_run), encoding="utf-8")
    build.files["dossier.md"] = "Plain-language summary"
    document = {
        "schema": "skywatch.dossier/1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "candidate": candidate.to_json(),
        "tier": tier,
        "checks": [check.__dict__ for check in candidate.checks],
        "checks_not_run": not_run,
        "onset": {"absent_until": candidate.absent_until, "present_from": candidate.present_from,
                  "dated": bool(_parse_day(candidate.absent_until)
                                and _parse_day(candidate.present_from))},
        "statistics": build.stats,
        "files": _file_records(build) + [{"name": "dossier.json",
                                          "description": "This machine-readable record"}],
        "panels_missing": build.missing,
        "provenance": {
            **build.provenance,
            "sources": {"sentinel2_catalogue": config.EARTH_SEARCH,
                        "esri_world_imagery": hires_mod.WORLD_IMAGERY,
                        "esri_wayback": hires_mod.WAYBACK_CAPABILITIES},
            "attribution": [S2_ATTRIBUTION.format(years="(see scene dates)"),
                            hires_mod.ATTRIBUTION],
        },
        "closing_statement": CLOSING_STATEMENT,
    }
    (folder / "dossier.json").write_text(
        json.dumps(_clean(document), indent=2, allow_nan=False), encoding="utf-8")
    return folder


def thumbnail(candidate: Candidate, out_path: Path, size_px: int = 320) -> Path:
    """Write a bare before/after pair for the catalogue page and return its path.

    The PNG is ``size_px`` high: before on the left, after on the right, a
    4 px white gap between them, identical colour stretch, no decorations. A
    candidate without a dated onset gets a single current view. A half whose
    imagery cannot be read is flat grey, so the function never raises on
    data or network failure.
    """
    size = max(int(size_px), 16)
    today = _today()
    comps: dict[str, dict[str, Any] | None] = {}
    try:
        grid = detail_grid(candidate)
        for phase, window in _windows(candidate, today).items():
            try:
                comps[phase] = _composite(grid, window, today)
            except Exception as exc:  # a missing half is drawn grey
                _log.info("thumbnail %s: %s unavailable: %s", candidate.id, phase, exc)
                comps[phase] = None
    except Exception as exc:
        _log.info("thumbnail %s: no imagery: %s", candidate.id, exc)
        comps = {phase: None for phase in _windows(candidate, today)}
    stretch = _stretch(list(comps.values()), ("red", "green", "blue"))
    tiles: list[Image.Image] = []
    for comp in comps.values():
        if comp is None:
            tiles.append(Image.new("RGB", (size, size), (128, 128, 128)))
        else:
            rgb = io.rgb_image(comp["red"], comp["green"], comp["blue"], stretch=stretch)
            tiles.append(Image.fromarray(rgb).resize((size, size), Image.Resampling.LANCZOS))
    gap = 4
    sheet = Image.new("RGB", (size * len(tiles) + gap * (len(tiles) - 1), size), (255, 255, 255))
    for i, tile in enumerate(tiles):
        sheet.paste(tile, (i * (size + gap), 0))
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _save_png(sheet, out_path)
    return out_path
