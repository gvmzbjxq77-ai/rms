"""Region-wide recurrence of a change signature.

A change that recurs at several unrelated places in one region, in the same
year, with the same spectral direction and a similar size, is driven by
something that acts on the whole region (rain, greening, blown sand, soil
moisture, or the sensor itself), not by a local event. ``annotate_siblings``
counts that recurrence over every yearly candidate the detector found in a
region and records it on each candidate; the natural-process sub-test
``regional_pattern`` reads it. Event-window and thermal candidates are not
compared: their regions are dated by construction, so sharing a year means
nothing there.
"""
from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from ..core.models import Candidate

SPECTRAL = ("d_brightness", "d_ndvi", "d_nbr", "d_swir")
YEARLY_KINDS = frozenset({"step", "transient", "latest_year"})
#: Two change vectors are the same signature when their cosine is at least
#: this and the larger is at most ``MAGNITUDE_RATIO`` times the smaller.
MIN_COSINE = 0.9
MAGNITUDE_RATIO = 2.0
#: Others needed before the pattern counts as regional / as suggestive.
EXPLAIN_SIBLINGS = 4
SUGGEST_SIBLINGS = 2


def eligible(candidate: Candidate) -> bool:
    """Yearly optical candidates with a non-zero spectral change vector."""
    return (candidate.detector == "optical_change"
            and candidate.measurements.get("kind") in YEARLY_KINDS
            and float(np.linalg.norm(vector(candidate))) > 0.0)


def vector(candidate: Candidate) -> np.ndarray:
    return np.array([float(candidate.measurements.get(k, 0.0) or 0.0) for k in SPECTRAL])


def _distance_km(a: Candidate, b: Candidate) -> float:
    lat = np.radians((a.lat + b.lat) / 2.0)
    dx = np.radians(a.lon - b.lon) * np.cos(lat) * 6371.0
    dy = np.radians(a.lat - b.lat) * 6371.0
    return float(np.hypot(dx, dy))


def annotate_siblings(candidates: Sequence[Candidate]) -> dict[str, dict[str, Any]]:
    """Record on each eligible candidate the others sharing its signature and year.

    Sets ``measurements["regional_siblings"]`` to a census with the count,
    the ids of up to eight siblings, how many candidates were compared, the
    year and the spread (km) of the matching set, and returns the census by
    candidate id. Pass every yearly candidate of the region, not only the ones
    kept for review: the census is only as good as the sample it sees.
    """
    pool = [c for c in candidates if eligible(c)]
    vectors = {c.id: vector(c) for c in pool}
    norms = {k: float(np.linalg.norm(v)) for k, v in vectors.items()}
    census: dict[str, dict[str, Any]] = {}
    for c in pool:
        v, nv, year = vectors[c.id], norms[c.id], c.measurements.get("break_year")
        siblings: list[tuple[str, float, float]] = []
        for other in pool:
            if other is c or other.measurements.get("break_year") != year:
                continue
            w, nw = vectors[other.id], norms[other.id]
            cosine = float(v @ w / (nv * nw))
            ratio = max(nv, nw) / max(min(nv, nw), 1e-9)
            if cosine >= MIN_COSINE and ratio <= MAGNITUDE_RATIO:
                siblings.append((other.id, round(cosine, 3), round(_distance_km(c, other), 1)))
        siblings.sort(key=lambda s: -s[1])
        info = {
            "count": len(siblings), "compared": len(pool) - 1, "year": year,
            "ids": [s[0] for s in siblings[:8]],
            "spread_km": round(max((s[2] for s in siblings), default=0.0), 1),
            "min_cosine": MIN_COSINE, "magnitude_ratio": MAGNITUDE_RATIO,
        }
        c.measurements["regional_siblings"] = info
        census[c.id] = info
    return census


def copy_census(source: Sequence[Candidate], targets: Sequence[Candidate]) -> int:
    """Copy ``regional_siblings`` from ``source`` to same-id ``targets``; count copied."""
    by_id = {c.id: c.measurements.get("regional_siblings") for c in source}
    copied = 0
    for target in targets:
        info = by_id.get(target.id)
        if info is not None:
            target.measurements["regional_siblings"] = info
            copied += 1
    return copied
