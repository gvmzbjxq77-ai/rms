"""Tests for witness-report ingestion, seeded regions and report matching."""
from __future__ import annotations

import io as stdio
import re
import zipfile
from http import HTTPStatus
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

import numpy as np
import pandas as pd
import pytest
import requests

from skywatch.core import config
from skywatch.core.models import Candidate
from skywatch.reports import ingest


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _candidate(lat: float, lon: float, absent: str | None, present: str | None) -> Candidate:
    return Candidate(id="c1", region_id="r", lat=lat, lon=lon,
                     bbox=(lon - 0.01, lat - 0.01, lon + 0.01, lat + 0.01),
                     signature="landing_trace", detector="test", score=0.5,
                     absent_until=absent, present_from=present)


def _report(rid: str, when: str, lat: float | None, lon: float | None, text: str,
            source: str = "nuforc", country: str = "US", place: str = "Testville",
            precision: str = "day", klass: str | None = None,
            loc_km: float = 10.0) -> dict[str, Any]:
    return {"id": rid, "source": source, "source_file": source, "datetime": when,
            "date_precision": precision, "time_basis": "local", "lat": lat, "lon": lon,
            "location_precision_km": loc_km, "country": country, "place": place, "shape": "",
            "duration_s": None, "text": text, "official_class": klass,
            "official_identification": None, "tags": ingest.tag_text(text)}


