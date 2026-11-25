"""Tests for the catalogue checks: Wikidata, aviation accidents, meteorites, ranges."""
from __future__ import annotations

import json
import math
import time
from http import HTTPStatus
from typing import Any

import pandas as pd
import pytest
import requests

from skywatch.core.models import Candidate
from skywatch.eliminate import records, wikidata


def make_candidate(lat: float, lon: float, absent: str | None = None, present: str | None = None,
                   signature: str = "crash", area_m2: float = 2500.0) -> Candidate:
    return Candidate(id="t1", region_id="r", lat=lat, lon=lon, bbox=(lon - 0.001, lat - 0.001, lon + 0.001, lat + 0.001),
                     signature=signature, detector="test", score=0.5, area_m2=area_m2,  # type: ignore[arg-type]
                     absent_until=absent, present_from=present)


def item(qid: str, label: str, category: str, dist: float, date: str | None = None,
         precision: str | None = None, classes: list[str] | None = None) -> dict[str, Any]:
    return {"qid": qid, "label": label, "instance_of": classes or [category], "instance_of_qids": [], "category": category,
            "categories": [category], "distance_km": dist, "lat": 0.0, "lon": 0.0, "date": date,
            "date_precision": precision if date else None, "date_property": "P585" if date else None, "url": ""}


class FakeResponse:
    def __init__(self, status: int, payload: Any = None) -> None:
        self.status_code = int(status)
        self._payload = payload
        self.headers: dict[str, str] = {}
        self.text = "fake"

    def json(self) -> Any:
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


