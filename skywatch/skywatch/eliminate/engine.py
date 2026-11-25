"""Elimination engine: run every check on every candidate, then assign a tier.

Tier ladder, exactly as implemented in ``skywatch.core.models.assign_tier``:

- T0: at least one check has status "explains".
- T1: unexplained, but seen in only one independent sensor family.
- T2: seen in two or more sensor families, but a mandatory check did not run,
  a check is inconclusive, or there is no dated onset window.
- T3: two or more sensors, a dated abrupt onset, every mandatory check ran,
  and none explains it and none is inconclusive.
- T4: T3 plus an independent witness report matched in time and place.

A check that cannot run is recorded as "not_run" with the reason. It is never
skipped silently and never counted as having failed to explain.
"""
from __future__ import annotations

import importlib
import logging
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Sequence

from ..core.models import (MANDATORY_CHECKS, Candidate, CheckResult, Region, assign_tier)

log = logging.getLogger(__name__)

#: (check name, dotted path of ``fn(candidate) -> list[CheckResult]``, category, mandatory)
REGISTRY: list[tuple[str, str, str, bool]] = [
    ("artefact_screen", "skywatch.eliminate.artefacts.check_artefacts", "artefact", True),
    ("landcover", "skywatch.eliminate.landcover.check_landcover", "natural", True),
    ("osm_infrastructure", "skywatch.eliminate.osm.check_osm", "infrastructure", True),
    ("wikidata_nearby", "skywatch.eliminate.wikidata.check_wikidata", "infrastructure", True),
    ("military_or_rocket_range", "skywatch.eliminate.records.check_ranges", "infrastructure", False),
    ("aviation_accident", "skywatch.eliminate.records.check_aviation_accident", "event", False),
    ("meteorite_record", "skywatch.eliminate.records.check_meteorite", "event", False),
    ("fire_history", "skywatch.eliminate.fire.check_fire", "event", True),
    ("natural_process", "skywatch.eliminate.natural.check_natural", "natural", True),
]

assert {name for name, _, _, mandatory in REGISTRY if mandatory} == set(MANDATORY_CHECKS), \
    "REGISTRY mandatory checks must match models.MANDATORY_CHECKS"

Entry = tuple[str, str | Callable[[Candidate], list[CheckResult]], str, bool]


def _resolve(target: str | Callable[..., Any]) -> Callable[..., Any]:
    if callable(target):
        return target
    module_name, _, attr = target.rpartition(".")
    return getattr(importlib.import_module(module_name), attr)


def run_checks(candidate: Candidate, only: Sequence[str] | None = None,
               registry: Sequence[Entry] | None = None) -> Candidate:
    """Run the registered checks on one candidate and set its tier.

    A missing module, an exception or an empty return becomes a "not_run"
    result carrying the error type. Results replace earlier results of the
    same check name. Witness reports are matched afterwards.
    """
    results: dict[str, CheckResult] = {c.check: c for c in candidate.checks}
    for name, target, category, _mandatory in (registry if registry is not None else REGISTRY):
        if only is not None and name not in only:
            continue
        try:
            produced = list(_resolve(target)(candidate) or [])
            if not produced:
                raise ValueError("check returned no result")
        except Exception as exc:
            log.warning("check %s failed for %s: %r", name, candidate.id, exc)
            produced = [CheckResult(check=name, category=category, status="not_run",  # type: ignore[arg-type]
                                    detail=f"{type(exc).__name__}: {str(exc)[:200]}",
                                    source="engine")]
        for result in produced:
            results[result.check] = result
    candidate.checks = list(results.values())
    if only is None:
        try:
            match = importlib.import_module("skywatch.reports.ingest").match_reports
            candidate.reports = list(match(candidate) or [])
        except Exception as exc:
            candidate.reports = []
            candidate.checks = [c for c in candidate.checks if c.check != "report_match"]
            candidate.checks.append(CheckResult(
                check="report_match", category="report", status="not_run",
                detail=f"{type(exc).__name__}: {str(exc)[:200]}", source="engine"))
    candidate.tier, candidate.tier_reason = assign_tier(candidate)
    return candidate


def confirm_sensors(candidate: Candidate) -> Candidate:
    """Ask the Landsat and radar modules whether they independently see the feature."""
    errors: dict[str, str] = {}
    for label, path in (("landsat", "skywatch.detect.landsat.confirm"),
                        ("sar", "skywatch.detect.sar.confirm")):
        try:
            _resolve(path)(candidate)
        except Exception as exc:
            errors[label] = f"{type(exc).__name__}: {str(exc)[:200]}"
    if errors:
        candidate.measurements["confirm_errors"] = errors
    candidate.sensors = sorted(set(candidate.sensors))
    return candidate


def run_all(candidates: Sequence[Candidate], workers: int = 3, confirm: bool = True,
            progress: bool = True) -> list[Candidate]:
    """Confirm sensors and run all checks for many candidates, order preserved."""
    def one(candidate: Candidate) -> Candidate:
        try:
            if confirm:
                confirm_sensors(candidate)
            return run_checks(candidate)
        except Exception as exc:  # last line of defence: keep the batch alive
            candidate.notes += f" engine failure: {type(exc).__name__}"
            candidate.tier, candidate.tier_reason = assign_tier(candidate)
            return candidate

    with ThreadPoolExecutor(max(1, workers)) as pool:
        done = []
        for index, result in enumerate(pool.map(one, candidates), start=1):
            done.append(result)
            if progress:
                print(f"  [{index}/{len(candidates)}] {result.id} -> {result.tier}", flush=True)
    return done


def summarise(candidates: Sequence[Candidate],
              regions: Sequence[Region] | None = None) -> dict[str, Any]:
    """Counts by tier, signature, detector and check status, plus per-region rates."""
    checks: dict[str, Counter[str]] = {}
    not_run: Counter[str] = Counter()
    for candidate in candidates:
        for check in candidate.checks:
            checks.setdefault(check.check, Counter())[check.status] += 1
            if check.status == "not_run":
                not_run[f"{check.check}: {check.detail[:80]}"] += 1
    summary: dict[str, Any] = {
        "n_candidates": len(candidates),
        "tiers": dict(Counter(c.tier or "untiered" for c in candidates)),
        "signatures": dict(Counter(c.signature for c in candidates)),
        "detectors": dict(Counter(c.detector for c in candidates)),
        "checks": {name: dict(counts) for name, counts in sorted(checks.items())},
        "not_run_reasons": not_run.most_common(15),
        "explained_by": dict(Counter(
            check.check for c in candidates for check in c.checks if check.status == "explains")),
    }
    if regions is not None:
        per_region: dict[str, Any] = {}
        for region in regions:
            mine = [c for c in candidates if c.region_id == region.id]
            entry: dict[str, Any] = {"kind": region.kind, "n": len(mine),
                                     "tiers": dict(Counter(c.tier or "untiered" for c in mine))}
            if mine:
                entry["explained_share"] = sum(c.tier == "T0" for c in mine) / len(mine)
            per_region[region.id] = entry
        summary["regions"] = per_region
    return summary
