"""Tests for the OpenStreetMap infrastructure check and the WorldCover land-cover check."""
from __future__ import annotations

import multiprocessing
import threading
import time
from typing import Any, Callable

import numpy as np
import pytest
import requests

from skywatch.core import io
from skywatch.core.models import Candidate
from skywatch.eliminate import landcover, osm

LAT0, LON0 = 30.0, 10.0
KX, KY = osm._metres_per_degree(LAT0)


def ll(x: float, y: float) -> tuple[float, float]:
    """Metres east/north of the test origin -> (lat, lon)."""
    return LAT0 + y / KY, LON0 + x / KX


def cand(lat: float, lon: float, half_m: float = 30.0, **kw: Any) -> Candidate:
    return Candidate(id="c", region_id="r", lat=lat, lon=lon, bbox=io.point_bbox(lat, lon, half_m),
                     signature="unknown", detector="test", score=0.5,
                     area_m2=(2 * half_m) ** 2, **kw)


# --------------------------------------------------------------------------
# Synthetic OSM extract
# --------------------------------------------------------------------------

def _square(x0: float, y0: float, x1: float, y1: float) -> list[tuple[float, float]]:
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]


def build_xml() -> bytes:
    """A quarry, a track, a building, a power line, a mast and a military
    multipolygon with a hole, plus two ways that carry no real tags."""
    nodes: list[str] = []
    ways: list[str] = []
    next_id = [1]

    def add_way(way_id: int, pts: list[tuple[float, float]], tags: dict[str, str]) -> None:
        refs = []
        closed = len(pts) > 2 and pts[0] == pts[-1]
        for x, y in pts[:-1] if closed else pts:
            lat, lon = ll(x, y)
            nodes.append(f'<node id="{next_id[0]}" lat="{lat:.7f}" lon="{lon:.7f}"/>')
            refs.append(next_id[0])
            next_id[0] += 1
        if closed:
            refs.append(refs[0])
        body = "".join(f'<nd ref="{r}"/>' for r in refs)
        body += "".join(f'<tag k="{k}" v="{v}"/>' for k, v in tags.items())
        ways.append(f'<way id="{way_id}">{body}</way>')

    add_way(100, _square(1000, 1000, 1400, 1400), {"landuse": "quarry", "name": "Test Pit"})
    add_way(101, [(-2000, -500), (2000, -500)], {"highway": "track"})
    add_way(102, _square(-1500, 800, -1480, 820), {"building": "yes"})
    add_way(103, [(-2500, 2000), (2500, 2000)], {"power": "line"})
    add_way(104, [(0, 0), (50, 50)], {})
    add_way(105, [(0, 100), (50, 150)], {"source": "survey"})
    add_way(106, [(-2400, -2400), (-2000, -2400), (-2000, -2000)], {})
    add_way(107, [(-2000, -2000), (-2400, -2000), (-2400, -2400)], {})
    add_way(108, _square(-2300, -2300, -2100, -2100), {})
    add_way(109, _square(500, -2600, 600, -2500), {"highway": "residential"})  # loop road
    lat, lon = ll(0, -1500)
    nodes.append(f'<node id="900" lat="{lat:.7f}" lon="{lon:.7f}"><tag k="man_made" v="mast"/></node>')
    # ways 106 and 107 share end nodes by coordinate, as real members share node ids
    relation = ('<relation id="500"><member type="way" ref="106" role="outer"/>'
                '<member type="way" ref="107" role="outer"/><member type="way" ref="108" role="inner"/>'
                '<member type="way" ref="9999" role="outer"/>'
                '<tag k="type" v="multipolygon"/><tag k="landuse" v="military"/></relation>')
    return ('<?xml version="1.0"?><osm version="0.6">' + "".join(nodes) + "".join(ways)
            + relation + "</osm>").encode()


class FakeResponse:
    def __init__(self, status_code: int = 200, content: bytes = b"") -> None:
        self.status_code = status_code
        self.content = content
        self.text = content.decode("utf-8", "replace")
        self.headers: dict[str, str] = {}


def _width(params: dict[str, str]) -> float:
    west, _, east, _ = (float(v) for v in params["bbox"].split(","))
    return east - west