@pytest.fixture(autouse=True)
def isolated(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    """Unit tests get an empty cache, no pacing delays and no network; live tests keep the real settings."""
    records.clear_cache()
    wikidata.reset_breaker()
    if request.node.get_closest_marker("network"):
        yield
        records.clear_cache()
        return

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("unit test tried to use the network")

    monkeypatch.setattr(requests, "get", forbidden)
    monkeypatch.setattr(wikidata, "CACHE_DIR", tmp_path / "wd")
    monkeypatch.setattr(wikidata, "RETRY_SLEEPS", (0.0, 0.0))
    monkeypatch.setattr(wikidata, "MIN_INTERVAL_S", 0.0)
    yield
    records.clear_cache()
    wikidata.reset_breaker()


# ---------------------------------------------------------------- wikidata: pure logic

def test_classify_labels_maps_classes_and_avoids_traps() -> None:
    assert wikidata.classify_labels(["open-pit mine"]) == ["mine_or_quarry"]
    assert wikidata.classify_labels(["stratovolcano"]) == ["volcano_or_geothermal"]
    assert wikidata.classify_labels(["aviation accident"]) == ["aviation_accident"]
    assert wikidata.classify_labels(["military airbase"])[0] == "military"
    assert wikidata.classify_labels(["wind farm"])[0] == "power_or_industry"
    assert wikidata.classify_labels(["city", "national park"]) == ["settlement", "protected_area"]
    # Words that merely contain or neighbour a keyword must not become causal categories.
    for label in ("naval mine", "military operation", "Amsterdam", "macadam road", "oil company", "mountain", "battle"):
        assert wikidata.classify_labels([label]) == [], label
    assert set(wikidata.EXPLAIN_KM) == set(wikidata.CATEGORIES) - {"settlement", "protected_area", "other"}


def test_bindings_are_grouped_per_item_with_best_date_and_priority() -> None:
    def row(qid: str, dist: str, cls: str, cls_label: str, **extra: str) -> dict[str, Any]:
        out: dict[str, Any] = {"item": {"value": f"http://www.wikidata.org/entity/{qid}"}, "itemLabel": {"value": f"L{qid}"},
                               "dist": {"value": dist}, "loc": {"value": "Point(10.5 -20.25)"},
                               "class": {"value": f"http://www.wikidata.org/entity/{cls}"}, "classLabel": {"value": cls_label}}
        out.update({k: {"value": v} for k, v in extra.items()})
        return out

    rows = [row("Q1", "1.5", "Q10", "village", inc="1900-01-01T00:00:00Z", incPrec="9", links="2", ceb="u1", sv="u2"),
            row("Q1", "1.2", "Q11", "gold mine", pit="2021-05-04T00:00:00Z", pitPrec="11", links="2", ceb="u1", sv="u2"),
            row("Q2", "0.4", "Q12", "thing nobody maps"),
            {"item": {"value": "not-a-qid"}, "dist": {"value": "0.1"}}]
    items = wikidata._finalise(wikidata._items_from_bindings(rows), {"Q12": ["impact_crater"]})
    assert [i["qid"] for i in items] == ["Q2", "Q1"]
    assert items[0]["category"] == "impact_crater"  # resolved through the subclass map
    mine = items[1]
    assert mine["distance_km"] == 1.2 and mine["category"] == "mine_or_quarry"
    assert mine["categories"] == ["mine_or_quarry", "settlement"]
    assert (mine["date"], mine["date_precision"], mine["date_property"]) == ("2021-05-04", "day", "P585")
    assert (mine["lat"], mine["lon"]) == (-20.25, 10.5)
    assert (mine["sitelinks"], mine["notable_sitelinks"]) == (2, 0)  # only bot-written Cebuano/Swedish stubs
    assert items[0]["notable_sitelinks"] is None  # unknown stays unknown


def test_date_helpers() -> None:
    assert wikidata.date_interval("2022-03-21", "day") == (wikidata.parse_iso_date("2022-03-21"),) * 2
    start, end = wikidata.date_interval("2020-02-01", "month")  # type: ignore[misc]
    assert (start.day, end.day) == (1, 29)
    assert wikidata.date_interval("1900-01-01", "century") is None
    assert wikidata.date_interval("-0300-01-01", "year") is None
    cand = make_candidate(0, 0, "2022-04-01T10:00:00Z", "2022-03-01")  # reversed and with a time part
    window = wikidata.onset_window(cand, pad_days=30)
    assert window is not None and window[0].isoformat() == "2022-01-30" and window[1].isoformat() == "2022-05-01"
    assert wikidata.onset_window(make_candidate(0, 0, None, "2022-03-01")) is None
    assert wikidata.haversine_km(0, 0, 0, 1) == pytest.approx(111.195, abs=0.01)


def test_site_within_limit_explains_but_settlement_never_does() -> None:
    cand = make_candidate(10, 10)
    near_mine = wikidata.evaluate_items(cand, [item("Q1", "Pit", "mine_or_quarry", 1.5)], 10.0)
    assert near_mine.status == "explains" and near_mine.check == "wikidata_nearby" and near_mine.category == "infrastructure"
    assert near_mine.evidence["explaining"][0]["qid"] == "Q1"
    far_mine = wikidata.evaluate_items(cand, [item("Q1", "Pit", "mine_or_quarry", 3.0)], 10.0)
    assert far_mine.status == "does_not_explain"
    assert far_mine.evidence["causal_near_misses"][0]["distance_km"] == 3.0 and "Pit" in far_mine.detail
    benign = wikidata.evaluate_items(cand, [item("Q2", "Town", "settlement", 0.1), item("Q3", "Park", "protected_area", 0.2)], 10.0)
    assert benign.status == "does_not_explain" and benign.evidence["nearest"][0]["label"] == "Town"
    empty = wikidata.evaluate_items(cand, [], 10.0)
    assert empty.status == "does_not_explain" and empty.evidence["n_items"] == 0


def test_minor_site_without_any_article_only_explains_at_short_range() -> None:
    cand = make_candidate(10, 10, area_m2=0.0)  # bbox half-diagonal ~0.16 km is used as the footprint
    adit = {**item("Q7", "Apex Tunnel", "mine_or_quarry", 1.5), "notable_sitelinks": 0}
    far = wikidata.evaluate_items(cand, [adit], 10.0)
    assert far.status == "does_not_explain" and far.evidence["causal_near_misses"][0]["qid"] == "Q7"
    assert wikidata.evaluate_items(cand, [{**adit, "distance_km": 0.4}], 10.0).status == "explains"
    assert wikidata.evaluate_items(cand, [{**adit, "notable_sitelinks": 12}], 10.0).status == "explains"
    # A recorded crash keeps its 2 km limit even without an article: its date does the filtering.
    crash = {**item("Q9", "Flight 1", "aviation_accident", 1.5, "2022-03-21", "day"), "notable_sitelinks": 0}
    assert wikidata.evaluate_items(make_candidate(10, 10, "2022-03-10", "2022-04-02"), [crash], 10.0).status == "explains"


def test_event_items_need_a_date_inside_the_onset_window() -> None:
    crash = item("Q9", "Flight 1", "aviation_accident", 0.5, "2022-03-21", "day")
    dated = make_candidate(10, 10, "2022-03-10", "2022-04-02")
    assert wikidata.evaluate_items(dated, [crash], 10.0).status == "explains"
    later = make_candidate(10, 10, "2024-03-10", "2024-04-02")
    result = wikidata.evaluate_items(later, [crash], 10.0)
    assert result.status == "does_not_explain" and result.evidence["events_outside_window"][0]["qid"] == "Q9"
    no_date = item("Q9", "Flight 1", "aviation_accident", 0.5)
    assert wikidata.evaluate_items(dated, [no_date], 10.0).status == "inconclusive"
    # Year precision: the whole year is compared, so 2022 overlaps the window.
    assert wikidata.evaluate_items(dated, [item("Q8", "Fall", "meteorite", 1.0, "2022-01-01", "year")], 10.0).status == "explains"
    # Without an onset window proximity alone decides.
    assert wikidata.evaluate_items(make_candidate(10, 10), [no_date], 10.0).status == "explains"


def test_truncated_item_list_short_of_the_limit_is_inconclusive() -> None:
    cand = make_candidate(10, 10)
    dense = [item(f"Q{i}", "Statue", "other", 0.3) for i in range(50)]
    assert wikidata.evaluate_items(cand, dense, 10.0, truncated=True).status == "inconclusive"
    assert wikidata.evaluate_items(cand, dense, 10.0, truncated=False).status == "does_not_explain"


# ---------------------------------------------------------------- wikidata: endpoint behaviour

def test_network_failure_is_not_run_and_then_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    def down(*args: Any, **kwargs: Any) -> Any:
        calls.append(1)
        raise requests.ConnectionError("proxy refused")

    monkeypatch.setattr(requests, "get", down)
    result = wikidata.check_wikidata(make_candidate(20.5, 51.5))
    assert len(result) == 1 and result[0].status == "not_run" and "unavailable" in result[0].detail
    assert len(calls) == 3  # three attempts, no fallback query for a dead connection
    with pytest.raises(wikidata.WikidataError) as info:
        wikidata.nearby_items(20.5, 51.6)
    assert info.value.kind == "breaker" and len(calls) == 3


def test_server_errors_are_not_run_never_does_not_explain(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse(HTTPStatus.SERVICE_UNAVAILABLE))
    assert wikidata.check_wikidata(make_candidate(20.5, 51.5))[0].status == "not_run"
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse(HTTPStatus.OK, payload=None))
    assert wikidata.check_wikidata(make_candidate(20.5, 51.5))[0].status == "not_run"


