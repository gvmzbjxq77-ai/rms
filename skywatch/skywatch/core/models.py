"""Shared data model: regions, candidates, elimination checks, evidence tiers.

Every detector emits ``Candidate`` objects, every elimination check returns a
``CheckResult``, and the tier is derived only from recorded evidence. Nothing
in this model asserts an origin: the highest tier means "unexplained after
every check", never "identified".
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal

BBox = tuple[float, float, float, float]  # west, south, east, north (WGS84 degrees)

RegionKind = Literal["blind", "control", "seeded"]
Signature = Literal["crash", "landing_trace", "installation", "thermal", "unknown"]
CheckCategory = Literal["infrastructure", "natural", "event", "artefact", "report"]
CheckStatus = Literal["explains", "does_not_explain", "inconclusive", "not_run"]
Tier = Literal["T0", "T1", "T2", "T3", "T4"]

#: Independent sensor families. Two bands of one instrument are ONE sensor.
SENSORS = ("optical_s2", "optical_landsat", "thermal_landsat", "thermal_aster",
           "radar_s1", "nightlights_viirs", "terrain_dem", "optical_vhr")


@dataclass
class Region:
    """An area to search. ``kind`` decides how its results are interpreted."""

    id: str
    name: str
    bbox: BBox
    kind: RegionKind
    biome: str = ""
    notes: str = ""
    #: Yearly date window (MM-DD, MM-DD) with the clearest, snow-free, most
    #: comparable imagery; a window may wrap the new year (e.g. 12-01 to 02-28).
    season: tuple[str, str] = ("06-01", "08-31")
    #: Control regions: what a correct pipeline should find (and explain) here.
    expected: str = ""
    #: Machine-checkable form of ``expected`` (see skywatch.sweep.regions).
    expect: dict[str, Any] = field(default_factory=dict)
    #: Seeded regions: the report that motivated it (source, date, summary).
    seed: dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckResult:
    """Outcome of one conventional-explanation test for one candidate.

    ``explains`` means the check found a sufficient mundane cause.
    ``not_run`` must be used whenever the data source failed or does not
    cover the location; a check that could not run never counts as passed.
    """

    check: str
    category: CheckCategory
    status: CheckStatus
    detail: str = ""
    source: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class Candidate:
    """A surface anomaly found by a detector, with everything known about it."""

    id: str
    region_id: str
    lat: float
    lon: float
    bbox: BBox
    signature: Signature
    detector: str
    #: Detector-native strength in 0..1 (not a probability of anything exotic).
    score: float
    area_m2: float = 0.0
    #: ISO dates bracketing the appearance: last scene without the feature and
    #: first scene with it. Both None when the feature has no known onset.
    absent_until: str | None = None
    present_from: str | None = None
    #: Sensor families (see SENSORS) in which the feature is independently seen.
    sensors: list[str] = field(default_factory=list)
    shape: dict[str, Any] = field(default_factory=dict)
    measurements: dict[str, Any] = field(default_factory=dict)
    checks: list[CheckResult] = field(default_factory=list)
    tier: Tier | None = None
    tier_reason: str = ""
    #: Witness reports matched in space and time (for T4).
    reports: list[dict[str, Any]] = field(default_factory=list)
    notes: str = ""

    def to_json(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> "Candidate":
        data = dict(raw)
        data["checks"] = [CheckResult(**c) for c in data.get("checks", [])]
        data["bbox"] = tuple(data["bbox"])
        return cls(**data)


#: Checks that must have actually run before a candidate may reach T3.
MANDATORY_CHECKS = ("osm_infrastructure", "landcover", "wikidata_nearby",
                    "fire_history", "artefact_screen", "natural_process")


def assign_tier(candidate: Candidate) -> tuple[Tier, str]:
    """Derive the evidence tier from recorded checks, sensors and reports.

    The ladder is cumulative: T2 needs two independent sensors, T3 also needs
    a dated abrupt onset with every mandatory check run and none explaining,
    T4 also needs an independent report matched in time and place.
    """
    explaining = [c for c in candidate.checks if c.status == "explains"]
    if explaining:
        return "T0", "explained by: " + ", ".join(sorted({c.check for c in explaining}))
    sensors = sorted(set(candidate.sensors))
    if len(sensors) < 2:
        return "T1", f"seen in one sensor only ({', '.join(sensors) or 'none'})"
    ran = {c.check for c in candidate.checks if c.status in ("does_not_explain", "inconclusive")}
    missing = [name for name in MANDATORY_CHECKS if name not in ran]
    dated = bool(candidate.absent_until and candidate.present_from)
    inconclusive = [c.check for c in candidate.checks if c.status == "inconclusive"]
    if missing or not dated or inconclusive:
        why = []
        if missing:
            why.append("checks not run: " + ", ".join(missing))
        if not dated:
            why.append("no dated onset window")
        if inconclusive:
            why.append("inconclusive: " + ", ".join(sorted(set(inconclusive))))
        return "T2", f"confirmed in {len(sensors)} sensors; " + "; ".join(why)
    if candidate.reports:
        return "T4", "abrupt dated onset, all checks failed to explain, independent report matched"
    return "T3", "abrupt dated onset and every mandatory check failed to explain it"


def save_candidates(path: Path, candidates: Iterable[Candidate]) -> None:
    """Write candidates as JSON lines, replacing the file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        for candidate in candidates:
            handle.write(json.dumps(candidate.to_json(), default=str) + "\n")


def load_candidates(path: Path) -> list[Candidate]:
    """Read candidates written by ``save_candidates``; missing file is empty."""
    if not path.exists():
        return []
    with path.open() as handle:
        return [Candidate.from_json(json.loads(line)) for line in handle if line.strip()]