@pytest.fixture
def fake_osm(tmp_path, monkeypatch) -> Callable[[Callable[[dict[str, str]], FakeResponse]], list]:
    """Point the module at an empty cache and a scripted API; returns the call log."""
    monkeypatch.setattr(osm, "CACHE_DIR", tmp_path / "osm")
    monkeypatch.setattr(osm, "MIN_INTERVAL_S", 0.0)
    osm._parsed_file.cache_clear()
    calls: list[tuple[float, str]] = []

    def install(handler: Callable[[dict[str, str]], FakeResponse]) -> list:
        def fake(params: dict[str, str]) -> FakeResponse:
            calls.append((time.time(), params["bbox"]))
            return handler(params)
        monkeypatch.setattr(osm, "_http_get", fake)
        return calls
    return install


def ok(_: dict[str, str]) -> FakeResponse:
    return FakeResponse(200, build_xml())


# --------------------------------------------------------------------------
# OSM unit tests
# --------------------------------------------------------------------------

def test_classify_separates_causes_from_plain_roads() -> None:
    assert osm.classify({"landuse": "quarry"}) == "landuse=quarry"
    assert osm.classify({"aeroway": "runway"}) == "aeroway=runway"
    assert osm.classify({"building": "yes", "power": "plant"}) == "power=plant"
    assert osm.classify({"disused:man_made": "mineshaft"}) == "disused:man_made=mineshaft"
    assert osm.classify({"highway": "construction"}) == "highway=construction"
    assert osm.classify({"historic": "archaeological_site"}) == "historic=archaeological_site"
    for tags in ({"highway": "track"}, {"highway": "primary"}, {"building": "no"},
                 {"natural": "scrub"}, {"landuse": "forest"}, {"barrier": "fence"}, {}):
        assert osm.classify(tags) is None, tags
    assert osm.is_road({"highway": "track"}) and not osm.is_road({"highway": "footway"})


def test_features_have_geometry_and_true_distances(fake_osm) -> None:
    fake_osm(ok)
    lat, lon = ll(1200, 1200)  # centre of the quarry
    feats = osm.osm_features(lat, lon, 5000.0)
    by_id = {(f["osm_type"], f["osm_id"]): f for f in feats}
    assert ("way", 104) not in by_id and ("way", 105) not in by_id  # untagged / metadata only
    assert ("way", 106) not in by_id  # untagged member way is only part of its relation
    quarry = by_id[("way", 100)]
    assert quarry["distance_m"] == 0.0 and quarry["geom_type"] == "Polygon"
    assert quarry["explains"] == "landuse=quarry" and len(quarry["geometry"]) == 5
    assert by_id[("way", 101)]["distance_m"] == pytest.approx(1700, abs=3)
    assert by_id[("way", 101)]["is_road"] and by_id[("way", 101)]["explains"] is None
    assert by_id[("way", 103)]["distance_m"] == pytest.approx(800, abs=3)
    assert by_id[("node", 900)]["distance_m"] == pytest.approx(np.hypot(1200, 2700), abs=5)
    assert [f["distance_m"] for f in feats] == sorted(f["distance_m"] for f in feats)
    assert all(f["distance_m"] <= 5000 for f in feats)


def test_multipolygon_relation_area_and_hole(fake_osm) -> None:
    fake_osm(ok)
    inside = {f["osm_id"]: f for f in osm.osm_features(*ll(-2350, -2350), 2000.0)}[500]
    assert inside["distance_m"] == 0.0 and inside["explains"] == "landuse=military"
    in_hole = {f["osm_id"]: f for f in osm.osm_features(*ll(-2200, -2200), 2000.0)}[500]
    assert in_hole["distance_m"] == pytest.approx(100, abs=3)  # to the inner ring
    # A closed highway is a loop line, not an area: its centre is 50 m from it.
    loop = {f["osm_id"]: f for f in osm.osm_features(*ll(550, -2550), 2000.0)}[109]
    assert loop["distance_m"] == pytest.approx(50, abs=3)