def test_invalid_coordinates_are_not_run_without_any_request() -> None:
    for lat, lon in ((math.nan, 10.0), (95.0, 10.0), (10.0, math.inf)):
        assert wikidata.check_wikidata(make_candidate(lat, lon))[0].status == "not_run"
    with pytest.raises(ValueError):
        wikidata.nearby_items(10.0, 10.0, radius_km=0.0)


def test_sparql_caches_replies_and_paces_live_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    stamps: list[float] = []
    seen_headers: list[dict[str, str]] = []

    def fake_get(url: str, params: dict[str, str], headers: dict[str, str], timeout: Any) -> FakeResponse:
        stamps.append(time.monotonic())
        seen_headers.append(headers)
        assert url == wikidata.ENDPOINT and params["format"] == "json" and timeout
        return FakeResponse(HTTPStatus.OK, {"results": {"bindings": [{"x": {"value": params["query"]}}]}})

    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(wikidata, "MIN_INTERVAL_S", 0.25)
    assert wikidata.sparql("Q-A")[0]["x"]["value"] == "Q-A"
    assert wikidata.sparql("Q-A")[0]["x"]["value"] == "Q-A"  # served from disk
    assert wikidata.sparql("Q-B")[0]["x"]["value"] == "Q-B"
    assert len(stamps) == 2 and stamps[1] - stamps[0] >= 0.24
    assert seen_headers[0]["User-Agent"].startswith("skywatch")


