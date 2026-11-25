"""Tier logic, the engine's failure handling, and the artefact / natural checks."""
from skywatch.core.models import MANDATORY_CHECKS, Candidate, CheckResult
from skywatch.eliminate import artefacts, engine, natural


def _candidate(**kwargs) -> Candidate:
    base = dict(id="SW-T-0001", region_id="T", lat=20.0, lon=10.0, bbox=(9.99, 19.99, 10.01, 20.01),
                signature="unknown", detector="optical_change", score=0.5, area_m2=40000.0,
                absent_until="2021-07-01", present_from="2021-09-01",
                sensors=["optical_s2", "radar_s1"])
    base.update(kwargs)
    return Candidate(**base)


def _stub(name: str, status: str):
    return (name, lambda c: [CheckResult(check=name, category="natural", status=status)], "natural", True)


def _clean_registry():
    return [_stub(name, "does_not_explain") for name in MANDATORY_CHECKS]


def test_tiers_follow_the_ladder():
    c = engine.run_checks(_candidate(), only=list(MANDATORY_CHECKS), registry=_clean_registry())
    assert c.tier == "T3"
    one_sensor = engine.run_checks(_candidate(sensors=["optical_s2"]),
                                   only=list(MANDATORY_CHECKS), registry=_clean_registry())
    assert one_sensor.tier == "T1"
    undated = engine.run_checks(_candidate(absent_until=None, present_from=None),
                                only=list(MANDATORY_CHECKS), registry=_clean_registry())
    assert undated.tier == "T2"
    reg = _clean_registry()
    reg[0] = _stub(MANDATORY_CHECKS[0], "explains")
    assert engine.run_checks(_candidate(), only=list(MANDATORY_CHECKS), registry=reg).tier == "T0"
    reg[0] = _stub(MANDATORY_CHECKS[0], "inconclusive")
    assert engine.run_checks(_candidate(), only=list(MANDATORY_CHECKS), registry=reg).tier == "T2"
    with_report = _candidate(reports=[{"id": "r1"}])
    assert engine.run_checks(with_report, only=list(MANDATORY_CHECKS),
                             registry=_clean_registry()).tier == "T4"


def test_failures_become_not_run_and_block_t3():
    def boom(_c):
        raise RuntimeError("source down")

    reg = _clean_registry()
    reg[1] = (MANDATORY_CHECKS[1], boom, "natural", True)
    reg[2] = (MANDATORY_CHECKS[2], "skywatch.no_such_module.check", "natural", True)
    reg[3] = (MANDATORY_CHECKS[3], lambda c: [], "natural", True)
    c = engine.run_checks(_candidate(), only=list(MANDATORY_CHECKS), registry=reg)
    status = {k.check: k.status for k in c.checks}
    assert [status[MANDATORY_CHECKS[i]] for i in (1, 2, 3)] == ["not_run"] * 3
    assert c.tier == "T2" and "checks not run" in c.tier_reason
    summary = engine.summarise([c])
    assert summary["tiers"] == {"T2": 1} and summary["not_run_reasons"]


def test_sub_results_are_kept_and_replaced():
    def multi(_c):
        return [CheckResult("natural_process", "natural", "does_not_explain"),
                CheckResult("natural:snow_ice", "natural", "does_not_explain")]

    c = _candidate(checks=[CheckResult("natural_process", "natural", "not_run")])
    engine.run_checks(c, only=["natural_process"], registry=[("natural_process", multi, "natural", True)])
    assert {k.check: k.status for k in c.checks} == {
        "natural_process": "does_not_explain", "natural:snow_ice": "does_not_explain"}


def _series(after_values):
    dates = ["2021-01-10", "2021-03-10", "2021-05-10", "2021-06-20",
             "2021-09-05", "2021-10-05", "2021-11-05", "2021-12-05"]
    inside = [0.30, 0.31, 0.30, 0.30] + list(after_values)
    return {"dates": dates, "inside": {"brightness": inside, "ndvi": [0.1] * 8, "nbr": [0.1] * 8},
            "ring": {"brightness": [0.30] * 8, "ndvi": [0.1] * 8, "nbr": [0.1] * 8}}


def test_per_scene_support_separates_real_change_from_composite_artefact():
    meas = {"kind": "step", "break_year": 2021, "d_brightness": 0.10, "d_ndvi": 0.0, "d_nbr": 0.0}
    real = _candidate(measurements={**meas, "series": _series([0.40, 0.41, 0.40, 0.39])})
    assert artefacts._per_scene_support(real).status == "does_not_explain"
    fake = _candidate(measurements={**meas, "series": _series([0.30, 0.31, 0.30, 0.30])})
    assert artefacts._per_scene_support(fake).status == "explains"
    assert artefacts._per_scene_support(_candidate(measurements=meas)).status == "not_run"
    results = artefacts.check_artefacts(fake)
    assert results[0].check == "artefact_screen" and results[0].status == "explains"


