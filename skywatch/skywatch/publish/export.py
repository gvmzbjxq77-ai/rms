"""Collect sweep results into one catalogue file for the results page.

The catalogue states what was searched, what was found, what explained each
candidate, what could not be checked, and how the control regions fared.
Null results and failures are exported alongside the finds.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..core import config
from ..core.models import Candidate, load_candidates
from ..eliminate.engine import summarise
from ..sweep import regions as region_defs
from ..sweep.run import CAND_DIR, REGION_DIR, all_regions

SITE = config.OUTPUT / "site"
ADJUDICATION_DIR = config.OUTPUT / "adjudication"
TIER_ORDER = {"T4": 0, "T3": 1, "T2": 2, "T1": 3, "T0": 4, None: 5}


def load_final(region_id: str) -> tuple[list[Candidate], str]:
    """Candidates of a region at the furthest stage reached, and that stage's name."""
    for stage in ("final", "refined", "raw"):
        path = CAND_DIR / stage / f"{region_id}.jsonl"
        if path.exists():
            return load_candidates(path), stage
    return [], "none"


def _compact(candidate: Candidate) -> dict[str, Any]:
    m, shape = candidate.measurements, candidate.shape or {}
    record: dict[str, Any] = {
        "id": candidate.id, "region": candidate.region_id,
        "lat": round(candidate.lat, 5), "lon": round(candidate.lon, 5),
        "tier": candidate.tier, "tier_reason": candidate.tier_reason,
        "signature": candidate.signature, "detector": candidate.detector,
        "kind": m.get("kind"), "break_year": m.get("break_year"),
        "absent_until": candidate.absent_until, "present_from": candidate.present_from,
        "onset_window_days": m.get("onset_window_days"), "onset_note": m.get("onset_note"),
        "area_m2": round(candidate.area_m2), "score": round(candidate.score, 3),
        "snr": round(float(m.get("step_snr", m.get("median_z", m.get("z", 0.0))) or 0.0), 1),
        "sensors": candidate.sensors,
        "change": {k: round(float(m[k]), 3) for k in ("d_brightness", "d_ndvi", "d_nbr", "d_swir")
                   if isinstance(m.get(k), (int, float))},
        "thermal_K": m.get("median_anomaly_K"),
        "shape": {k: round(float(shape[k]), 2) for k in
                  ("equivalent_diameter_m", "elongation", "circularity", "rectangularity", "regularity")
                  if isinstance(shape.get(k), (int, float))},
        "checks": [{"check": c.check, "category": c.category, "status": c.status,
                    "detail": c.detail[:400], "source": c.source[:120]} for c in candidate.checks],
        "reports": candidate.reports[:5],
        "confirm": {
            "landsat": {k: v for k, v in (m.get("landsat") or {}).items() if k in ("status", "reason", "optical", "thermal")},
            "sar": {k: v for k, v in (m.get("sar") or {}).items()
                    if k in ("status", "reason", "shift_db", "noise_db", "confirmed", "relative_orbit")},
        },
    }
    verdict = ADJUDICATION_DIR / f"{candidate.id}.json"
    if verdict.exists():
        record["adjudication"] = json.loads(verdict.read_text())
    return record


def build_catalogue(site: Path = SITE) -> dict[str, Any]:
    """Write ``catalogue.json`` under ``site`` and return its content."""
    regions = all_regions()
    region_rows: list[dict[str, Any]] = []
    everything: list[Candidate] = []
    for region in regions:
        summary_file = REGION_DIR / f"{region.id}.json"
        summary = json.loads(summary_file.read_text()) if summary_file.exists() else {"status": "not_run"}
        candidates, stage = load_final(region.id)
        tiered = [c for c in candidates if c.tier]
        everything.extend(tiered)
        west, south, east, north = region.bbox
        row: dict[str, Any] = {
            "id": region.id, "name": region.name, "kind": region.kind, "biome": region.biome,
            "lat": round((south + north) / 2, 3), "lon": round((west + east) / 2, 3),
            "bbox": [round(v, 4) for v in region.bbox], "area_km2": round(region_defs.area_km2(region)),
            "season": list(region.season), "status": summary.get("status"),
            "years": summary.get("years", []), "blobs_detected": summary.get("n_blobs_total", 0),
            "event_candidates": summary.get("n_event_candidates"),
            "stage": stage, "reviewed": len(tiered),
            "tiers": {t: sum(c.tier == t for c in tiered) for t in ("T0", "T1", "T2", "T3", "T4")},
            "expected": region.expected, "seed": region.seed, "notes": region.notes,
            "error": summary.get("error"),
        }
        if region.kind == "control":
            row["expectation"] = region_defs.evaluate_expectation(region, tiered or candidates)
        region_rows.append(row)
    blind = [r for r in regions if r.kind == "blind"]
    done_blind = [r for r in region_rows if r["kind"] == "blind" and r["status"] == "ok"]
    everything.sort(key=lambda c: (TIER_ORDER.get(c.tier, 5), -c.score))
    catalogue = {
        "coverage": {
            **region_defs.coverage(blind),
            "blind_regions_completed": len(done_blind),
            "blind_area_completed_km2": sum(r["area_km2"] for r in done_blind),
            "blobs_detected_blind": sum(r["blobs_detected"] or 0 for r in done_blind),
        },
        "summary": summarise(everything, regions),
        "regions": region_rows,
        "candidates": [_compact(c) for c in everything],
    }
    site.mkdir(parents=True, exist_ok=True)
    (site / "catalogue.json").write_text(json.dumps(catalogue, default=str))
    return catalogue


if __name__ == "__main__":
    result = build_catalogue()
    print(json.dumps({"coverage": result["coverage"], "tiers": result["summary"]["tiers"],
                      "candidates": len(result["candidates"])}, indent=1))
