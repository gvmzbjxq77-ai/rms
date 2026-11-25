"""Geometry of anomalies: blob descriptors, ring and linear-scar finders.

Everything here produces triage measurements and labels only. A "crash" or
"landing_trace" label says what a shape resembles, never what caused it.
"""
from __future__ import annotations

from typing import Any

import numpy as np
from scipy import ndimage
from skimage import feature, measure, transform

_EMPTY: dict[str, Any] = {
    "area_m2": 0.0, "perimeter_m": 0.0, "equivalent_diameter_m": 0.0,
    "major_axis_m": 0.0, "minor_axis_m": 0.0, "elongation": 1.0,
    "orientation_deg": 0.0, "circularity": 0.0, "solidity": 0.0,
    "eccentricity": 0.0, "rectangularity": 0.0, "n_corners": 0,
    "straight_edge_fraction": 0.0, "hole_fraction": 0.0, "regularity": 0.0,
}


def _min_area_rect(points: np.ndarray) -> float:
    """Area of the smallest rotated rectangle enclosing 2-D points."""
    if len(points) < 3:
        return 0.0
    best = np.inf
    edges = np.diff(np.vstack([points, points[:1]]), axis=0)
    angles = np.unique(np.round(np.arctan2(edges[:, 1], edges[:, 0]) % (np.pi / 2), 4))
    for angle in angles:
        c, s = np.cos(-angle), np.sin(-angle)
        rot = points @ np.array([[c, -s], [s, c]]).T
        span = rot.max(axis=0) - rot.min(axis=0)
        best = min(best, float(span[0] * span[1]))
    return best if np.isfinite(best) else 0.0


