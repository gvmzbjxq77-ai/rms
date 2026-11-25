"""Elimination engine: run every check on every candidate, then assign a tier.

Tier ladder, exactly as implemented in ``skywatch.core.models.assign_tier``:

- T0: at least one check has status "explains".
- T1: unexplained, but seen in only one independent sensor family.
- T2: seen in two or more sensor families, but a mandatory check did not run,
  a check is inconclusive, or there is no dated onset window.
- T3: two or more sensors, a dated abrupt onset, every mandatory check ran,
  and none explains it and none is inconclusive.
- T4: T3 plus an independent witness report matched in time and place, where
  fewer than 0.1 such matches would be expected by chance from the local
  reporting rate.

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
    # Ordered cheapest first, so an early explanation saves the slow reads.
    ("military_or_rocket_range", "skywatch.eliminate.records.check_ranges", "infrastructure", False),
    ("landcover", "skywatch.eliminate.landcover.check_landcover", "natural", True),
    ("osm_infrastructure", "skywatch.eliminate.osm.check_osm", "infrastructure", True),
    ("wikidata_nearby", "skywatch.eliminate.wikidata.check_wikidata", "infrastructure", True),
    ("human_context", "skywatch.eliminate.context.check_context", "infrastructure", False),
    ("aviation_accident", "skywatch.eliminate.records.check_aviation_accident", "event", False),
    ("meteorite_record", "skywatch.eliminate.records.check_meteorite", "event", False),
    ("natural_process", "skywatch.eliminate.natural.check_natural", "natural", True),
    ("artefact_screen", "skywatch.eliminate.artefacts.check_artefacts", "artefact", True),
    ("fire_history", "skywatch.eliminate.fire.check_fire", "event", True),
]

assert {name for name, _, _, mandatory in REGISTRY if mandatory} == set(MANDATORY_CHECKS), \
    "REGISTRY mandatory checks must match models.MANDATORY_CHECKS"

Entry = tuple[str, str | Callable[[Candidate], list[CheckResult]], str, bool]

#: Witness reports count towards T4 only when the number of matches expected
#: by chance from the local reporting rate is at most this.
REPORT_CHANCE_LIMIT = 0.1


def _resolve(target: str | Callable[..., Any]) -> Callable[..., Any]:
    if callable(target):
        return target
    module_name, _, attr = target.rpartition(".")
    return getattr(importlib.import_module(module_name), attr)


def run_checks(candidate: Candidate, only: Sequence[str] | None = None,
               registry: Sequence[Entry] | None = None,
               stop_when_explained: bool = False) -> Candidate:
    """Run the registered checks on one candidate and set its tier.

    A missing module, an exception or an empty return becomes a "not_run"
    result carrying the error type. Results replace earlier results of the
    same check name. Witness reports are matched afterwards. With
    ``stop_when_explained`` the remaining checks are recorded as "not_run"
    (reason: already explained) once one check explains the candidate.
    """
    results: dict[str, CheckResult] = {c.check: c for c in candidate.checks}
    explained_by: str | None = None
    for name, target, category, _mandatory in (registry if registry is not None else REGISTRY):
        if only is not None and name not in only:
            continue
        if stop_when_explained and explained_by:
            results[name] = CheckResult(check=name, category=category, status="not_run",  # type: ignore[arg-type]
                                        detail=f"skipped: already explained by {explained_by}",
                                        source="engine")
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
            if result.status == "explains" and explained_by is None:
                explained_by = result.check
        # Kept current so later checks can read earlier results.
        candidate.checks = list(results.values())
    candidate.checks = list(results.values())
    if only is None:
        candidate.reports = []
        candidate.checks = [c for c in candidate.checks if c.check not in ("report_match", "witness_reports")]
        try:
            report = importlib.import_module("skywatch.reports.ingest").report_check(candidate)
            candidate.checks.append(report)
            matches = list(report.evidence.get("matches") or [])
            chance = float(report.evidence.get("expected_by_chance", 1.0))
            # A report only counts towards T4 when a coincidence is unlikely.
            if matches and chance <= REPORT_CHANCE_LIMIT:
                candidate.reports = matches
        except Exception as exc:
            candidate.checks.append(CheckResult(
                check="witness_reports", category="report", status="not_run",
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
            progress: bool = True, stop_when_explained: bool = True) -> list[Candidate]:
    """Run all checks for many candidates, then confirm the unexplained ones.

    Sensor confirmation (slow) is only attempted for candidates that no check
    explains; the tier is re-derived afterwards. Output order matches input.
    """
    def one(candidate: Candidate) -> Candidate:
        try:
            run_checks(candidate, stop_when_explained=stop_when_explained)
            if confirm and candidate.tier != "T0":
                confirm_sensors(candidate)
                candidate.tier, candidate.tier_reason = assign_tier(candidate)
            return candidate
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