def test_check_wikidata_end_to_end_on_a_canned_reply(monkeypatch: pytest.MonkeyPatch) -> None:
    def binding(qid: str, dist: str, cls: str) -> dict[str, Any]:
        return {"item": {"value": "http://www.wikidata.org/entity/" + qid}, "itemLabel": {"value": "Big Pit"},
                "dist": {"value": dist}, "loc": {"value": "Point(1 2)"},
                "class": {"value": "http://www.wikidata.org/entity/Q820477"}, "classLabel": {"value": cls}}

    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse(
        HTTPStatus.OK, {"results": {"bindings": [binding("Q5", "0.8", "mine")]}}))
    result = wikidata.check_wikidata(make_candidate(2.0, 1.0))[0]
    assert result.status == "explains" and "Big Pit" in result.detail and result.evidence["searched_radius_km"] == 10.0


# ---------------------------------------------------------------- records: NTSB table

def test_dms_strings_and_compact_ntsb_table() -> None:
    assert records._dms_to_degrees("332739N") == pytest.approx(33.4608, abs=1e-4)
    assert records._dms_to_degrees("1120457W") == pytest.approx(-112.0825, abs=1e-4)
    assert math.isnan(records._dms_to_degrees("garbage")) and math.isnan(records._dms_to_degrees(None))
    events = {"ev_id": ["A", "B", "C", "D"], "ntsb_no": ["N1", "N2", "N3", "N4"],
              "ev_date": ["2020-05-01 00:00:00", "2021-06-02 00:00:00", "2019-01-01 00:00:00", "2022-01-01 00:00:00"],
              "dec_latitude": [35.0, None, None, 0.0], "dec_longitude": [-110.0, None, None, 0.0],
              "latitude": [None, "332739N", None, None], "longitude": [None, "1120457W", None, None],
              "ev_highest_injury": ["FATL", "NONE", "NONE", "NONE"], "inj_tot_f": [2, 0, 0, 0],
              "ev_city": ["Tuba City", "Phoenix", "Nowhere", "Null Island"], "ev_state": ["AZ", "AZ", "NV", None],
              "ev_country": ["USA", "USA", "USA", "XX"]}
    aircraft = {"ev_id": ["A", "A", "B"], "acft_make": ["Cessna", "Piper", "Bell"], "acft_model": ["172", "PA-28", "206"],
                "damage": ["SUBS", "DEST", "MINR"]}
    table, stats = records.ntsb_frame(events, aircraft)
    assert list(table.columns) == list(records.NTSB_COLUMNS)
    assert list(table["event_id"]) == ["A", "B"]  # C has no coordinates, D sits at (0, 0)
    assert stats["events"] == 4 and stats["events_with_coordinates"] == 2 and stats["dropped_no_coordinates"] == 2
    first = table.iloc[0]
    assert first["aircraft"] == "Cessna 172 / Piper PA-28" and first["damage"] == "DEST" and first["date"] == "2020-05-01"
    assert table.iloc[1]["latitude"] == pytest.approx(33.4608, abs=1e-4)