def test_check_explains_inside_and_beside_a_quarry_but_not_far_from_it(fake_osm) -> None:
    fake_osm(ok)
    inside = osm.check_osm(cand(*ll(1200, 1200)))[0]
    assert (inside.check, inside.category, inside.status) == ("osm_infrastructure", "infrastructure", "explains")
    assert inside.evidence["explaining"][0]["kind"] == "landuse=quarry"
    assert inside.evidence["explaining"][0]["distance_m"] == 0.0
    assert "Test Pit" in inside.detail
    beside = osm.check_osm(cand(*ll(1550, 1200), half_m=60))[0]  # footprint edge 90 m off
    assert beside.status == "explains" and beside.evidence["tolerance_m"] == pytest.approx(120, abs=1)
    assert beside.evidence["explaining"][0]["distance_m"] == pytest.approx(90, abs=3)
    far = osm.check_osm(cand(*ll(1900, 1200), half_m=60))[0]  # 440 m off
    assert far.status == "does_not_explain"
    assert "incomplete" in far.detail and "weak evidence" in far.detail
    assert far.evidence["nearby_beyond_tolerance"][0]["kind"] == "landuse=quarry"


def test_a_road_alone_never_explains_but_is_always_measured(fake_osm) -> None:
    fake_osm(ok)
    result = osm.check_osm(cand(*ll(0, -500)))[0]  # sitting on the track
    assert result.status == "does_not_explain"
    assert result.evidence["nearest_road_m"] == 0.0
    assert result.evidence["nearest_road"]["highway"] == "track"
    assert result.evidence["nearest_building_m"] == pytest.approx(np.hypot(1450, 1270), abs=5)
    off_road = osm.check_osm(cand(*ll(0, 0)))[0]
    assert off_road.evidence["nearest_road_m"] == pytest.approx(470, abs=3)  # from footprint edge


def test_tolerance_follows_footprint_size(fake_osm) -> None:
    fake_osm(ok)
    small = osm.check_osm(cand(*ll(0, 0), half_m=5))[0]
    large = osm.check_osm(cand(*ll(0, 0), half_m=400))[0]
    assert small.evidence["tolerance_m"] == 100.0 and large.evidence["tolerance_m"] == 300.0


def test_second_call_is_served_from_cache(fake_osm) -> None:
    calls = fake_osm(ok)
    first = osm.check_osm(cand(*ll(1200, 1200)))[0]
    second = osm.check_osm(cand(*ll(1200, 1200)))[0]
    neighbour = osm.check_osm(cand(*ll(1230, 1180)))[0]  # snapped box is shared
    assert len(calls) == 1
    assert first.evidence["network_requests"] == 1 and second.evidence["network_requests"] == 0
    assert neighbour.evidence["network_requests"] == 0 and second.status == "explains"


def test_network_failure_is_not_run_and_is_not_cached(fake_osm, monkeypatch) -> None:
    monkeypatch.setattr(osm.time, "sleep", lambda _: None)

    def down(_: dict[str, str]) -> FakeResponse:
        raise requests.ConnectionError("proxy refused")
    calls = fake_osm(down)
    result = osm.check_osm(cand(*ll(1200, 1200)))[0]
    assert result.status == "not_run" and "could not be queried" in result.detail
    assert len(calls) == osm._RETRIES
    assert not list(osm.CACHE_DIR.glob("map_*"))
    with pytest.raises(osm.OsmUnavailable):
        osm.osm_features(*ll(1200, 1200))
    fake_osm(lambda _: FakeResponse(503, b"busy"))
    assert osm.check_osm(cand(*ll(1200, 1200)))[0].status == "not_run"
    fake_osm(lambda _: FakeResponse(429, b"slow down"))
    before = len(calls)
    assert osm.check_osm(cand(*ll(1200, 1200)))[0].status == "not_run"
    assert len(calls) == before + 1  # a rate-limit answer is not retried
    fake_osm(ok)  # the outage left nothing behind: the next call succeeds
    assert osm.check_osm(cand(*ll(1200, 1200)))[0].status == "explains"


def dense(params: dict[str, str]) -> FakeResponse:
    """An API that refuses any box wider than 0.03 degrees."""
    if _width(params) > 0.03:
        return FakeResponse(400, b"You requested too many nodes (limit is 50000). Either request "
                                 b"a smaller area, or use planet.osm")
    return FakeResponse(200, build_xml())


def test_refused_box_is_shrunk_and_refusals_are_cached(fake_osm) -> None:
    calls = fake_osm(dense)
    result = osm.check_osm(cand(*ll(1200, 1200)))[0]
    assert result.status == "explains"
    assert 750 <= result.evidence["covered_radius_m"] < 1000
    assert result.evidence["network_requests"] == 3 and len(calls) == 3  # 3000, 1500, 750 m
    again = osm.check_osm(cand(*ll(1200, 1200)))[0]
    assert again.evidence["network_requests"] == 0 and len(calls) == 3


