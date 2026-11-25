"""Follow-up for reviewed candidates: dossiers, timestamps, request drafts.

    python -m skywatch.sweep.followup [--limit 40] [--per-region 3]

Dossiers are built for the least explained candidates and for one explained
example per control region (so the published catalogue shows what an
ordinary explanation looks like). Every dossier folder is hashed and
timestamped. Request drafts and a ground-truth plan are written for
candidates at tier T2 and above. Nothing is sent anywhere except SHA-256
digests to the OpenTimestamps calendars.
"""
from __future__ import annotations

import argparse
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Sequence

from ..core import config
from ..core.models import Candidate
from ..publish.export import TIER_ORDER, load_final
from .run import all_regions

log = logging.getLogger("skywatch.followup")
DOSSIERS = config.OUTPUT / "dossiers"


def select(limit: int = 40, per_region: int = 3) -> list[Candidate]:
    """The least explained candidates overall, at most ``per_region`` from any
    one region, followed by one explained example from each control region."""
    chosen: list[Candidate] = []
    examples: list[Candidate] = []
    for region in all_regions():
        candidates = [c for c in load_final(region.id)[0] if c.tier]
        unexplained = sorted((c for c in candidates if c.tier != "T0"),
                             key=lambda c: (TIER_ORDER.get(c.tier, 5),
                                            c.measurements.get("crowding", 0.0), -c.score))
        chosen.extend(unexplained[:per_region])
        if region.kind == "control":
            target = (region.expect or {}).get("target")
            explained = [c for c in candidates if c.tier == "T0"]
            if target and explained:
                explained.sort(key=lambda c: (c.lat - target["lat"]) ** 2 + (c.lon - target["lon"]) ** 2)
            examples.extend(explained[:1])
    chosen.sort(key=lambda c: (TIER_ORDER.get(c.tier, 5), c.measurements.get("crowding", 0.0), -c.score))
    return chosen[:limit] + examples


def follow_up(candidate: Candidate, hires: bool = True, stamp: bool = True,
              force: bool = False) -> dict[str, Any]:
    """Build one candidate's dossier, drafts and timestamp; report what was done."""
    from ..dossier import build
    from ..foia import draft
    from ..provenance import ots

    folder = DOSSIERS / candidate.id
    report: dict[str, Any] = {"id": candidate.id, "tier": candidate.tier, "folder": str(folder)}
    if (folder / "dossier.json").exists() and not force:
        report["dossier"] = "kept"
    else:
        try:
            built = build.build_dossier(candidate, DOSSIERS, hires=hires)
            if built != folder:
                report["folder"] = str(built)
                folder = built
            report["dossier"] = "built"
        except Exception as exc:
            report["dossier"] = f"failed: {type(exc).__name__}: {str(exc)[:160]}"
            return report
    try:
        build.thumbnail(candidate, folder / "thumb.png")
    except Exception as exc:
        report["thumbnail"] = f"failed: {type(exc).__name__}"
    if candidate.tier in ("T2", "T3", "T4"):
        try:
            report["drafts"] = [p.name for p in draft.write_followups(candidate, folder)]
        except Exception as exc:
            report["drafts"] = f"failed: {type(exc).__name__}: {str(exc)[:160]}"
    if stamp:
        try:
            result = ots.stamp_directory(folder)
            report["timestamp"] = {k: result.get(k) for k in ("status", "manifest_sha256", "requested_utc")}
        except Exception as exc:
            report["timestamp"] = f"failed: {type(exc).__name__}: {str(exc)[:160]}"
    return report


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--per-region", type=int, default=3)
    parser.add_argument("--no-hires", action="store_true")
    parser.add_argument("--no-stamp", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.WARNING)
    chosen = select(args.limit, args.per_region)
    print(f"follow-up for {len(chosen)} candidates", flush=True)
    reports: list[dict[str, Any]] = []
    with ThreadPoolExecutor(args.workers) as pool:
        for report in pool.map(lambda c: follow_up(c, not args.no_hires, not args.no_stamp, args.force), chosen):
            reports.append(report)
            print(json.dumps(report), flush=True)
    path = config.OUTPUT / "followups.json"
    path.write_text(json.dumps(reports, indent=1))


if __name__ == "__main__":
    main()
