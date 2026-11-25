"""Country lookup, request drafts, ground-truth plan, manifests and terrain maths."""
import json

import numpy as np

from skywatch.core.models import Candidate, CheckResult
from skywatch.foia import draft
from skywatch.provenance import ots


def _candidate(lat: float, lon: float) -> Candidate:
    return Candidate(id="SW-T-0001", region_id="T", lat=lat, lon=lon,
                     bbox=(lon - 0.01, lat - 0.01, lon + 0.01, lat + 0.01), signature="unknown",
                     detector="optical_change", score=0.5, area_m2=12000.0,
                     absent_until="2022-03-01", present_from="2022-04-10",
                     checks=[CheckResult("osm_infrastructure", "infrastructure", "does_not_explain",
                                         evidence={"nearest_road_m": 4200.0}),
                             CheckResult("fire_history", "event", "inconclusive", detail="small fire possible")])


def test_country_lookup_and_ocean():
    assert draft.country_of(37.2, -116.0)["iso"] == "US"
    assert draft.country_of(-24.5, -69.5)["iso"] == "CL"
    assert draft.country_of(0.0, -30.0)["iso"] == ""


def test_us_drafts_are_specific_and_neutral():
    drafts = draft.draft_request(_candidate(37.2, -116.0))
    assert len(drafts) == 4 and "Federal Aviation Administration" in drafts[0]["agency"]
    body = drafts[0]["body_markdown"]
    assert "37.20000" in body and "2022-03-01" in body and "2022-04-10" in body
    assert "5 U.S.C." in body and "NEXRAD" in body
    lowered = " ".join(d["body_markdown"].lower() for d in drafts)
    assert all(word not in lowered for word in ("alien", "ufo", "extraterrestrial", "non-human"))


def test_unlisted_country_invents_no_law():
    drafts = draft.draft_request(_candidate(18.5, 11.5))      # Niger
    assert len(drafts) == 1 and drafts[0]["law"] == "none listed"


def test_ground_truth_plan_and_files(tmp_path):
    cand = _candidate(-24.5, -69.5)
    plan = draft.ground_truth_plan(cand)
    assert "4.2 km" in plan and "fire_history: inconclusive" in plan and "control samples" in plan
    written = draft.write_followups(cand, tmp_path)
    assert {p.name for p in written} == {"foia_1.md", "foia_2.md", "ground_truth_plan.md"}
    assert "Nothing has been sent" in (tmp_path / "foia_1.md").read_text()


def test_manifest_detects_any_edit(tmp_path):
    (tmp_path / "a.txt").write_text("one")
    (tmp_path / "b.json").write_text(json.dumps({"x": 1}))
    path = ots.write_manifest(tmp_path)
    first = json.loads(path.read_text())
    assert first["manifest_sha256"] and len(first["files"]) == 2
    (tmp_path / "a.txt").write_text("two")
    second = json.loads(ots.write_manifest(tmp_path).read_text())
    assert second["manifest_sha256"] != first["manifest_sha256"]


def test_terrain_slope_on_a_synthetic_ramp(monkeypatch):
    from skywatch.core import io
    from skywatch.detect import terrain

    grid = io.make_grid((10.0, 20.0, 10.02, 20.02), 30.0)
    ramp = np.tile(np.arange(grid.width, dtype="float32") * 30.0, (grid.height, 1))   # 45 degree slope
    monkeypatch.setattr(terrain, "dem", lambda g: ramp)
    slope, _aspect = terrain.slope_aspect(grid)
    assert abs(float(np.nanmedian(slope)) - 45.0) < 1.5