def test_footprint_larger_than_the_covered_area_is_not_run(fake_osm) -> None:
    fake_osm(dense)
    result = osm.check_osm(cand(*ll(-400, 0), half_m=700))[0]
    assert result.status == "not_run" and "covers only" in result.detail
    assert result.evidence["explaining"] == []


def test_area_dense_at_every_size_is_not_run(fake_osm) -> None:
    calls = fake_osm(lambda _: FakeResponse(400, b"You requested too many nodes (limit is 50000)."))
    result = osm.check_osm(cand(*ll(0, 0)))[0]
    assert result.status == "not_run" and "too many nodes" in result.detail
    # 3000, 1500, 750 and 375 m; the final 300 m try snaps to the 375 m box, whose
    # cached refusal is reused instead of asking again.
    assert len(calls) == 4


def test_hostile_inputs(fake_osm) -> None:
    calls = fake_osm(lambda _: FakeResponse(200, b'<?xml version="1.0"?><osm version="0.6"></osm>'))
    nan = osm.check_osm(cand(float("nan"), 10.0))[0]
    assert nan.status == "not_run" and not calls  # nothing is sent for a bad coordinate
    assert osm.check_osm(cand(95.0, 10.0))[0].status == "not_run"
    empty = osm.check_osm(cand(*ll(0, 0)))[0]
    assert empty.status == "does_not_explain" and empty.evidence["n_tagged_features"] == 0
    assert empty.evidence["nearest_road_m"] is None and empty.evidence["nearest_building_m"] is None
    assert "no tagged feature" in empty.detail and "incomplete" in empty.detail
    assert osm.osm_features(*ll(0, 0)) == []
    broken = cand(*ll(0, 0))
    broken.bbox = (float("nan"),) * 4  # type: ignore[assignment]
    broken.area_m2 = float("nan")
    point = osm.check_osm(broken)[0]
    assert point.status == "does_not_explain" and point.evidence["footprint_source"] == "point"


def test_box_clipped_at_the_antimeridian_is_not_run_when_nothing_is_found(fake_osm) -> None:
    fake_osm(lambda _: FakeResponse(200, b'<?xml version="1.0"?><osm version="0.6"></osm>'))
    result = osm.check_osm(cand(30.0, 179.9995))[0]  # about 48 m from the +/-180 line
    assert result.status == "not_run" and result.evidence["covered_radius_m"] < 60
    assert "covers only" in result.detail


def test_corrupt_response_is_not_run_and_dropped_from_cache(fake_osm) -> None:
    fake_osm(lambda _: FakeResponse(200, b"<osm><node id='1' lat='1'"))
    result = osm.check_osm(cand(*ll(0, 0)))[0]
    assert result.status == "not_run"
    assert not list(osm.CACHE_DIR.glob("map_*.xml.gz"))


def test_requests_are_spaced_one_second_apart_across_threads(fake_osm, monkeypatch) -> None:
    calls = fake_osm(ok)
    monkeypatch.setattr(osm, "MIN_INTERVAL_S", 1.0)
    boxes = [(10.0 + i, 30.0, 10.01 + i, 30.01) for i in range(3)]
    threads = [threading.Thread(target=osm._fetch_box, args=(b,)) for b in boxes]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    stamps = sorted(t for t, _ in calls)
    assert len(stamps) == 3
    assert all(b - a >= 0.99 for a, b in zip(stamps, stamps[1:])), stamps


def _child_fetch(bbox: tuple[float, float, float, float], log_path: str) -> None:
    def fake(params: dict[str, str]) -> FakeResponse:
        with open(log_path, "a") as handle:
            handle.write(f"{time.time():.6f}\n")
        return FakeResponse(200, build_xml())
    osm._http_get = fake  # type: ignore[assignment]
    osm._fetch_box(bbox)


def test_requests_are_spaced_one_second_apart_across_processes(fake_osm, monkeypatch, tmp_path) -> None:
    fake_osm(ok)
    monkeypatch.setattr(osm, "MIN_INTERVAL_S", 1.0)
    log = tmp_path / "stamps.txt"
    ctx = multiprocessing.get_context("fork")
    procs = [ctx.Process(target=_child_fetch, args=((20.0 + i, 30.0, 20.01 + i, 30.01), str(log)))
             for i in range(3)]
    for proc in procs:
        proc.start()
    for proc in procs:
        proc.join(30)
    stamps = sorted(float(line) for line in log.read_text().split())
    assert len(stamps) == 3
    assert all(b - a >= 0.99 for a, b in zip(stamps, stamps[1:])), stamps
    assert len(list(osm.CACHE_DIR.glob("map_*.xml.gz"))) == 3


