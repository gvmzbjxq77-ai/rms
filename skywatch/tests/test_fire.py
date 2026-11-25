"""Tests for skywatch.eliminate.fire: synthetic MODIS archive, then live data."""
from __future__ import annotations

import shutil
from datetime import date, timedelta
from typing import Any

import numpy as np
import pytest

from skywatch.core import io
from skywatch.core.models import Candidate, CheckResult
from skywatch.eliminate import fire

LAT, LON = 40.10, -121.05          # inside the 2021 Dixie Fire scar (California)
TODAY = date(2026, 11, 24)


def _global_pixel(lat: float, lon: float, npix: int) -> tuple[int, int]:
    pix = fire._TILE_M / npix
    x = fire._R * np.radians(lon) * np.cos(np.radians(lat))
    y = fire._R * np.radians(lat)
    return int((x - fire._X_MIN) // pix), int((fire._Y_MAX - y) // pix)


class FakeModis:
    """In-memory stand-in for the two MODIS collections."""

    def __init__(self) -> None:
        self.burns: list[tuple[float, float, date]] = []
        self.fires: list[tuple[float, float, date, int, str]] = []
        self.missing_months: set[str] = set()
        self.failing_months: set[str] = set()
        self.ba_fill: int = 0
        self.af_fill: int = 5
        self.search_error: Exception | None = None
        self.fetches: list[str] = []
        self.searches: list[str] = []
        self.bboxes: list[tuple[float, ...]] = []

    def new_archive(self) -> None:
        """Forget cached blocks: the archive content is about to be replaced."""
        shutil.rmtree(fire._CACHE_DIR, ignore_errors=True)

    def search(self, product: Any, bbox: Any, start: date, end: date) -> list[dict[str, Any]]:
        if self.search_error is not None:
            raise self.search_error
        self.searches.append(product.collection)
        self.bboxes.append(tuple(bbox))
        west, south, east, north = bbox
        tiles = set()
        for lon, lat in ((west, south), (west, north), (east, south), (east, north)):
            col, row = _global_pixel(lat, lon, 1)
            tiles.add((col, row))
        out = []
        if product is fire._BA:
            for month in fire._months(start, end):
                if month.strftime("%Y-%m") in self.missing_months:
                    continue
                for h, v in tiles:
                    out.append(self._granule("MCD64A1", month, h, v, ("Burn_Date", "Burn_Date_Uncertainty")))
        else:
            day = date(start.year, 1, 1)
            while day <= end:
                if day + timedelta(days=7) >= start:
                    for name in ("MOD14A1", "MYD14A1"):
                        for h, v in tiles:
                            out.append(self._granule(name, day, h, v, ("FireMask",)))
                day += timedelta(days=8)
                if day.year != (day - timedelta(days=8)).year:
                    day = date(day.year, 1, 1)
        return out

    @staticmethod
    def _granule(name: str, first: date, h: int, v: int, assets: tuple[str, ...]) -> dict[str, Any]:
        gid = f"{name}.A{first.year}{first.timetuple().tm_yday:03d}.h{h:02d}v{v:02d}.061.2022001000000"
        return {"id": gid, "product": name, "first_day": first.isoformat(), "h": h, "v": v,
                "production": "2022001000000",
                "hrefs": {a: f"fake://{name}/{first.isoformat()}/{a}" for a in assets}}

    def fetch(self, href: str, npix: int, h: int, v: int, col_off: int, row_off: int,
              size: int) -> tuple[np.ndarray, list[str]]:
        self.fetches.append(href)
        _, _, name, first_text, asset = href.split("/")
        first = date.fromisoformat(first_text)

        def local(lat: float, lon: float) -> tuple[int, int] | None:
            col, row = _global_pixel(lat, lon, npix)
            r, c = row - v * npix - row_off, col - h * npix - col_off
            return (r, c) if 0 <= r < size and 0 <= c < size else None

        if name == "MCD64A1":
            if first.strftime("%Y-%m") in self.failing_months:
                raise RuntimeError("simulated read failure")
            if asset == "Burn_Date_Uncertainty":
                return np.full((1, size, size), 2, dtype="uint8"), []
            data = np.full((1, size, size), self.ba_fill, dtype="int16")
            for lat, lon, day in self.burns:
                where = local(lat, lon)
                if where and (day.year, day.month) == (first.year, first.month):
                    data[0][where] = day.timetuple().tm_yday
            return data, []
        days = [first + timedelta(days=i) for i in range(8)]
        data = np.full((8, size, size), self.af_fill, dtype="uint8")
        for lat, lon, day, cls, product in self.fires:
            where = local(lat, lon)
            if where and product == name and day in days:
                data[days.index(day)][where] = cls
        return data, [d.isoformat() for d in days]


@pytest.fixture
def modis(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> FakeModis:
    fake = FakeModis()
    monkeypatch.setattr(fire, "_search", fake.search)
    monkeypatch.setattr(fire, "_fetch_block", fake.fetch)
    monkeypatch.setattr(fire, "_CACHE_DIR", tmp_path / "fire")
    monkeypatch.setattr(fire, "_today", lambda: TODAY)
    monkeypatch.setattr(fire, "_measure_s2", lambda *args: None)
    return fake


def _candidate(lat: float = LAT, lon: float = LON, absent: str | None = "2021-07-10",
               present: str | None = "2021-07-30", **measurements: Any) -> Candidate:
    return Candidate(id="t1", region_id="r", lat=lat, lon=lon, bbox=io.point_bbox(lat, lon, 60.0),
                     signature="crash", detector="test", score=0.5, area_m2=8000.0,
                     absent_until=absent, present_from=present, measurements=dict(measurements))


def _by_name(results: list[CheckResult]) -> dict[str, CheckResult]:
    assert [r.check for r in results] == ["fire_history", "burn_spectral", "lightning"]
    assert [r.category for r in results] == ["event", "natural", "event"]
    return {r.check: r for r in results}


BURN: dict[str, Any] = {"d_nbr": -0.42, "d_ndvi": -0.30, "d_brightness": -0.04, "recovery_fraction": 0.3}


# ---------------------------------------------------------------- geometry

def test_footprint_matches_known_modis_pixel() -> None:
    # Verified against the real h08v04 file: this point is row 2387, col 1733.
    px = fire._footprint(40.05, -121.20, 250.0, 2400)
    inside = np.flatnonzero(px.dist == 0)
    assert inside.size == 1
    k = int(inside[0])
    assert (px.h[k], px.v[k], px.row[k], px.col[k]) == (8, 4, 2387, 1733)
    assert (px.dist <= 250).all() and 4 <= px.size <= 12


def test_footprint_distance_matches_brute_force_on_the_ground() -> None:
    # Sample every cell densely, convert to lon/lat and take the true nearest distance.
    lat, lon, npix = 55.0, 160.0, 1200                       # strong shear far from the central meridian
    pix = fire._TILE_M / npix
    px = fire._footprint(lat, lon, 4000.0, npix)
    steps = (np.arange(25) + 0.5) / 25
    for k in range(0, px.size, 7):
        x = fire._X_MIN + (px.h[k] * npix + px.col[k] + steps[None, :]) * pix
        y = fire._Y_MAX - (px.v[k] * npix + px.row[k] + steps[:, None]) * pix
        lats = np.degrees(y / fire._R) + 0 * x
        lons = np.degrees(x / (fire._R * np.cos(y / fire._R)))
        brute = float(fire._haversine(lat, lon, lats, lons).min())
        assert abs(brute - px.dist[k]) < 0.06 * pix + 0.01 * px.dist[k]


def test_footprint_grows_with_radius_and_survives_extremes() -> None:
    small, large = fire._footprint(-24.0, -69.0, 0.0, 2400), fire._footprint(-24.0, -69.0, 3000.0, 2400)
    assert small.size == 1 and small.dist[0] == 0.0          # the cell containing the point
    assert np.pi * 3000 ** 2 <= large.size * 463.31 ** 2 <= np.pi * (3000 + 2 * 463.31) ** 2
    for lat, lon in ((89.99, 10.0), (-89.99, -170.0), (0.0, 180.0), (0.0, -180.0)):
        px = fire._footprint(lat, lon, 1000.0, 1200)
        assert np.isfinite(px.dist).all() and (px.col >= 0).all() and (px.row < 1200).all()


# ------------------------------------------------------------------ survey

def test_survey_reports_burn_and_fire_at_point_only(modis: FakeModis) -> None:
    modis.burns = [(LAT, LON, date(2021, 7, 19)), (LAT, LON + 0.06, date(2021, 7, 20))]  # second is 5 km away
    modis.fires = [(LAT, LON, date(2021, 7, 20), 9, "MOD14A1"), (LAT, LON, date(2021, 7, 21), 7, "MYD14A1")]
    survey = fire.fire_survey(LAT, LON, 100.0, "2021-07-01", "2021-08-15")
    assert survey["burned_area"]["status"] == "ok" and survey["active_fire"]["status"] == "ok"
    assert survey["burned_area"]["months_read"] == 2 and survey["active_fire"]["days_covered"] == 46
    got = [(d["date"], d["product"], d["pixels"], d["confidence"]) for d in survey["detections"]]
    assert got == [("2021-07-19", "MCD64A1", 1, "high"), ("2021-07-20", "MOD14A1", 1, "high"),
                   ("2021-07-21", "MYD14A1", 1, "low")]
    assert all(d["distance_m"] < 700 for d in survey["detections"])
    assert survey["detections"][0]["date_uncertainty_days"] == 2.0
    assert fire.burn_history(LAT, LON, 100.0, "2021-07-01", "2021-08-15") == survey["detections"]


def test_survey_respects_period_and_radius(modis: FakeModis) -> None:
    modis.burns = [(LAT, LON, date(2021, 7, 19))]
    assert fire.burn_history(LAT, LON, 100.0, "2021-07-20", "2021-08-15") == []
    assert fire.burn_history(LAT, LON + 0.06, 100.0, "2021-07-01", "2021-08-15") == []
    assert len(fire.burn_history(LAT, LON + 0.06, 5500.0, "2021-07-01", "2021-08-15")) == 1


def test_block_cache_prevents_repeat_reads(modis: FakeModis) -> None:
    modis.burns = [(LAT, LON, date(2021, 7, 19))]
    first = fire.fire_survey(LAT, LON, 100.0, "2021-07-01", "2021-08-15")
    reads, searches = len(modis.fetches), len(modis.searches)
    assert reads > 0
    # A neighbouring candidate 2 km away shares the cached blocks and catalogue answers.
    again = fire.fire_survey(LAT, LON, 100.0, "2021-07-01", "2021-08-15")
    fire.fire_survey(LAT + 0.018, LON, 100.0, "2021-07-01", "2021-08-15")
    assert again == first and len(modis.fetches) == reads and len(modis.searches) == searches


def test_footprint_across_tile_boundary_reads_both_tiles(modis: FakeModis) -> None:
    # 40.0 N is the edge between tile rows v04 and v05; the burn lies just across it.
    modis.burns = [(39.9985, LON, date(2021, 7, 19))]
    survey = fire.fire_survey(40.0015, LON, 300.0, "2021-07-01", "2021-07-31", active_fire=False)
    assert survey["burned_area"]["status"] == "ok"
    assert [d["date"] for d in survey["detections"]] == ["2021-07-19"]
    assert {h.split("/")[3] for h in modis.fetches} == {"2021-07-01"} and len(modis.fetches) >= 2


def test_search_box_stays_on_the_globe(modis: FakeModis) -> None:
    # The live catalogue rejects boxes beyond 180 E or 90 S (seen as a 40 s retry storm).
    edge = fire.fire_survey(66.0, 179.999, 200.0, "2021-07-01", "2021-07-31")
    assert edge["burned_area"]["status"] == "ok" and edge["active_fire"]["status"] == "ok"
    fire.fire_survey(-90.0, 0.0, 200.0, "2021-07-01", "2021-07-31")           # must not raise
    assert modis.bboxes
    for west, south, east, north in modis.bboxes:
        assert -180 <= west < east <= 180 and -90 <= south < north <= 90


def test_survey_rejects_bad_arguments(modis: FakeModis) -> None:
    for args in ((float("nan"), LON, 100.0, "2021-07-01", "2021-08-01"),
                 (LAT, LON, -5.0, "2021-07-01", "2021-08-01"),
                 (LAT, LON, 100.0, "2021-08-01", "2021-07-01"),
                 (LAT, LON, 100.0, "July", "2021-08-01")):
        with pytest.raises(ValueError):
            fire.fire_survey(*args)


def test_long_period_skips_daily_product(modis: FakeModis) -> None:
    survey = fire.fire_survey(LAT, LON, 100.0, "2018-01-01", "2021-12-31")
    assert survey["active_fire"]["status"] == "skipped" and survey["burned_area"]["months_read"] == 48
    assert "modis-14A1-061" not in modis.searches


# ------------------------------------------------------------- failures

def test_network_failure_is_not_run_and_history_raises(modis: FakeModis) -> None:
    modis.search_error = RuntimeError("STAC search failed: proxy refused")
    survey = fire.fire_survey(LAT, LON, 100.0, "2021-07-01", "2021-08-15")
    assert survey["burned_area"]["status"] == survey["active_fire"]["status"] == "failed"
    with pytest.raises(RuntimeError, match="no MODIS fire product"):
        fire.burn_history(LAT, LON, 100.0, "2021-07-01", "2021-08-15")
    results = _by_name(fire.check_fire(_candidate(**BURN)))
    assert results["fire_history"].status == "not_run"
    assert results["burn_spectral"].status == "inconclusive"      # never "explains" on spectra alone
    no_window = _by_name(fire.check_fire(_candidate(absent=None, present=None)))
    assert no_window["fire_history"].status == "not_run"


@pytest.mark.parametrize("setup", ["failing", "missing", "unmapped"])
def test_incomplete_record_never_becomes_does_not_explain(modis: FakeModis, setup: str) -> None:
    if setup == "failing":
        modis.failing_months = {"2021-07"}
    elif setup == "missing":
        modis.missing_months = {"2021-07"}
    else:
        modis.ba_fill, modis.af_fill = -1, 4             # unmapped burned area under cloud
    survey = fire.fire_survey(LAT, LON, 100.0, "2021-06-25", "2021-08-14")
    assert survey["burned_area"]["status"] in ("partial", "no_coverage")
    history = _by_name(fire.check_fire(_candidate(**BURN)))["fire_history"]
    assert history.status == "inconclusive" and "incomplete" in history.detail


def test_unmapped_burned_area_needs_a_clear_active_fire_view(modis: FakeModis) -> None:
    modis.ba_fill = -1                                   # e.g. snow season: no burned-area mapping
    history = _by_name(fire.check_fire(_candidate(**BURN)))["fire_history"]
    assert history.status == "does_not_explain" and "unmapped" in history.detail
    assert history.evidence["active_fire"]["clear_days_by_month"] == {"2021-06": 6, "2021-07": 31, "2021-08": 14}
    modis.new_archive()
    modis.af_fill = 0                                    # and the daily product has no data either
    assert _by_name(fire.check_fire(_candidate(**BURN)))["fire_history"].status == "inconclusive"


def test_failed_reads_are_not_cached(modis: FakeModis) -> None:
    modis.failing_months = {"2021-07"}
    assert fire.fire_survey(LAT, LON, 100.0, "2021-07-01", "2021-07-31", active_fire=False)[
        "burned_area"]["status"] == "failed"
    modis.failing_months = set()
    modis.burns = [(LAT, LON, date(2021, 7, 19))]
    assert len(fire.burn_history(LAT, LON, 100.0, "2021-07-01", "2021-07-31")) == 1


# ---------------------------------------------------------------- checks

def test_fire_in_window_with_burn_spectra_explains(modis: FakeModis) -> None:
    modis.burns = [(LAT, LON, date(2021, 7, 19))]
    results = _by_name(fire.check_fire(_candidate(**BURN)))
    history = results["fire_history"]
    assert history.status == "explains" and "2021-07-19" in history.detail
    assert history.evidence["window"] == ["2021-06-25", "2021-08-14"]     # padded by 15 days
    assert results["burn_spectral"].status == "explains"
    assert results["lightning"].status == "not_run" and "lightning" in results["lightning"].detail


def test_fire_within_padding_counts_and_outside_does_not(modis: FakeModis) -> None:
    modis.burns = [(LAT, LON, date(2021, 8, 12))]                # 13 days after present_from
    assert _by_name(fire.check_fire(_candidate(**BURN)))["fire_history"].status == "explains"
    modis.new_archive()
    modis.burns = [(LAT, LON, date(2021, 5, 2))]                 # weeks before the window
    results = _by_name(fire.check_fire(_candidate(**BURN)))
    assert results["fire_history"].status == "does_not_explain"
    assert "25 hectares" in results["fire_history"].detail
    assert results["burn_spectral"].status == "inconclusive"
    assert "unproven" in results["burn_spectral"].detail


def test_active_fire_alone_explains_only_above_low_confidence(modis: FakeModis) -> None:
    modis.fires = [(LAT, LON, date(2021, 7, 20), 7, "MOD14A1")]
    assert _by_name(fire.check_fire(_candidate(**BURN)))["fire_history"].status == "inconclusive"
    modis.new_archive()
    modis.fires = [(LAT, LON, date(2021, 7, 20), 8, "MYD14A1")]
    assert _by_name(fire.check_fire(_candidate(**BURN)))["fire_history"].status == "explains"


def test_fire_record_with_contradicting_spectra_is_inconclusive(modis: FakeModis) -> None:
    modis.burns = [(LAT, LON, date(2021, 7, 19))]
    results = _by_name(fire.check_fire(_candidate(d_nbr=0.08, d_ndvi=0.02, d_brightness=0.09)))
    assert results["fire_history"].status == "inconclusive"
    assert results["burn_spectral"].status == "does_not_explain"


def test_no_fire_and_no_burn_spectra(modis: FakeModis) -> None:
    results = _by_name(fire.check_fire(_candidate(d_nbr=-0.01, d_ndvi=0.0, d_brightness=-0.06)))
    assert results["fire_history"].status == "does_not_explain"
    assert results["burn_spectral"].status == "does_not_explain"


def test_fire_without_any_spectral_measurement(modis: FakeModis) -> None:
    modis.burns = [(LAT, LON, date(2021, 7, 19))]
    results = _by_name(fire.check_fire(_candidate(d_nbr="n/a", d_ndvi=float("nan"))))
    assert results["fire_history"].status == "explains"
    assert "no spectral measurement" in results["fire_history"].detail
    assert results["burn_spectral"].status == "not_run"


def test_no_onset_window_gives_context_only(modis: FakeModis) -> None:
    modis.burns = [(LAT, LON, date(2021, 7, 19))]
    for absent, present in ((None, None), (None, "2021-07-30"), ("garbage", "2021-07-30")):
        results = _by_name(fire.check_fire(_candidate(absent=absent, present=present, **BURN)))
        assert results["fire_history"].status == "inconclusive"
        assert "2021-07-19" in results["fire_history"].detail
    assert "modis-14A1-061" not in modis.searches                # daily product not read for context


def test_window_outside_modis_record_and_swapped_dates(modis: FakeModis) -> None:
    future = _by_name(fire.check_fire(_candidate(absent="2027-01-01", present="2027-02-01")))
    assert future["fire_history"].status == "not_run"
    modis.burns = [(LAT, LON, date(2021, 7, 19))]
    swapped = _by_name(fire.check_fire(_candidate(absent="2021-07-30", present="2021-07-10", **BURN)))
    assert swapped["fire_history"].status == "explains"


def test_hostile_candidates_do_not_raise(modis: FakeModis) -> None:
    for lat, lon in ((float("nan"), LON), (LAT, float("inf")), (123.0, LON)):
        results = _by_name(fire.check_fire(_candidate(lat=lat, lon=lon)))
        assert {r.status for r in results.values()} == {"not_run"}
    weird = _candidate(**BURN)
    weird.bbox = (float("nan"), 0.0, 0.0, 0.0)
    weird.area_m2 = float("nan")
    weird.measurements["spectral"] = "not a dict"
    assert _by_name(fire.check_fire(weird))["fire_history"].status == "does_not_explain"
    assert fire._footprint_radius(weird) == 0.0
    huge = _candidate(**BURN)
    huge.bbox = (-180.0, -80.0, 180.0, 80.0)
    assert fire._footprint_radius(huge) == 5000.0


def test_burn_likeness_grades() -> None:
    assert fire.burn_likeness(-0.35, -0.2, -0.03)[0] == "burn_like"
    assert fire.burn_likeness(-0.06, -0.05, -0.01)[0] == "weak"
    assert fire.burn_likeness(None, -0.2)[0] == "weak"
    assert fire.burn_likeness(-0.35, -0.2, 0.08)[0] == "not_burn_like"      # clearing: bright soil
    assert fire.burn_likeness(-0.35, -0.2, -0.03, d_nir=0.05)[0] == "not_burn_like"
    assert fire.burn_likeness(0.2, 0.2)[0] == "not_burn_like"
    assert fire.burn_likeness(0.0, 0.0, -0.08)[0] == "not_burn_like"
    assert fire.burn_likeness(None, None, -0.2)[0] == "unknown"


# ------------------------------------------------- Sentinel-2 measurement

def _fake_composites(monkeypatch: pytest.MonkeyPatch, after_nir: float, late_nir: float = 0.30) -> None:
    def composite(grid: Any, start: str, end: str, bands: Any = (), **_: Any) -> dict[str, Any]:
        nir = 0.40 if start < "2021-07-11" else after_nir if start < "2022-01-01" else late_nir
        out: dict[str, Any] = {b: np.full(grid.shape, 0.08, dtype="float32") for b in bands}
        out["nir"] = np.full(grid.shape, nir, dtype="float32")
        out["swir22"] = np.full(grid.shape, 0.15, dtype="float32")
        out["dates"] = [start]
        return out
    monkeypatch.setattr(io, "s2_composite", composite)
    monkeypatch.setattr(fire, "_today", lambda: TODAY)


def test_measure_s2_detects_nbr_drop_and_recovery(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_composites(monkeypatch, after_nir=0.12)
    got = fire._measure_s2(_candidate(), 50.0, (date(2021, 7, 10), date(2021, 7, 30)))
    assert got is not None
    assert got["d_nbr"] == pytest.approx((0.12 - 0.15) / 0.27 - (0.40 - 0.15) / 0.55, abs=1e-4)
    assert got["d_nir"] == pytest.approx(-0.28, abs=1e-4) and got["d_ndvi"] < -0.3
    assert 0.5 < got["recovery_fraction"] < 0.9
    assert fire.burn_likeness(got["d_nbr"], got["d_ndvi"], got["d_brightness"], got["d_nir"])[0] == "burn_like"


def test_measure_s2_all_nan_or_missing_is_none(monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_composites(monkeypatch, after_nir=float("nan"))
    assert fire._measure_s2(_candidate(), 50.0, (date(2021, 7, 10), date(2021, 7, 30))) is None
    monkeypatch.setattr(io, "s2_composite", lambda *a, **k: None)
    assert fire._measure_s2(_candidate(), 50.0, (date(2021, 7, 10), date(2021, 7, 30))) is None
    # Before Sentinel-2 existed there is nothing to measure.
    assert fire._measure_s2(_candidate(), 50.0, (date(2010, 7, 10), date(2010, 7, 30))) is None


def test_sentinel_failure_becomes_not_run(modis: FakeModis, monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*args: Any) -> None:
        raise RuntimeError("STAC search failed")
    monkeypatch.setattr(fire, "_measure_s2", boom)
    results = _by_name(fire.check_fire(_candidate()))
    assert results["burn_spectral"].status == "not_run" and "failed" in results["burn_spectral"].detail
    assert results["fire_history"].status == "does_not_explain"


# -------------------------------------------------------------------- live

@pytest.mark.network
def test_live_dixie_fire_is_found_and_explains() -> None:
    """Dixie Fire, Plumas National Forest: ignited 2021-07-13, burned here in late July."""
    found = fire.burn_history(LAT, LON, 300.0, "2021-06-15", "2021-09-30")
    burned = [d for d in found if d["product"] == "MCD64A1"]
    active = [d for d in found if d["product"] in ("MOD14A1", "MYD14A1")]
    assert burned and all("2021-07-13" <= d["date"] <= "2021-08-31" for d in burned)
    assert len({d["date"] for d in active}) >= 3
    assert any(d["confidence"] == "high" for d in active)
    assert fire.burn_history(LAT, LON, 300.0, "2020-06-15", "2020-09-30") == []      # the year before
    candidate = _candidate(absent="2021-07-05", present="2021-09-25")                # no measurements
    results = _by_name(fire.check_fire(candidate))
    assert results["fire_history"].status == "explains"
    assert results["burn_spectral"].status == "explains"
    assert results["burn_spectral"].evidence["d_nbr"] < -0.2


@pytest.mark.network
def test_live_atacama_never_burned() -> None:
    """Hyper-arid Atacama core (24 S, 69 W): no fuel, no fire."""
    survey = fire.fire_survey(-24.0, -69.0, 500.0, "2019-01-01", "2020-12-31", active_fire=False)
    assert survey["burned_area"]["status"] == "ok" and survey["burned_area"]["months_read"] == 24
    assert survey["detections"] == []
    candidate = _candidate(lat=-24.0, lon=-69.0, absent="2022-01-10", present="2022-03-20",
                           d_nbr=-0.01, d_ndvi=0.0, d_brightness=-0.05)
    results = _by_name(fire.check_fire(candidate))
    assert results["fire_history"].status == "does_not_explain"
    assert results["fire_history"].evidence["active_fire"]["days_covered"] >= 90
    assert results["burn_spectral"].status == "does_not_explain"
    assert results["lightning"].status == "not_run"
