"""Prepare review briefs for the least explained candidates and record verdicts.

A brief is everything a sceptical reviewer needs: the measurements, every
check with its status and detail, the sensor confirmations and the dossier
images. The reviewer's verdict is stored beside the dossier as
``output/adjudication/<id>.json`` and shown on the results page.

Verdict vocabulary (``verdict`` field):
- ``explained``: the reviewer found a sufficient ordinary cause (say which).
- ``probably_ordinary``: an ordinary cause is likely but not demonstrated.
- ``unexplained``: nothing available explains it; ground truth is needed.
- ``artefact``: the detection is a data or processing artefact.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..core import config
from ..core.models import Candidate
from ..publish.export import TIER_ORDER, load_final
from ..sweep.run import all_regions

ADJUDICATION_DIR = config.OUTPUT / "adjudication"
DOSSIERS = config.OUTPUT / "dossiers"
VERDICT_LABELS = {"explained": "explained", "probably_ordinary": "probably ordinary",
                  "unexplained": "unexplained, ground truth needed", "artefact": "data artefact"}


def brief(candidate: Candidate) -> dict[str, Any]:
    """Everything about one candidate, in plain JSON, for a reviewer."""
    m = candidate.measurements
    folder = DOSSIERS / candidate.id
    images = sorted(p.name for p in folder.glob("*.png")) if folder.exists() else []
    series = m.get("series") or {}
    return {
        "id": candidate.id, "region": candidate.region_id, "lat": candidate.lat, "lon": candidate.lon,
        "tier": candidate.tier, "tier_reason": candidate.tier_reason, "signature": candidate.signature,
        "detector": candidate.detector, "kind": m.get("kind"), "break_year": m.get("break_year"),
        "absent_until": candidate.absent_until, "present_from": candidate.present_from,
        "onset_window_days": m.get("onset_window_days"), "onset_note": m.get("onset_note"),
        "area_m2": candidate.area_m2, "sensors": candidate.sensors,
        "change": {k: m.get(k) for k in ("d_brightness", "d_ndvi", "d_nbr", "d_swir",
                                          "recovery_fraction", "persistence_years", "step_snr", "crowding")},
        "shape": candidate.shape,
        "series_summary": {"n_scenes": len(series.get("dates", [])),
                           "feature": m.get("series_feature"), "shift": m.get("series_shift"),
                           "noise": m.get("series_noise"), "flips": m.get("onset_flips")},
        "landsat": {k: v for k, v in (m.get("landsat") or {}).items() if k != "before" and k != "after"},
        "sar": {k: v for k, v in (m.get("sar") or {}).items() if k != "before" and k != "after"},
        "checks": [{"check": c.check, "status": c.status, "detail": c.detail,
                    "evidence": _trim(c.evidence)} for c in candidate.checks],
        "reports": candidate.reports,
        "dossier_folder": str(folder), "images": images,
        "google_maps": f"https://www.google.com/maps/@{candidate.lat},{candidate.lon},800m/data=!3m1!1e3",
    }


def _trim(evidence: dict[str, Any], limit: int = 1500) -> Any:
    text = json.dumps(evidence, default=str)
    return evidence if len(text) <= limit else text[:limit] + "..."


def candidates_for_review(limit: int = 30, per_region: int = 3) -> list[Candidate]:
    """The least explained candidates, spread across regions."""
    chosen: list[Candidate] = []
    for region in all_regions():
        mine = [c for c in load_final(region.id)[0] if c.tier and c.tier != "T0"]
        mine.sort(key=lambda c: (TIER_ORDER.get(c.tier, 5), c.measurements.get("crowding", 0.0), -c.score))
        chosen.extend(mine[:per_region])
    chosen.sort(key=lambda c: (TIER_ORDER.get(c.tier, 5), c.measurements.get("crowding", 0.0), -c.score))
    return chosen[:limit]


def write_briefs(limit: int = 30, per_region: int = 3) -> list[Path]:
    """Write ``output/adjudication/briefs/<id>.json`` for the review set."""
    folder = ADJUDICATION_DIR / "briefs"
    folder.mkdir(parents=True, exist_ok=True)
    written = []
    for candidate in candidates_for_review(limit, per_region):
        path = folder / f"{candidate.id}.json"
        path.write_text(json.dumps(brief(candidate), indent=1, default=str))
        written.append(path)
    return written


def record_verdict(candidate_id: str, verdict: str, one_line: str, summary: str,
                   explanation: str = "", next_step: str = "", reviewers: int = 0,
                   votes: dict[str, int] | None = None) -> Path:
    """Store a panel verdict for the results page."""
    if verdict not in VERDICT_LABELS:
        raise ValueError(f"unknown verdict {verdict!r}")
    ADJUDICATION_DIR.mkdir(parents=True, exist_ok=True)
    path = ADJUDICATION_DIR / f"{candidate_id}.json"
    path.write_text(json.dumps({
        "verdict": verdict, "verdict_label": VERDICT_LABELS[verdict], "one_line": one_line,
        "summary": summary, "explanation": explanation, "next_step": next_step,
        "reviewers": reviewers, "votes": votes or {}}, indent=1))
    return path


if __name__ == "__main__":
    paths = write_briefs()
    print(f"{len(paths)} briefs written to {ADJUDICATION_DIR / 'briefs'}")