# --------------------------------------------------------------------------
# Land-cover unit tests
# --------------------------------------------------------------------------

@pytest.fixture
def lc_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(landcover, "CACHE_DIR", tmp_path / "landcover")
    return tmp_path / "landcover"


def test_tile_names() -> None:
    assert landcover.tile_name(36.5, -116.5) == "N36W117"
    assert landcover.tile_name(-1.5, 10.2) == "S03E009"
    assert landcover.tile_name(0.0, 0.0) == "N00E000"
    assert landcover.tile_name(-0.1, -0.1) == "S03W003"
    assert landcover.tile_name(59.9, 179.9) == "N57E177"
    assert landcover.tile_name(40.7549, -73.9840) == "N39W075"
    assert set(landcover._tiles_for((-117.01, 35.99, -116.99, 36.01))) == {
        "N33W120", "N33W117", "N36W120", "N36W117"}
    assert landcover._tiles_for((-116.6, 36.4, -116.5, 36.5)) == ["N36W117"]


def test_fractions_cover_every_key_and_sum_to_one() -> None:
    classes = np.array([[40, 40, 50, 0], [60, 60, 60, 60], [80, 90, 95, 7]], dtype="uint8")
    frac = landcover.fractions_from_classes(classes)
    assert tuple(frac) == landcover.FRACTION_KEYS and sum(frac.values()) == pytest.approx(1.0)
    assert frac["cropland"] == pytest.approx(2 / 12) and frac["bare"] == pytest.approx(4 / 12)
    assert frac["nodata"] == pytest.approx(2 / 12)  # the 0 and the unknown code 7
    masked = landcover.fractions_from_classes(classes, classes == 40)
    assert masked["cropland"] == 1.0
    assert landcover.fractions_from_classes(classes, np.zeros(classes.shape, bool))["nodata"] == 1.0


def _frac(**kw: float) -> dict[str, float]:
    out = {k: 0.0 for k in landcover.FRACTION_KEYS}
    out.update(kw)
    return out


def test_evaluate_rules() -> None:
    bare = _frac(bare=1.0)
    assert landcover.evaluate_landcover(_frac(cropland=0.8, bare=0.2), bare)[0] == "explains"
    assert landcover.evaluate_landcover(_frac(water=0.3, wetland=0.3, bare=0.4), bare)[0] == "explains"
    status, detail, extra = landcover.evaluate_landcover(_frac(bare=0.9, shrub=0.1), bare)
    assert status == "does_not_explain" and extra["dominant"] == "bare" and "bare" in detail
    assert landcover.evaluate_landcover(_frac(tree=1.0), bare)[0] == "does_not_explain"
    assert landcover.evaluate_landcover(_frac(nodata=0.9, cropland=0.1), bare)[0] == "not_run"
    # half the footprint unmapped, the mapped half cropland: judged on the mapped part
    assert landcover.evaluate_landcover(_frac(nodata=0.5, cropland=0.5), bare)[0] == "explains"
    mixed = landcover.evaluate_landcover(_frac(cropland=0.3, water=0.3, bare=0.4), bare)
    assert mixed[0] == "explains" and mixed[2]["explained_by"] == "mixed"


def test_builtup_explains_only_when_independent_of_the_candidate() -> None:
    built = _frac(builtup=0.9, bare=0.1)
    lone, town = _frac(bare=1.0), _frac(builtup=0.4, bare=0.6)
    status, detail, extra = landcover.evaluate_landcover(built, lone, "2018-07-01", "2019-07-01")
    assert status == "does_not_explain" and extra["map_predates_onset"] is False
    assert "candidate itself" in detail
    assert landcover.evaluate_landcover(built, lone)[0] == "does_not_explain"  # undated
    assert landcover.evaluate_landcover(built, town, "2018-07-01", "2019-07-01")[0] == "explains"
    later = landcover.evaluate_landcover(built, lone, "2022-08-01", "2023-06-01")
    assert later[0] == "explains" and later[2]["map_predates_onset"] is True
    straddle = landcover.evaluate_landcover(built, lone, "2021-08-01", "2022-06-01")
    assert straddle[0] == "does_not_explain" and straddle[2]["map_predates_onset"] is None