@pytest.fixture()
def store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the module at an empty temporary data directory."""
    monkeypatch.setattr(ingest, "REPORTS_PATH", tmp_path / "reports.jsonl")
    monkeypatch.setattr(ingest, "SUMMARY_PATH", tmp_path / "summary.json")
    monkeypatch.setattr(ingest, "RAW_DIR", tmp_path / "raw")
    ingest._CACHE.clear()
    return tmp_path


def _write(rows: list[dict[str, Any]]) -> None:
    ingest.write_reports(pd.DataFrame(rows, columns=list(ingest._COLUMNS)))


def _xlsx(rows: list[list[str]]) -> bytes:
    """A minimal shared-strings workbook like the GEIPAN export."""
    strings: list[str] = []
    sheet = []
    for r, row in enumerate(rows, start=1):
        cells = []
        for c, value in enumerate(row):
            strings.append(value)
            cells.append(f'<c r="{chr(65 + c)}{r}" t="s"><v>{len(strings) - 1}</v></c>')
        sheet.append(f'<row r="{r}">{"".join(cells)}</row>')
    ns = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
    shared = "".join(f"<si><t>{escape(s)}</t></si>" for s in strings)
    buffer = stdio.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("xl/sharedStrings.xml", f"<sst {ns}>{shared}</sst>")
        archive.writestr("xl/worksheets/sheet1.xml",
                         f'<worksheet {ns}><sheetData>{"".join(sheet)}</sheetData></worksheet>')
    return buffer.getvalue()


GEIPAN_HEADER = ["ID Etude de Cas", "Titre du Cas", "Détails", "Année", "Identification",
                 "Classification", "Observation date", "Latitude", "Longitude", "Phenomenon",
                 "Region", "Type de cas"]


# --------------------------------------------------------------------------
# tag rules
# --------------------------------------------------------------------------

@pytest.mark.parametrize("text, expected", [
    ("Disc landed in the pasture and left three burn marks on the ground.",
     {"landing", "physical_trace"}),
    ("Object crashed into the woods, debris recovered by men in trucks.", {"crash_retrieval"}),
    ("Two small beings stood beside it; I felt paralyzed.", {"close_encounter"}),
    ("L'objet s'est posé dans un champ ; les gendarmes ont relevé des traces au sol et de "
     "l'herbe brûlée.", {"landing", "physical_trace"}),
    ("Un engin lumineux s'écrase dans la forêt.", {"crash_retrieval"}),
    # things the rules must NOT label
    ("Bright landing lights of a plane landing at the airport.", set()),
    ("We own 22 acres of open land and saw a light.", set()),
    ("Trois traces de condensation dans le ciel, un avion en phase d'atterrissage.", set()),
    ("It hovered, then left. No marks on the ground, it never landed.", set()),
    ("Aucune trace au sol n'a été relevée par la gendarmerie.", set()),
    ("Glowing object. ((NUFORC Note: Space debris crashed in the ocean. PD))", set()),
    ("Rentrée atmosphérique de débris spatial selon le GEIPAN.", set()),
    ("Trop long pour un flash de satellite ou de débris ; risque important de crash.", set()),
    ("We found metallic debris scattered in the field the next morning.", {"crash_retrieval"}),
    ("", set()),
])
def test_tag_rules_label_claims_and_respect_exclusions(text: str, expected: set[str]) -> None:
    assert set(ingest.tag_text(text)) == expected
    # the vectorised path used at build time must agree with the scalar path
    assert set(ingest._tag_series(pd.Series([text]))[0]) == expected


def test_tag_text_tolerates_non_text() -> None:
    assert ingest.tag_text(None) == []
    assert ingest._tag_series(pd.Series([None, np.nan, "landed"], dtype=object)) == [
        [], [], ["landing"]]


# --------------------------------------------------------------------------
# normalisers
# --------------------------------------------------------------------------

def test_normalise_planetsig_handles_dirty_rows() -> None:
    raw = pd.DataFrame([
        ["10/10/2013 24:00", "chester (uk/england)", "", "gb", "disk", "20", "20 s",
         "Disc landed&#44 left burn marks on the ground", "1/1/2014", "53.2", "-2.916667"],
        ["6/1/2012 21:15", "nowhere", "tx", "us", "light", "x", "", "light", "", "33q.20", "-97.1"],
        ["6/2/2012 21:15", "null island", "tx", "us", "light", "5", "", "light", "", "0", "0"],
        ["garbage", "x", "tx", "us", "", "", "", "", "", "30", "-97"],
    ], dtype=object)
    out = ingest.normalise_planetsig(raw)
    assert len(out) == 3                                   # the undated row is dropped
    first = out.iloc[0]
    assert first["datetime"] == "2013-10-11T00:00:00"      # 24:00 rolls into the next day
    assert first["place"] == "Chester" and first["country"] == "GB"
    assert first["text"] == "Disc landed, left burn marks on the ground"
    assert first["tags"] == ["landing", "physical_trace"]
    assert first["location_precision_km"] == ingest.PRECISION_CITY_KM
    assert np.isnan(out.iloc[1]["lat"]) and np.isnan(out.iloc[1]["location_precision_km"])
    assert np.isnan(out.iloc[2]["lat"]) and np.isnan(out.iloc[2]["lon"])   # 0,0 is no geocode
    assert out["id"].is_unique and out["id"].str.startswith("nuforc-").all()


def test_normalise_tidytuesday_joins_gazetteer_and_is_honest_about_big_cities() -> None:
    sightings = pd.DataFrame({
        "reported_date_time_utc": ["2019-07-08T02:10:00Z", "2020-01-01T00:00:00Z",
                                   "2021-03-03T03:03:00Z"],
        "city": ["Smalltown", "Metropolis", "Ghost Town"],
        "state": ["GA", "NY", "NV"], "country_code": ["US", "US", "NA"],
        "shape": ["disk", "NA", "orb"], "duration_seconds": ["60", "NA", "5"],
        "summary": ["It landed in a field", "NA", "orb"]})
    places = pd.DataFrame({
        "city": ["Smalltown", "Metropolis", "Metropolis"], "state": ["GA", "NY", "NY"],
        "country_code": ["US", "US", "US"], "latitude": ["33.8", "40.7", "40.7"],
        "longitude": ["-84.0", "-74.0", "-74.0"], "population": ["2000", "8000000", "8000000"]})
    out = ingest.normalise_tidytuesday(sightings, places)
    assert len(out) == 3
    small, big, ghost = out.iloc[0], out.iloc[1], out.iloc[2]
    assert small["datetime"] == "2019-07-08T02:10:00Z" and small["time_basis"] == "utc"
    assert small["location_precision_km"] == ingest.PRECISION_CITY_KM
    assert big["location_precision_km"] == ingest.PRECISION_BIG_CITY_KM
    assert big["text"] == "" and big["shape"] == "" and np.isnan(big["duration_s"])
    assert ghost["country"] == "NA"                        # Namibia's code is not "missing"
    assert np.isnan(ghost["lat"]) and np.isnan(ghost["location_precision_km"])


def test_geipan_xlsx_round_trip_keeps_partial_dates_and_classes() -> None:
    table = ingest.read_xlsx_table(_xlsx([
        GEIPAN_HEADER,
        ["2016-03-00001", "MARIGOT (LE) (972) 20.03.2016", "Traces d'herbes brûlées dans le champ.",
         "2016", "inconnu", "D", "20/03/2016", "14.82", "-61.03", "PAN D", "Outre-Mer",
         "Observation terrestre"],
        ["1947-08-00002", "LIEZ (85) --.08.1947", "Objet brillant.", "1947", "manque", "C",
         "--/08/1947", "46.37", "-0.7", "Manque", "Pays de la Loire", "Observation terrestre"],
        ["1937-01-00003", "[AERO] ORANGE (84) --.--.1937", "Globe.", "1937", "avion", "A",
         "--/--/1937", "44.14", "4.81", "Avion", "Autre", "Observation aéronautique"],
        ["", "SANS ID (01) 01.01.2000", "x", "2000", "", "B", "01/01/2000", "1", "1", "", "", ""],
        ["2001-01-00005", "SANS DATE (01)", "x", "2001", "", "B", "", "45", "1", "", "", ""],
    ]))
    assert list(table.columns) == GEIPAN_HEADER and len(table) == 5
    out = ingest.normalise_geipan(table)
    assert list(out["id"]) == ["geipan-2016-03-00001", "geipan-1947-08-00002",
                               "geipan-1937-01-00003"]
    assert list(out["date_precision"]) == ["day", "month", "year"]
    assert list(out["datetime"]) == ["2016-03-20", "1947-08-01", "1937-01-01"]
    assert list(out["official_class"]) == ["D", "C", "A"]
    assert list(out["place"]) == ["Le Marigot", "Liez", "Orange"]
    assert list(out["country"]) == ["FR", "FR", ""]
    assert list(out["location_precision_km"]) == [ingest.PRECISION_COMMUNE_KM] * 2 + [
        ingest.PRECISION_VEHICLE_KM]
    assert out.iloc[0]["tags"] == ["physical_trace"]


def test_xlsx_reader_rejects_dtd_and_missing_sheet() -> None:
    buffer = stdio.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("xl/worksheets/sheet1.xml",
                         '<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "b">]><worksheet/>')
    with pytest.raises(ValueError, match="DTD"):
        ingest.read_xlsx_table(buffer.getvalue())
    empty = stdio.BytesIO()
    with zipfile.ZipFile(empty, "w") as archive:
        archive.writestr("other.txt", "x")
    with pytest.raises(ValueError, match="no worksheet"):
        ingest.read_xlsx_table(empty.getvalue())


def test_dedupe_merges_utc_and_local_copies_of_one_report() -> None:
    text = "Silver disc landed beside the grain elevator for two minutes"
    older = ingest.normalise_planetsig(pd.DataFrame([
        ["7/7/2013 21:10", "smalltown", "ga", "us", "disk", "120", "", text, "", "33.8", "-84.0"],
        ["7/9/2013 21:10", "smalltown", "ga", "us", "disk", "120", "", text, "", "33.8", "-84.0"],
        ["7/7/2013 21:10", "smalltown", "ga", "us", "light", "5", "", "light", "", "33.8", "-84"],
    ], dtype=object))
    newer = ingest.normalise_tidytuesday(
        pd.DataFrame({"reported_date_time_utc": ["2013-07-08T01:10:00Z"], "city": ["Smalltown"],
                      "state": ["GA"], "country_code": ["US"], "shape": ["disk"],
                      "duration_seconds": ["120"], "summary": [text]}),
        pd.DataFrame({"city": ["Smalltown"], "state": ["GA"], "country_code": ["US"],
                      "latitude": ["33.8"], "longitude": ["-84.0"], "population": ["2000"]}))
    kept, removed = ingest._dedupe_nuforc(newer, older)
    assert removed == 1
    # the same words two days later are a different report; a 5-letter text is never a key
    assert list(kept["datetime"]) == ["2013-07-09T21:10:00", "2013-07-07T21:10:00"]


# --------------------------------------------------------------------------
# matching
# --------------------------------------------------------------------------

def _match_fixture() -> list[dict[str, Any]]:
    rows = [
        _report("near-in", "2020-05-10T22:00:00", 40.00, -100.00, "Disc landed in a field"),
        _report("near-edge", "2020-05-24", 40.10, -100.00, "light"),         # 7 days after
        _report("near-late", "2020-05-25", 40.10, -100.00, "light"),         # 8 days after
        _report("far", "2020-05-10", 44.50, -100.00, "Disc landed"),         # 500 km north
        _report("month-in", "2020-05-01", 40.05, -100.0, "light", precision="month"),
        _report("explained", "2020-05-10", 40.0, -100.0, "avion", source="geipan", klass="A"),
        _report("no-geocode", "2020-05-10", None, None, "landed"),
    ]
    # background so that the place counts as covered and has a reporting rate
    rows += [_report(f"bg{i}", f"20{16 + i % 7:02d}-01-15", 40.3, -100.2, "light")
             for i in range(8)]
    return rows


def test_match_reports_filters_by_distance_window_and_class(store: Path) -> None:
    _write(_match_fixture())
    cand = _candidate(40.0, -100.0, "2020-05-05", "2020-05-17")
    matches = ingest.match_reports(cand)
    assert [m["id"] for m in matches] == ["near-in", "near-edge"]
    first = matches[0]
    assert first["distance_km"] == 0.0 and first["tags"] == ["landing"]
    assert first["claim_status"] == "unverified witness report"
    assert first["location_precision_km"] == 10.0 and first["source"] == "nuforc"
    assert matches[1]["distance_km"] == pytest.approx(11.12, abs=0.05)
    # a month-precision report only matches when the whole month is inside the window
    wide = _candidate(40.0, -100.0, "2020-04-28", "2020-05-29")
    assert "month-in" in [m["id"] for m in ingest.match_reports(wide)]
    # 500 km away nothing matches; a larger radius does reach the far report
    away = _candidate(44.5, -106.3, "2020-05-05", "2020-05-17")
    assert ingest.match_reports(away) == []
    assert [m["id"] for m in ingest.match_reports(
        _candidate(44.0, -100.0, "2020-05-05", "2020-05-17"), radius_km=60.0)] == ["far"]


def test_match_reports_hostile_inputs(store: Path) -> None:
    _write(_match_fixture())
    assert ingest.match_reports(_candidate(40.0, -100.0, None, None)) == []
    assert ingest.match_reports(_candidate(40.0, -100.0, "2020-05-05", None)) == []
    assert ingest.match_reports(_candidate(40.0, -100.0, "not-a-date", "2020-05-17")) == []
    assert ingest.match_reports(_candidate(float("nan"), float("nan"),
                                           "2020-05-05", "2020-05-17")) == []
    assert ingest.match_reports(_candidate(40.0, -100.0, "2020-05-05", "2020-05-17"),
                                radius_km=0.0) == []
    # reversed window ends are tolerated
    assert len(ingest.match_reports(_candidate(40.0, -100.0, "2020-05-17", "2020-05-05"))) == 2


def test_match_reports_is_fast_on_a_large_table(store: Path) -> None:
    rng = np.random.default_rng(0)
    n = 60_000
    days = pd.Timestamp("2016-01-01") + pd.to_timedelta(rng.integers(0, 2500, n), unit="D")
    frame = pd.DataFrame({
        "id": [f"r{i}" for i in range(n)], "source": "nuforc", "source_file": "nuforc",
        "datetime": days.strftime("%Y-%m-%d"), "date_precision": "day", "time_basis": "local",
        "lat": rng.uniform(25, 49, n), "lon": rng.uniform(-124, -67, n),
        "location_precision_km": 10.0, "country": "US", "place": "X", "shape": "",
        "duration_s": np.nan, "text": "light", "official_class": None,
        "official_identification": None, "tags": [[] for _ in range(n)]})
    ingest.write_reports(frame)
    cand = _candidate(38.0, -95.0, "2019-01-01", "2019-03-01")
    ingest.match_reports(cand)                              # loads and indexes once
    import time
    start = time.perf_counter()
    for _ in range(200):
        ingest.match_reports(cand)
    assert (time.perf_counter() - start) / 200 < 0.02       # 20 ms budget per candidate
    truth = frame[(ingest._haversine_km(38.0, -95.0, frame["lat"].to_numpy(),
                                        frame["lon"].to_numpy()) <= 30.0)
                  & (frame["datetime"] >= "2018-12-25") & (frame["datetime"] <= "2019-03-08")]
    assert sorted(m["id"] for m in ingest.match_reports(cand)) == sorted(truth["id"])


def test_report_check_separates_no_report_from_could_not_look(store: Path) -> None:
    _write(_match_fixture())
    ran = ingest.report_check(_candidate(40.0, -100.0, "2020-05-05", "2020-05-17"))
    assert ran.status == "does_not_explain" and ran.category == "report"
    assert [m["id"] for m in ran.evidence["matches"]] == ["near-in", "near-edge"]
    assert 0.0 < ran.evidence["expected_by_chance"] < 1.0
    assert "nuforc" in ran.evidence["coverage"]
    # no onset window, no local coverage, or a window after the data ends: never a pass
    assert ingest.report_check(_candidate(40.0, -100.0, None, None)).status == "not_run"
    assert ingest.report_check(_candidate(-25.0, 130.0, "2020-05-05", "2020-05-17")
                               ).status == "not_run"
    assert ingest.report_check(_candidate(40.0, -100.0, "2026-01-01", "2026-02-01")
                               ).status == "not_run"


# --------------------------------------------------------------------------
# selection
# --------------------------------------------------------------------------

def _seed_fixture() -> list[dict[str, Any]]:
    return [
        _report("us1", "2019-07-07T23:00:00", 33.85, -84.02, "Disc landed and left burn marks "
                "on the ground", place="Snellville"),
        _report("us2", "2019-07-08", 33.86, -84.03, "It landed there too",
                place="Snellville"),                         # same site, weaker claim: skipped
        _report("us3", "2018-02-02", 41.0, -75.0, "Object crashed in the woods",
                place="St. Mary's / O'Brien"),
        _report("us-hoax", "2018-03-03", 35.0, -90.0, "Landed, burn marks on the ground. "
                "((NUFORC Note: Hoax. PD))", place="Hoaxville"),
        _report("us-old", "2012-03-03", 36.0, -91.0, "Landed, left burn marks on the ground",
                place="Oldtown"),
        _report("us-sky", "2019-01-01", 37.0, -92.0, "A light in the sky", place="Skytown"),
        _report("us-month", "2019-05-01", 38.0, -93.0, "Landed in a field", place="Vague",
                precision="month"),
        _report("fr1", "2016-12-20", 44.04, 5.94, "Traces d'herbes brûlées dans le champ",
                source="geipan", country="FR", place="Peyruis", klass="C", loc_km=5.0),
        _report("fr-a", "2017-01-01", 45.0, 5.0, "Un engin s'est posé dans un champ",
                source="geipan", country="FR", place="Explique", klass="A", loc_km=5.0),
        _report("gb1", "2020-09-08", 52.67, -2.45, "Heavy landing, bright light", country="GB",
                place="Telford"),
    ]


def test_landing_trace_reports_orders_by_location_precision(store: Path) -> None:
    _write(_seed_fixture())
    found = ingest.landing_trace_reports()
    assert set(found["id"]) == {"us1", "us2", "us3", "us-hoax", "us-month", "fr1", "fr-a", "gb1"}
    assert list(found["location_precision_km"]) == sorted(found["location_precision_km"])
    assert set(found["id"].iloc[:2]) == {"fr1", "fr-a"}
    assert "us-old" in set(ingest.landing_trace_reports(min_year=2010)["id"])
    assert list(ingest.landing_trace_reports(tags=("crash_retrieval",))["id"]) == ["us3"]


def test_seeded_regions_are_valid_spread_and_caveated(store: Path) -> None:
    _write(_seed_fixture())
    regions = ingest.seeded_regions(n=12, half_size_m=4000.0)
    by_report = {r.seed["report_id"]: r for r in regions}
    assert set(by_report) == {"us1", "us3", "fr1", "gb1"}   # hoax, A-class, vague, old: out
    assert [r.seed["report_id"] for r in regions][0] == "us1"            # strongest claim
    assert {r.seed["country"] for r in regions[:3]} == {"US", "FR", "GB"}  # spread first
    for number, region in enumerate(regions, start=1):
        assert re.fullmatch(rf"S{number:02d}-[A-Z0-9]+(?:-[A-Z0-9]+)*", region.id)
        assert region.kind == "seeded"
        west, south, east, north = region.bbox
        assert all(type(v) is float for v in region.bbox)
        assert west < region.seed["lon"] < east and south < region.seed["lat"] < north
        assert (north - south) * 111.32 == pytest.approx(8.0, rel=0.01)
        assert set(region.seed) >= {"source", "report_id", "datetime", "summary",
                                    "location_precision_km"}
        assert len(region.seed["summary"]) <= 300
        assert "may lie anywhere within" in region.notes and "unverified" in region.notes
    assert by_report["us3"].id.endswith("ST-MARY-S-O-BRIEN")
    assert by_report["us1"].season == ("07-07", "09-06")
    assert by_report["fr1"].season == ("12-20", "02-19")                 # wraps the new year
    assert ingest.seeded_regions(n=0) == []
    assert len(ingest.seeded_regions(n=2)) == 2


# --------------------------------------------------------------------------
# failure modes
# --------------------------------------------------------------------------

def test_empty_report_file_yields_empty_results_not_errors(store: Path) -> None:
    _write([])
    assert ingest.load_reports().empty
    assert ingest.landing_trace_reports().empty
    assert ingest.seeded_regions() == []
    cand = _candidate(40.0, -100.0, "2020-05-05", "2020-05-17")
    assert ingest.match_reports(cand) == []
    assert ingest.report_check(cand).status == "not_run"


def test_network_failure_is_reported_never_turned_into_no_reports(
        store: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(*args: Any, **kwargs: Any) -> Any:
        raise requests.ConnectionError("proxy refused")

    monkeypatch.setattr(ingest.requests, "get", refuse)
    monkeypatch.setattr(ingest.time, "sleep", lambda seconds: None)
    with pytest.raises(ingest.ReportsUnavailable):
        ingest.build(force=True)
    with pytest.raises(ingest.ReportsUnavailable):
        ingest.load_reports()
    cand = _candidate(40.0, -100.0, "2020-05-05", "2020-05-17")
    assert ingest.match_reports(cand) == []
    check = ingest.report_check(cand)
    assert check.status == "not_run" and "unavailable" in check.detail
    assert not ingest.REPORTS_PATH.exists()


def test_one_dead_source_is_recorded_and_the_rest_still_build(
        store: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    csv_text = ('7/7/2019 21:10,smalltown,ga,us,disk,120,2 min,'
                '"Disc landed, left burn marks on the ground",7/9/2019,33.8,-84.0\n')

    class Reply:
        def __init__(self, status: int, content: bytes) -> None:
            self.status_code, self.content = status, content

    def fake_get(url: str, **kwargs: Any) -> Reply:
        assert kwargs["headers"]["User-Agent"] == config.USER_AGENT and kwargs["timeout"]
        if "planetsig" in url:
            return Reply(HTTPStatus.OK, csv_text.encode())
        return Reply(HTTPStatus.NOT_FOUND, b"")

    monkeypatch.setattr(ingest.requests, "get", fake_get)
    monkeypatch.setattr(ingest.time, "sleep", lambda seconds: None)
    summary = ingest.build(force=True)
    assert summary["files"]["nuforc_planetsig_2014"]["status"] == "ok"
    assert summary["files"]["geipan"]["status"] == "failed"
    assert summary["files"]["nuforc_tidytuesday_2023"]["status"] == "failed"
    assert summary["total"] == 1 and summary["sources"]["nuforc"]["date_max"] == "2019-07-07"
    assert summary["tags"] == {"landing": 1, "physical_trace": 1, "crash_retrieval": 0,
                               "close_encounter": 0}
    assert "geipan" not in summary["sources"]
    assert ingest.build() == summary                        # second call: no network at all
    assert list(ingest.load_reports()["place"]) == ["Smalltown"]


def test_fetch_refuses_hosts_outside_the_allowlist(store: Path,
                                                   monkeypatch: pytest.MonkeyPatch) -> None:
    def explode(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("no request may be sent to a refused host")

    monkeypatch.setattr(ingest.requests, "get", explode)
    for url in ("https://nuforc.org/subndx/?id=all", "https://example.org/x.csv"):
        with pytest.raises(RuntimeError, match="not allowed"):
            ingest._fetch(url, store / "x", force=True)
    hosts = {requests.utils.urlparse(u).hostname for spec in ingest.SOURCE_FILES.values()
             for u in spec["parts"].values()}
    assert hosts <= set(config.ALLOWED_HOSTS) and not any("nuforc.org" in h for h in hosts)
    assert any("nuforc.org" in key for key in ingest.SOURCES_NOT_INGESTED)


# --------------------------------------------------------------------------
# live data
# --------------------------------------------------------------------------

@pytest.mark.network
def test_live_geipan_export_downloads_and_parses(tmp_path: Path) -> None:
    url = ingest.SOURCE_FILES["geipan"]["parts"]["geipan_export_cas.xlsx"]
    path = ingest._fetch(url, tmp_path / "geipan.xlsx", force=True)
    cases = ingest.normalise_geipan(ingest.read_xlsx_table(path.read_bytes()))
    assert len(cases) > 3000
    assert set(cases["official_class"].dropna()) == {"A", "B", "C", "D"}
    assert cases["datetime"].max() >= "2026-01-01" and cases["datetime"].min() < "1960"
    in_france = cases[cases["lat"].between(41, 51.5) & cases["lon"].between(-5.5, 9.8)]
    assert len(in_france) > 0.85 * len(cases)


@pytest.mark.network
def test_live_github_copies_are_reachable() -> None:
    for name in ("nuforc_planetsig_2014", "nuforc_tidytuesday_2023"):
        for url in ingest.SOURCE_FILES[name]["parts"].values():
            reply = requests.get(url, headers={"User-Agent": config.USER_AGENT,
                                               "Range": "bytes=0-2047"}, timeout=(15, 60))
            assert reply.status_code in (HTTPStatus.OK, HTTPStatus.PARTIAL_CONTENT), url
            assert len(reply.content) > 500


@pytest.mark.network
def test_live_build_then_match_a_real_report() -> None:
    summary = ingest.build()
    assert summary["sources"]["nuforc"]["count"] > 100_000
    assert summary["sources"]["nuforc"]["date_max"] >= "2023-05-01"
    assert summary["sources"]["geipan"]["count"] > 3000
    assert all(info["status"] == "ok" for info in summary["files"].values())
    recent = ingest.landing_trace_reports(min_year=2016)
    assert len(recent) >= 50 and (recent["date"].dt.year >= 2016).all()
    # GEIPAN case 2016-03 at Peyruis (class C): burnt-grass traces claimed in a field
    peyruis = recent[recent["place"] == "Peyruis"].iloc[0]
    assert peyruis["source"] == "geipan" and "physical_trace" in peyruis["tags"]
    here = _candidate(float(peyruis["lat"]), float(peyruis["lon"]), "2016-03-15", "2016-03-25")
    matches = ingest.match_reports(here)
    assert peyruis["id"] in [m["id"] for m in matches]
    assert matches[0]["distance_km"] < 1.0
    far = _candidate(float(peyruis["lat"]) + 4.5, float(peyruis["lon"]), "2016-03-15",
                     "2016-03-25")
    assert all(m["id"] != peyruis["id"] for m in ingest.match_reports(far))
    assert ingest.report_check(here).status == "does_not_explain"
    regions = ingest.seeded_regions()
    assert len(regions) == 12 and len({r.seed["country"] for r in regions}) >= 3
    assert all(re.fullmatch(r"S\d\d-[A-Z0-9-]+", r.id) and r.kind == "seeded" for r in regions)