def describe_blob(mask: np.ndarray, res_m: float) -> dict[str, Any]:
    """Shape descriptors of one blob (largest component of a boolean mask).

    ``regularity`` (0..1) is ``solidity * max(circularity**2,
    rectangularity * straight_edge_fraction)``: high for clean discs and for
    straight-edged rectangles, low for ragged natural outlines.
    ``orientation_deg`` is the major-axis angle, 0 = east, counter-clockwise.
    """
    mask = np.asarray(mask, dtype=bool)
    if mask.ndim != 2 or not mask.any():
        return dict(_EMPTY)
    labels = measure.label(mask, connectivity=2)
    props = max(measure.regionprops(labels), key=lambda p: p.area)
    blob = labels == props.label
    area_px = float(props.area)
    out = dict(_EMPTY)
    out["area_m2"] = area_px * res_m ** 2
    out["equivalent_diameter_m"] = float(2 * np.sqrt(area_px / np.pi) * res_m)
    if area_px < 4:
        out["perimeter_m"] = float(4 * np.sqrt(area_px) * res_m)
        out["major_axis_m"] = out["minor_axis_m"] = out["equivalent_diameter_m"]
        return out
    perimeter_px = max(float(props.perimeter), 1.0)
    major = max(float(props.axis_major_length), 1.0)
    minor = max(float(props.axis_minor_length), 1.0)
    out["perimeter_m"] = perimeter_px * res_m
    out["major_axis_m"] = major * res_m
    out["minor_axis_m"] = minor * res_m
    out["elongation"] = major / minor
    # skimage orientation is measured from the row axis; convert to east-CCW.
    out["orientation_deg"] = float((90.0 + np.degrees(props.orientation)) % 180.0)
    out["circularity"] = float(np.clip(4 * np.pi * area_px / perimeter_px ** 2, 0, 1))
    out["solidity"] = float(np.clip(props.solidity, 0, 1))
    out["eccentricity"] = float(props.eccentricity)
    filled = ndimage.binary_fill_holes(blob)
    out["hole_fraction"] = float((filled.sum() - blob.sum()) / max(filled.sum(), 1))
    padded = np.pad(filled, 1)
    contours = measure.find_contours(padded.astype(float), 0.5)
    if contours:
        contour = max(contours, key=len)
        rect_area = _min_area_rect(contour[::max(1, len(contour) // 200)])
        out["rectangularity"] = float(np.clip(filled.sum() / max(rect_area, 1.0), 0, 1))
        poly = measure.approximate_polygon(contour, tolerance=max(1.0, 0.02 * perimeter_px))
        seg = np.hypot(*np.diff(poly, axis=0).T)
        if seg.size:
            long_edges = seg >= max(4.0, 0.12 * seg.sum())
            out["n_corners"] = int(max(len(poly) - 1, 0))
            out["straight_edge_fraction"] = float(seg[long_edges].sum() / seg.sum())
    out["regularity"] = float(np.clip(out["solidity"] * max(
        out["circularity"] ** 2, out["rectangularity"] * out["straight_edge_fraction"]), 0, 1))
    return out


def _robust_z(image: np.ndarray) -> np.ndarray:
    """Image as robust z-scores (median / MAD), NaN replaced by 0."""
    finite = np.isfinite(image)
    if not finite.any():
        return np.zeros(image.shape, dtype="float32")
    med = np.median(image[finite])
    mad = np.median(np.abs(image[finite] - med)) * 1.4826
    z = (image - med) / max(float(mad), 1e-6)
    z[~finite] = 0
    return z.astype("float32")


def find_rings(image: np.ndarray, res_m: float, min_diameter_m: float,
               max_diameter_m: float, max_results: int = 50) -> list[dict[str, Any]]:
    """Circular or annular features in a single-band image (NaN tolerated).

    Uses a circular Hough transform on Canny edges. Each result has col, row,
    diameter_m, contrast (robust z of the disc interior, or of the rim for a
    hollow ring, against the image), completeness (share of the circumference
    lying on an edge) and polarity. Only circles with completeness >= 0.55 and
    |contrast| >= 2 are returned, which rejects circles "found" in noise.
    """
    image = np.asarray(image, dtype="float32")
    if image.ndim != 2 or min(image.shape) < 8 or not np.isfinite(image).any():
        return []
    z = _robust_z(image)
    edges = feature.canny(z, sigma=1.5)
    if not edges.any():
        return []
    r_min = max(2, int(round(min_diameter_m / (2 * res_m))))
    r_max = max(r_min + 1, int(round(max_diameter_m / (2 * res_m))))
    r_max = min(r_max, min(image.shape) // 2)
    if r_max <= r_min:
        return []
    radii = np.unique(np.linspace(r_min, r_max, min(40, r_max - r_min + 1)).astype(int))
    accum = transform.hough_circle(edges, radii)
    _, cols, rows, found = transform.hough_circle_peaks(
        accum, radii, min_xdistance=r_min, min_ydistance=r_min,
        total_num_peaks=max_results * 3, normalize=True)
    edge_near = ndimage.binary_dilation(edges, iterations=1)
    theta = np.linspace(0, 2 * np.pi, 180, endpoint=False)
    height, width = image.shape
    yy, xx = np.ogrid[:height, :width]
    results: list[dict[str, Any]] = []
    for col, row, radius in zip(cols, rows, found):
        px = np.round(col + radius * np.cos(theta)).astype(int)
        py = np.round(row + radius * np.sin(theta)).astype(int)
        inside = (px >= 0) & (px < width) & (py >= 0) & (py < height)
        if inside.mean() < 0.7:
            continue
        completeness = float(edge_near[py[inside], px[inside]].mean() * inside.mean())
        if completeness < 0.55:
            continue
        dist = np.sqrt((xx - col) ** 2 + (yy - row) ** 2)
        disc = dist <= 0.8 * radius
        band = np.abs(dist - radius) <= max(1.0, 0.15 * radius)
        if not disc.any() or not band.any():
            continue
        # A filled disc differs inside; a pure ring differs only along its rim.
        contrast = max((float(np.median(z[disc])), float(np.median(z[band]))), key=abs)
        if abs(contrast) < 2.0:
            continue
        results.append({"col": float(col), "row": float(row),
                        "diameter_m": float(2 * radius * res_m),
                        "contrast": contrast, "completeness": completeness,
                        "polarity": 1 if contrast >= 0 else -1})
    results.sort(key=lambda r: -r["completeness"] * (1 + abs(r["contrast"])))
    return results[:max_results]


def find_linear_scars(image: np.ndarray, res_m: float, min_length_m: float,
                      max_width_m: float = 200.0, max_results: int = 50) -> list[dict[str, Any]]:
    """Straight, narrow linear features (gouges, tracks) in a single band.

    The image is high-pass filtered at the scale of ``max_width_m``, pixels
    beyond 3 robust sigmas are kept, and straight runs are extracted with a
    probabilistic Hough transform. Each result has endpoints, length_m,
    width_m, straightness (share of the line lying on flagged pixels),
    contrast (median robust z along the line) and polarity.
    """
    image = np.asarray(image, dtype="float32")
    if image.ndim != 2 or min(image.shape) < 8 or not np.isfinite(image).any():
        return []
    filled = np.where(np.isfinite(image), image, np.nanmedian(image))
    window = max(3, int(round(2 * max_width_m / res_m)) | 1)
    z = _robust_z(filled - ndimage.median_filter(filled, size=window))
    min_len_px = max(4, int(round(min_length_m / res_m)))
    results: list[dict[str, Any]] = []
    for polarity in (1, -1):
        binary = (z * polarity) >= 3.0
        if binary.sum() < min_len_px:
            continue
        lines = transform.probabilistic_hough_line(
            binary, threshold=max(5, min_len_px // 2), line_length=min_len_px,
            line_gap=2, rng=0)
        for (c0, r0), (c1, r1) in lines:
            length_px = float(np.hypot(c1 - c0, r1 - r0))
            n = max(int(length_px), 2)
            cc = np.clip(np.round(np.linspace(c0, c1, n)).astype(int), 0, image.shape[1] - 1)
            rr = np.clip(np.round(np.linspace(r0, r1, n)).astype(int), 0, image.shape[0] - 1)
            straightness = float(binary[rr, cc].mean())
            label_img, _ = ndimage.label(binary)
            ids = np.unique(label_img[rr, cc])
            ids = ids[ids > 0]
            area_px = float(np.isin(label_img, ids).sum()) if ids.size else float(n)
            width_m = area_px / max(length_px, 1.0) * res_m
            if width_m > max_width_m:
                continue
            results.append({"col0": float(c0), "row0": float(r0), "col1": float(c1),
                            "row1": float(r1), "length_m": length_px * res_m,
                            "width_m": float(width_m), "straightness": straightness,
                            "contrast": float(np.median(z[rr, cc])), "polarity": polarity})
    results.sort(key=lambda r: -r["length_m"] * r["straightness"])
    return results[:max_results]


def classify_signature(shape: dict[str, Any], spectral: dict[str, Any]) -> str:
    """Triage label from shape and spectral change. Rules, in order:

    - ``thermal``: the detection came from a thermal sensor.
    - ``installation``: rectilinear outline (rectangularity >= 0.7 with
      straight_edge_fraction >= 0.5), or large (> 20 ha) and brighter.
    - ``crash``: elongated (elongation >= 3) scar with vegetation loss, burn
      signal or darkening (d_ndvi <= -0.05, d_nbr <= -0.05 or d_brightness < 0).
    - ``landing_trace``: compact (10 to 300 m across), circular (circularity
      >= 0.6) or ring-shaped (hole_fraction >= 0.15) mark with a vegetation
      or soil change.
    - otherwise ``unknown``.
    These labels only sort candidates for review; they conclude nothing.
    """
    if spectral.get("origin") == "thermal":
        return "thermal"
    area = float(shape.get("area_m2", 0.0))
    diameter = float(shape.get("equivalent_diameter_m", 0.0))
    d_bri = float(spectral.get("d_brightness", 0.0) or 0.0)
    d_ndvi = float(spectral.get("d_ndvi", 0.0) or 0.0)
    d_nbr = float(spectral.get("d_nbr", 0.0) or 0.0)
    rectilinear = (shape.get("rectangularity", 0.0) >= 0.7
                   and shape.get("straight_edge_fraction", 0.0) >= 0.5 and area >= 3600)
    if rectilinear or (area > 2.0e5 and d_bri > 0.02):
        return "installation"
    if shape.get("elongation", 1.0) >= 3.0 and (d_ndvi <= -0.05 or d_nbr <= -0.05 or d_bri < 0):
        return "crash"
    compact = 10.0 <= diameter <= 300.0
    round_or_ring = shape.get("circularity", 0.0) >= 0.6 or shape.get("hole_fraction", 0.0) >= 0.15
    changed = abs(d_ndvi) >= 0.04 or abs(d_bri) >= 0.02 or abs(d_nbr) >= 0.04
    if compact and round_or_ring and changed:
        return "landing_trace"
    return "unknown"