def test_check_landcover_on_synthetic_rasters(lc_cache, monkeypatch) -> None:
    lat, lon = 36.5, -116.9
    candidate = cand(lat, lon, half_m=60)
    scene: dict[str, Any] = {}

    def fake_read(grid: io.Grid):
        classes = np.full(grid.shape, scene["around"], dtype="uint8")
        classes[landcover._rect_mask(grid, candidate.bbox, lat, lon)] = scene["inside"]
        return classes, ["N36W117"], []
    monkeypatch.setattr(landcover, "_read_classes", fake_read)

    scene.update(inside=40, around=60)
    field = landcover.check_landcover(candidate)[0]
    assert (field.check, field.category, field.status) == ("landcover", "natural", "explains")
    assert field.evidence["footprint"]["cropland"] == 1.0 and field.evidence["context"]["bare"] == 1.0
    assert 100 <= field.evidence["footprint_pixels"] <= 225  # about 120 m x 120 m at 10 m

    scene.update(inside=60, around=60)
    desert = landcover.check_landcover(candidate)[0]
    assert desert.status == "does_not_explain" and desert.evidence["footprint"]["bare"] == 1.0

    scene.update(inside=50, around=60)
    assert landcover.check_landcover(candidate)[0].status == "does_not_explain"  # lone structure
    scene.update(inside=50, around=50)
    assert landcover.check_landcover(candidate)[0].status == "explains"  # inside a town

    scene.update(inside=0, around=0)
    empty = landcover.check_landcover(candidate)[0]
    assert empty.status == "not_run" and "no data" in empty.detail


def test_landcover_failures_are_not_run(lc_cache, monkeypatch) -> None:
    monkeypatch.setattr(landcover, "_tile_exists", lambda name: True)

    def boom(*args: Any, **kwargs: Any) -> np.ndarray:
        raise RuntimeError("read failed after 3 tries")
    monkeypatch.setattr(landcover.io, "read_to_grid", boom)
    result = landcover.check_landcover(cand(36.5, -116.9))[0]
    assert result.status == "not_run" and "unreadable" in result.detail
    assert not list(lc_cache.rglob("*.npz"))  # a failed read is never cached
    with pytest.raises(landcover.LandcoverUnavailable):
        landcover.landcover_fractions(36.5, -116.9, 200.0)
    assert landcover.check_landcover(cand(float("nan"), -116.9))[0].status == "not_run"
    assert landcover.check_landcover(cand(36.5, 500.0))[0].status == "not_run"
    for radius in (0.0, float("nan"), 1e7):
        with pytest.raises(ValueError):
            landcover.landcover_fractions(36.5, -116.9, radius)


def test_absent_tile_is_nodata_not_water(lc_cache, monkeypatch) -> None:
    monkeypatch.setattr(landcover, "_tile_exists", lambda name: False)
    monkeypatch.setattr(landcover.io, "read_to_grid",
                        lambda *a, **k: pytest.fail("an absent tile must not be read"))
    frac = landcover.landcover_fractions(1.5, -28.5, 300.0)
    assert frac["nodata"] == 1.0 and frac["water"] == 0.0
    built = landcover.builtup_within(1.5, -28.5, 300.0)
    assert built["nearest_builtup_m"] is None and built["nodata_fraction"] == 1.0
    result = landcover.check_landcover(cand(1.5, -28.5))[0]
    assert result.status == "not_run" and result.evidence["missing_tiles"] == ["N00W030"]


def test_tile_index_caches_answers_but_not_failures(lc_cache, monkeypatch) -> None:
    monkeypatch.setattr(landcover.time, "sleep", lambda _: None)
    calls: list[str] = []
    answer: dict[str, Any] = {"code": 404}

    def fake_head(url: str, **kwargs: Any) -> FakeResponse:
        calls.append(url)
        if answer["code"] is None:
            raise requests.ConnectionError("down")
        return FakeResponse(answer["code"])
    monkeypatch.setattr(landcover.requests, "head", fake_head)
    assert landcover._tile_exists("N00W030") is False
    assert landcover._tile_exists("N00W030") is False and len(calls) == 1
    assert landcover._tile_exists("S63E000") is False and len(calls) == 1  # outside the map
    answer["code"] = None
    with pytest.raises(landcover.LandcoverUnavailable):
        landcover._tile_exists("N36W117")
    assert len(calls) == 1 + landcover._RETRIES
    answer["code"] = 403
    with pytest.raises(landcover.LandcoverUnavailable):
        landcover._tile_exists("N36W117")
    answer["code"] = 200
    assert landcover._tile_exists("N36W117") is True  # the outage was not remembered