def ntsb_table(rows: list[dict[str, Any]]) -> pd.DataFrame:
    base = {"ntsb_no": "X1", "aircraft": "Cessna 172", "damage": "DEST", "injury_severity": "FATL", "fatalities": 1,
            "location": "Somewhere, NV", "country": "USA"}
    frame = pd.DataFrame([{**base, **row} for row in rows], columns=list(records.NTSB_COLUMNS))
    frame["day"] = pd.to_datetime(frame["date"]).dt.date
    return frame


@pytest.fixture
def fake_sources(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """One destroyed-aircraft accident at (38.0, -116.0) on 2021-07-10 and an empty Wikidata neighbourhood."""
    state: dict[str, Any] = {"wikidata": []}
    records._tables["ntsb"] = ntsb_table([
        {"event_id": "E1", "date": "2021-07-10", "latitude": 38.0, "longitude": -116.0},
        {"event_id": "E2", "date": "2015-01-01", "latitude": 38.3, "longitude": -116.0}])
    monkeypatch.setattr(wikidata, "nearby_items", lambda lat, lon, radius_km=10.0: list(state["wikidata"]))
    return state


def test_aviation_accident_explains_only_in_place_and_time(fake_sources: dict[str, Any]) -> None:
    near = (38.009, -116.0)  # 1.0 km north of the accident
    hit = records.check_aviation_accident(make_candidate(*near, "2021-07-01", "2021-08-15"))[0]
    assert (hit.check, hit.category, hit.status) == ("aviation_accident", "event", "explains")
    assert hit.evidence["matches"][0]["id"] == "E1" and hit.evidence["matches"][0]["distance_km"] == pytest.approx(1.0, abs=0.01)
    padded = records.check_aviation_accident(make_candidate(*near, "2021-07-25", "2021-08-15"))[0]
    assert padded.status == "explains"  # 15 days before the window: inside the 30-day pad
    wrong_time = records.check_aviation_accident(make_candidate(*near, "2023-07-01", "2023-08-15"))[0]
    assert wrong_time.status == "does_not_explain"
    assert wrong_time.evidence["nearest_record"]["id"] == "E1" and wrong_time.evidence["nearest_in_window"] is None
    assert "United States" in wrong_time.evidence["coverage"] and "weak evidence" in wrong_time.detail
    wrong_place = records.check_aviation_accident(make_candidate(38.05, -116.0, "2021-07-01", "2021-08-15"))[0]
    assert wrong_place.status == "does_not_explain" and wrong_place.evidence["nearest_in_window"]["id"] == "E1"
    undated = records.check_aviation_accident(make_candidate(*near))[0]
    assert undated.status == "inconclusive" and "no dated onset" in undated.detail


def test_aviation_lesser_severity_is_inconclusive_and_minor_is_ignored(fake_sources: dict[str, Any]) -> None:
    cand = make_candidate(38.009, -116.0, "2021-07-01", "2021-08-15")
    records._tables["ntsb"] = ntsb_table([{"event_id": "E1", "date": "2021-07-10", "latitude": 38.0, "longitude": -116.0,
                                           "damage": "SUBS", "injury_severity": "NONE", "fatalities": 0}])
    assert records.check_aviation_accident(cand)[0].status == "inconclusive"
    records._tables["ntsb"] = ntsb_table([{"event_id": "E1", "date": "2021-07-10", "latitude": 38.0, "longitude": -116.0,
                                           "damage": "MINR", "injury_severity": "NONE", "fatalities": 0}])
    result = records.check_aviation_accident(cand)[0]
    assert result.status == "does_not_explain" and result.evidence["records_in_radius"][0]["id"] == "E1"


def test_aviation_uses_wikidata_when_ntsb_is_missing_and_not_run_when_both_fail(
        fake_sources: dict[str, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    def no_ntsb(build: bool = True) -> pd.DataFrame:
        raise records.RecordsUnavailable("no table")

    monkeypatch.setattr(records, "load_ntsb", no_ntsb)
    fake_sources["wikidata"] = [item("Q111", "Flight 5735", "aviation_accident", 0.04, "2022-03-21", "day")]
    cand = make_candidate(23.324, 111.112, "2022-03-12", "2022-04-01")
    hit = records.check_aviation_accident(cand)[0]
    assert hit.status == "explains" and hit.evidence["sources_used"] == ["wikidata"] and "ntsb" in hit.evidence["sources_failed"]
    fake_sources["wikidata"] = []
    miss = records.check_aviation_accident(cand)[0]
    assert miss.status == "does_not_explain" and "NTSB table unavailable" in miss.evidence["coverage"]

    def no_wikidata(lat: float, lon: float, radius_km: float = 10.0) -> list[dict[str, Any]]:
        raise wikidata.WikidataError("down")

    monkeypatch.setattr(wikidata, "nearby_items", no_wikidata)
    dead = records.check_aviation_accident(cand)[0]
    assert dead.status == "not_run" and set(dead.evidence["sources_failed"]) == {"ntsb", "wikidata"}


# ---------------------------------------------------------------- records: meteorites

def meteorite_table() -> pd.DataFrame:
    frame = pd.DataFrame([
        {"name": "Testfall", "id": 1, "name_type": "Valid", "class": "H5", "mass": 3000.0, "fall": "Fell", "year": 2012.0,
         "lat": 40.0, "long": -117.0},
        {"name": "Bigiron", "id": 2, "name_type": "Valid", "class": "Iron", "mass": 2.0e6, "fall": "Found", "year": 1891.0,
         "lat": -25.0, "long": 130.0},
        {"name": "Pebble", "id": 3, "name_type": "Valid", "class": "L6", "mass": 40.0, "fall": "Found", "year": 1999.0,
         "lat": 10.0, "long": 10.0}])
    frame.attrs["coverage_end_year"] = 2013
    return frame


def test_meteorite_record_statuses() -> None:
    records._tables["meteorites"] = meteorite_table()
    fall_site = (40.009, -117.0)
    hit = records.check_meteorite(make_candidate(*fall_site, "2011-11-01", "2012-09-01"))[0]
    assert (hit.check, hit.category, hit.status) == ("meteorite_record", "event", "explains")
    assert hit.evidence["matches"][0]["name"] == "Testfall"
    old_window = records.check_meteorite(make_candidate(*fall_site, "2005-01-01", "2006-01-01"))[0]
    assert old_window.status == "does_not_explain" and old_window.evidence["nearest_record"]["name"] == "Testfall"
    # A window after the catalogue ends cannot be tested: not_run, never a pass.
    modern = records.check_meteorite(make_candidate(*fall_site, "2021-01-01", "2021-06-01"))[0]
    assert modern.status == "not_run" and "2013" in modern.detail and modern.evidence["catalogue_last_fall_year"] == 2013
    assert records.check_meteorite(make_candidate(-25.01, 130.0))[0].status == "inconclusive"  # undated, 2 t iron nearby
    assert records.check_meteorite(make_candidate(10.005, 10.0))[0].status == "does_not_explain"  # 40 g find is no cause
    assert records.check_meteorite(make_candidate(60.0, 60.0))[0].status == "does_not_explain"


def test_meteorite_table_unavailable_is_not_run(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    monkeypatch.setattr(records, "METEORITE_CSV", tmp_path / "missing.csv")

    def refused(*args: Any, **kwargs: Any) -> Any:
        raise requests.ConnectionError("refused")

    monkeypatch.setattr(requests, "get", refused)
    monkeypatch.setattr(records.time, "sleep", lambda s: None)
    result = records.check_meteorite(make_candidate(40.0, -117.0))[0]
    assert result.status == "not_run" and "unavailable" in result.detail
    assert not (tmp_path / "missing.csv").exists() and not (tmp_path / "missing.csv.part").exists()


# ---------------------------------------------------------------- records: ranges

REQUIRED_RANGE_WORDS = ("Baikonur Cosmodrome", "Baikonur downrange", "Altai", "Plesetsk drop", "Vostochny", "Kapustin Yar",
                        "Sary Shagan", "Jiuquan", "Taiyuan", "Xichang", "Wenchang", "Lop Nur", "Nevada Test and Training",
                        "Nevada National Security", "White Sands", "Dugway", "Edwards", "China Lake", "Vandenberg", "Woomera",
                        "Semipalatinsk", "Pokhran", "Reggane", "In Ekker", "Maralinga", "Novaya Zemlya", "Kwajalein")


def test_ranges_file_is_complete_and_marked_approximate() -> None:
    raw = json.loads(records.RANGES_PATH.read_text())
    entries = records.load_ranges()
    assert len(entries) == len(raw["entries"]) >= 60  # every curated entry passes validation
    names = " | ".join(e["name"] for e in entries)
    for word in REQUIRED_RANGE_WORDS:
        assert word in names, word
    assert all(e["approximate"] is True and e["kind"] in records.RANGE_KINDS and e["confidence"] in ("high", "medium", "low")
               and e["note"] for e in raw["entries"])
    assert "APPROXIMATE" in raw["geometry_note"]


def test_ranges_inside_outside_margin_and_cautions() -> None:
    inside = records.check_ranges(make_candidate(37.0, -116.05))[0]  # Yucca Flat, Nevada National Security Site
    assert (inside.check, inside.category, inside.status) == ("military_or_rocket_range", "infrastructure", "explains")
    assert "Nevada National Security Site" in inside.evidence["entry"]["name"]
    outside = records.check_ranges(make_candidate(20.5, 51.5))[0]  # Rub al Khali
    assert outside.status == "does_not_explain" and outside.evidence["nearest_entry"]["distance_to_edge_km"] > 100
    # 31 km from the NNSS circle centre (radius 28 km, margin 5.6 km), clear of the neighbouring circles.
    margin = records.check_ranges(make_candidate(36.98 - 31.0 / 111.2, -116.2))[0]
    assert margin.status == "inconclusive" and "uncertainty margin" in margin.detail
    diffuse = records.check_ranges(make_candidate(27.0, 108.4))[0]  # populated Xichang drop corridor
    assert diffuse.status == "inconclusive" and "shared with unrelated land use" in diffuse.detail
    low_conf = records.check_ranges(make_candidate(47.3, 67.0, signature="crash"))[0]  # Baikonur steppe drop zones
    assert low_conf.status == "inconclusive" and "low confidence" in low_conf.detail


def test_drop_zone_explains_only_impact_like_signatures(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    path = tmp_path / "ranges.json"
    path.write_text(json.dumps({"entries": [
        {"name": "Zone", "country": "X", "kind": "drop_zone", "lat": 0.0, "lon": 0.0, "radius_km": 30, "confidence": "medium"},
        {"name": "Broken", "country": "X", "kind": "picnic_area", "lat": 0.0, "lon": 0.0, "radius_km": 30},
        {"name": "NoRadius", "country": "X", "kind": "test_range", "lat": 0.0, "lon": 0.0}]}))
    monkeypatch.setattr(records, "RANGES_PATH", path)
    assert [e["name"] for e in records.load_ranges()] == ["Zone"]  # invalid entries are dropped, not guessed
    assert records.check_ranges(make_candidate(0.1, 0.1, signature="crash"))[0].status == "explains"
    assert records.check_ranges(make_candidate(0.1, 0.1, signature="installation"))[0].status == "inconclusive"


def test_ranges_file_missing_or_corrupt_is_not_run(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    monkeypatch.setattr(records, "RANGES_PATH", tmp_path / "absent.json")
    assert records.check_ranges(make_candidate(37.0, -116.05))[0].status == "not_run"
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    monkeypatch.setattr(records, "RANGES_PATH", bad)
    assert records.check_ranges(make_candidate(37.0, -116.05))[0].status == "not_run"


def test_invalid_coordinates_are_not_run_in_every_record_check() -> None:
    results = records.check_records(make_candidate(math.nan, math.nan))
    assert [r.check for r in results] == ["aviation_accident", "meteorite_record", "military_or_rocket_range"]
    assert all(r.status == "not_run" for r in results)


# ---------------------------------------------------------------- live data

@pytest.mark.network
def test_live_wikidata_mine_volcano_and_empty_desert() -> None:
    mine = wikidata.nearby_items(40.523, -112.151, 10.0)  # Bingham Canyon copper mine, Utah
    bingham = next(i for i in mine if i["qid"] == "Q2450901")
    assert bingham["category"] == "mine_or_quarry" and bingham["distance_km"] < 1.0
    assert wikidata.check_wikidata(make_candidate(40.523, -112.151))[0].status == "explains"
    etna = wikidata.check_wikidata(make_candidate(37.751, 14.994, signature="thermal"))[0]
    assert etna.status == "explains" and etna.evidence["explaining"][0]["explains_as"] == "volcano_or_geothermal"
    assert wikidata.nearby_items(20.5, 51.5, 10.0) == []  # Rub al Khali: nothing catalogued, and no error
    desert = wikidata.check_wikidata(make_candidate(20.5, 51.5))[0]
    assert desert.status == "does_not_explain" and desert.evidence["n_items"] == 0


@pytest.mark.network
def test_live_aviation_accident_china_eastern_5735_and_desert() -> None:
    site = (23.324, 111.112)
    hit = records.check_aviation_accident(make_candidate(*site, "2022-03-12", "2022-04-01"))[0]
    assert hit.status == "explains" and "5735" in hit.detail and hit.evidence["matches"][0]["date"] == "2022-03-21"
    year_before = records.check_aviation_accident(make_candidate(*site, "2020-03-12", "2020-04-01"))[0]
    assert year_before.status == "does_not_explain"
    desert = records.check_aviation_accident(make_candidate(20.5, 51.5, "2022-03-12", "2022-04-01"))[0]
    assert desert.status == "does_not_explain" and desert.evidence["records_in_radius"] == []
    assert "ntsb" in desert.evidence["sources_used"] and "weak evidence" in desert.evidence["coverage"]


@pytest.mark.network
def test_live_ntsb_table_matches_a_recorded_us_crash() -> None:
    table = records.load_ntsb()
    assert len(table) > 20000 and table["date"].min() < "2009" and table["date"].max() > "2025"
    row = table[(table["country"] == "USA") & (table["damage"] == "DEST") & (table["injury_severity"] == "FATL")
                & (table["date"] > "2020-01-01")].iloc[0]
    day = pd.Timestamp(row["date"])
    cand = make_candidate(float(row["latitude"]) + 0.005, float(row["longitude"]),
                          (day - pd.Timedelta(days=20)).date().isoformat(), (day + pd.Timedelta(days=20)).date().isoformat())
    result = records.check_aviation_accident(cand)[0]
    assert result.status == "explains" and row["event_id"] in [m["id"] for m in result.evidence["matches"]]


@pytest.mark.network
def test_live_meteorite_table_chelyabinsk() -> None:
    table = records.load_meteorites()
    assert len(table) > 30000 and table.attrs["coverage_end_year"] == 2013
    site = (54.81667, 61.11667)  # catalogue position of the 2013 Chelyabinsk fall
    assert records.check_meteorite(make_candidate(*site, "2013-01-20", "2013-03-01"))[0].status == "explains"
    assert records.check_meteorite(make_candidate(*site, "2022-01-20", "2022-03-01"))[0].status == "not_run"
    assert records.check_meteorite(make_candidate(20.5, 51.5, "2010-01-01", "2010-06-01"))[0].status == "does_not_explain"