def test_pivot_sized_disc_is_explained_as_agriculture(monkeypatch):
    monkeypatch.setattr(natural._Context, "landcover", lambda self, wide=False: {"bare": 1.0})
    monkeypatch.setattr(natural._Context, "terrain", lambda self: {"slope_deg": 0.5, "elevation_m": 200})
    disc = _candidate(area_m2=5.0e5, measurements={"d_ndvi": 0.4},
                      shape={"equivalent_diameter_m": 800.0, "circularity": 0.9})
    results = {r.check: r for r in natural.check_natural(disc)}
    assert results["natural:agriculture"].status == "explains"
    assert results["natural_process"].status == "explains"
    pad = _candidate(measurements={"d_brightness": 0.1},
                     shape={"equivalent_diameter_m": 200.0, "circularity": 0.5, "regularity": 0.8})
    assert {r.check: r for r in natural.check_natural(pad)}["natural_process"].status == "does_not_explain"


def test_human_context_marks_nearby_activity_inconclusive(monkeypatch):
    from skywatch.eliminate import context

    monkeypatch.setattr("skywatch.eliminate.landcover.landcover_fractions",
                        lambda lat, lon, r: {"bare": 1.0, "cropland": 0.0, "builtup": 0.0})
    remote = _candidate(checks=[CheckResult("osm_infrastructure", "infrastructure", "does_not_explain",
                                            evidence={"nearest_road_m": 5200.0, "nearest_building_m": None})])
    assert context.check_context(remote)[0].status == "does_not_explain"
    near = _candidate(checks=[CheckResult("osm_infrastructure", "infrastructure", "does_not_explain",
                                          evidence={"nearest_road_m": 80.0, "nearest_building_m": 600.0})])
    result = context.check_context(near)[0]
    assert result.status == "inconclusive" and "80 m" in result.detail
    nothing = _candidate(checks=[CheckResult("osm_infrastructure", "infrastructure", "not_run")])
    monkeypatch.setattr("skywatch.eliminate.landcover.landcover_fractions",
                        lambda lat, lon, r: (_ for _ in ()).throw(RuntimeError("down")))
    assert context.check_context(nothing)[0].status == "not_run"


def test_artefact_observation_count_reads_event_window_layout():
    from skywatch.core.models import Candidate
    from skywatch.eliminate import artefacts

    def cand(composites, year=2022):
        return Candidate(id="e", region_id="r", lat=0, lon=0, bbox=(0, 0, 1, 1), signature="unknown",
                         detector="optical_event", score=0.5, area_m2=3000, present_from="2022-04-07",
                         measurements={"kind": "event_window", "break_year": year, "composite_dates": composites})

    event = cand({"before": ["2021-10-24", "2021-11-13"], "after": ["2022-04-07", "2022-04-12", "2022-07-26"]})
    result = artefacts._observation_count(event)
    assert result.status == "does_not_explain" and result.evidence["dates_before"] == 2
    thin = cand({"before": ["2021-10-24"], "after": ["2022-04-07", "2022-04-12"]})
    assert artefacts._observation_count(thin).status == "inconclusive"
    yearly = cand({"2020": ["2020-07-01", "2020-07-11"], "2021": ["2021-07-02", "2021-07-12"],
                   "2022": ["2022-07-03", "2022-07-13"]}, year=2021)
    yearly.measurements["n_valid_years"] = 8
    assert artefacts._observation_count(yearly).status == "does_not_explain"
    assert artefacts._bracketing_dates({"2020": ["2020-07-01"]}, 2019) is None


def test_index_change_beyond_physical_range_is_an_artefact():
    from skywatch.core.models import Candidate
    from skywatch.eliminate import artefacts

    def cand(**m):
        return Candidate(id="x", region_id="r", lat=0, lon=0, bbox=(0, 0, 1, 1), signature="unknown",
                         detector="optical_change", score=0.5, area_m2=1600, measurements=m)

    assert artefacts._index_range(cand(d_ndvi=3.19, d_brightness=-0.1)).status == "explains"
    assert artefacts._index_range(cand(d_ndvi=-0.7, d_nbr=-0.76)).status == "does_not_explain"
    umbrella = artefacts.check_artefacts(cand(d_ndvi=3.19, kind="transient"))[0]
    assert umbrella.status == "explains" and "physical range" in umbrella.detail