def test_builtup_statistics_on_a_synthetic_raster() -> None:
    classes = np.full((201, 201), 60, dtype="uint8")
    yy, xx = np.ogrid[:201, :201]
    dist = (np.hypot(xx - 100, yy - 100) * 10.0).astype("float32")
    mask = dist <= 800
    none = landcover._builtup_stats(classes, mask, dist)
    assert none["nearest_builtup_m"] is None and none["builtup_fraction"] == 0.0
    classes[99:102, 149:152] = 50   # a 3 x 3 block 490-510 m east
    classes[100, 80] = 50           # a lone pixel 200 m west
    stats = landcover._builtup_stats(classes, mask, dist)
    assert stats["nearest_builtup_m"] == pytest.approx(200, abs=1)
    assert stats["nearest_builtup_cluster_m"] == pytest.approx(490, abs=1)
    assert stats["builtup_pixels"] == 10
    assert stats["builtup_fraction"] == pytest.approx(10 / mask.sum())
    classes[100, 100] = 50
    assert landcover._builtup_stats(classes, mask, dist)["nearest_builtup_m"] == 0.0
    classes[:] = 0
    assert landcover._builtup_stats(classes, mask, dist)["nodata_fraction"] == 1.0


# --------------------------------------------------------------------------
# Live tests (real hosts, real cache)
# --------------------------------------------------------------------------

@pytest.mark.network
def test_live_osm_airport_is_explained_and_cached() -> None:
    runway = cand(35.0594, -118.1517, half_m=60)  # Mojave Air and Space Port runway
    first = osm.check_osm(runway)[0]
    assert first.status == "explains", first.detail
    assert first.evidence["explaining"][0]["kind"].startswith("aeroway=")
    assert first.evidence["nearest_road_m"] is not None and first.evidence["nearest_building_m"] is not None
    start = time.time()
    second = osm.check_osm(runway)[0]
    assert second.evidence["network_requests"] == 0 and time.time() - start < 2.0
    assert second.status == "explains"


@pytest.mark.network
def test_live_osm_empty_desert_is_not_explained() -> None:
    result = osm.check_osm(cand(18.5, 11.5, half_m=60))[0]  # Tenere, Niger
    assert result.status == "does_not_explain", result.detail
    assert result.evidence["explaining"] == [] and "incomplete" in result.detail
    assert result.evidence["covered_radius_m"] >= 3000


@pytest.mark.network
def test_live_landcover_field_city_desert_ocean() -> None:
    field = landcover.check_landcover(cand(42.05, -93.90, half_m=60))[0]  # Iowa
    assert field.status == "explains" and field.evidence["explained_by"] == "cropland", field.detail
    city = landcover.check_landcover(cand(40.7549, -73.9840, half_m=60))[0]  # Midtown Manhattan
    assert city.status == "explains" and city.evidence["explained_by"] == "builtup", city.detail
    desert = landcover.check_landcover(cand(36.50, -116.90, half_m=60))[0]  # Death Valley
    assert desert.status == "does_not_explain" and desert.evidence["footprint"]["bare"] > 0.9
    ocean = landcover.check_landcover(cand(1.5, -28.5, half_m=60))[0]  # mid-Atlantic, no tile
    assert ocean.status == "not_run" and ocean.evidence["missing_tiles"] == ["N00W030"]


@pytest.mark.network
def test_live_builtup_and_fractions() -> None:
    town = landcover.builtup_within(40.7549, -73.9840, 1000.0)
    assert town["builtup_fraction"] > 0.8 and town["nearest_builtup_m"] == 0.0
    wild = landcover.builtup_within(36.50, -116.90, 1000.0)
    assert wild["builtup_fraction"] == 0.0 and wild["nearest_builtup_m"] is None
    frac = landcover.landcover_fractions(36.50, -116.90, 1000.0)
    assert frac["bare"] > 0.95 and sum(frac.values()) == pytest.approx(1.0)
