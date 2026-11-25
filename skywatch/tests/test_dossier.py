"""Tests for evidence dossiers and the high-resolution viewing imagery."""
from __future__ import annotations

import io as stdio
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from PIL import Image

from skywatch.core import io
from skywatch.core.models import MANDATORY_CHECKS, Candidate, CheckResult
from skywatch.dossier import build, hires

BENBAN = (24.456, 32.739)

# --------------------------------------------------------------------------
# Fakes
# --------------------------------------------------------------------------

_RELEASES = [("WB_2014_R01", "2014-02-20", 10), ("WB_2016_R05", "2016-03-02", 20),
             ("WB_2018_R02", "2018-02-14", 30), ("WB_2020_R03", "2020-02-20", 40),
             ("WB_2022_R06", "2022-06-08", 50), ("WB_2024_R09", "2024-09-12", 60)]
_NUMS = [num for _, _, num in _RELEASES]
_COLOURS = [(200, 180, 120), (60, 120, 60), (40, 60, 160), (150, 40, 40), (90, 90, 90),
            (220, 220, 60), (20, 150, 150)]


def _capabilities() -> bytes:
    layers = "".join(
        f"<Layer><ows:Title>World Imagery (Wayback {day})</ows:Title>"
        f"<ows:Identifier>{ident}</ows:Identifier><Format>image/jpeg</Format>"
        f'<ResourceURL format="image/jpeg" resourceType="tile" template="https://wayback.'
        f"maptiles.arcgis.com/arcgis/rest/services/World_Imagery/WMTS/1.0.0/{{TileMatrixSet}}/"
        f'MapServer/tile/{num}/{{TileMatrix}}/{{TileRow}}/{{TileCol}}"/></Layer>'
        for ident, day, num in reversed(_RELEASES))  # the real document lists newest first
    return ('<?xml version="1.0"?><Capabilities xmlns="https://www.opengis.net/wmts/1.0" '
            'xmlns:ows="https://www.opengis.net/ows/1.1"><Contents>'
            f"{layers}</Contents></Capabilities>").encode()


def _jpeg(colour: tuple[int, int, int]) -> bytes:
    buffer = stdio.BytesIO()
    Image.new("RGB", (256, 256), colour).save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()


class FakeEsri:
    """Stands in for the Esri hosts: availability maps, tiles, releases, metadata."""

    def __init__(self, max_world_zoom: int = 15, versions: tuple[int, ...] = (0, 2, 3, 5),
                 same_pixels: dict[int, int] | None = None, change_record: bool = True) -> None:
        self.max_world_zoom = max_world_zoom
        self.versions = versions
        self.same_pixels = {3: 2} if same_pixels is None else same_pixels
        self.change_record = change_record
        self.tile_requests = 0

    def _effective(self, num: int) -> int | None:
        index = _NUMS.index(num)
        older = [v for v in self.versions if v <= index]
        return max(older) if older else None

    def __call__(self, url: str, params: dict[str, Any] | None = None) -> bytes:
        if url.endswith("WMTSCapabilities.xml"):
            return _capabilities()
        if url.endswith("/identify"):
            return json.dumps({"results": [{"layerId": 0, "attributes": {
                "DATE (YYYYMMDD)": "20250219", "RESOLUTION (M)": "0.31", "DESCRIPTION": "WV03",
                "SOURCE": "Vantor", "MinMapLevel": "12", "MaxMapLevel": "18"}}]}).encode()
        match = re.search(r"services\.arcgisonline\.com.*/tilemap/(\d+)/\d+/\d+/(\d+)/(\d+)$", url)
        if match:
            zoom, cols, rows = (int(g) for g in match.groups())
            return json.dumps({"data": [int(zoom <= self.max_world_zoom)] * (cols * rows)}).encode()
        match = re.search(r"services\.arcgisonline\.com.*/tile/(\d+)/\d+/\d+$", url)
        if match:
            self.tile_requests += 1
            return _jpeg(_COLOURS[int(match.group(1)) % len(_COLOURS)])
        match = re.search(r"wayback.*/tilemap/(\d+)/\d+/\d+/\d+$", url)
        if match:
            if not self.change_record:
                raise hires.HiresError("change record unreachable")
            index = _NUMS.index(int(match.group(1)))
            effective = self._effective(int(match.group(1)))
            if effective is None:
                return json.dumps({"data": [0]}).encode()
            record: dict[str, Any] = {"data": [1]}
            if effective != index:
                record["select"] = [_NUMS[effective]]
            return json.dumps(record).encode()
        match = re.search(r"wayback.*/tile/(\d+)/\d+/\d+/\d+$", url)
        if match:
            self.tile_requests += 1
            effective = self._effective(int(match.group(1)))
            if effective is None:
                raise hires.HiresError("HTTP 404")
            return _jpeg(_COLOURS[self.same_pixels.get(effective, effective)])
        raise AssertionError(f"unexpected request: {url}")


def _offline(url: str, params: dict[str, Any] | None = None) -> bytes:
    raise hires.HiresError(f"request failed: {url}: proxy refused")


@pytest.fixture
def esri(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> FakeEsri:
    fake = FakeEsri()
    monkeypatch.setattr(hires, "_http_get", fake)
    monkeypatch.setattr(hires, "CACHE_DIR", tmp_path / "cache")
    return fake


def _fake_composite(grid: io.Grid, start: str, end: str, **_: Any) -> dict[str, Any]:
    """Flat bright ground; from 2020 on a dark square sits in the middle."""
    height, width = grid.shape
    year = int(start[:4])
    base = (0.30 + 0.01 * np.random.default_rng(year).standard_normal((height, width))).astype("float32")
    out: dict[str, Any] = {band: base.copy() for band in io.S2_BANDS}
    out["nir"] = base + 0.05
    if year >= 2020:
        for band in io.S2_BANDS:
            out[band][height * 2 // 5:height * 3 // 5, width * 2 // 5:width * 3 // 5] = 0.08
    out["count"] = np.full((height, width), 4, dtype="uint8")
    out["dates"] = [f"{year}-06-01", f"{year}-08-15"]
    out["scene_ids"] = [f"S2A_FAKE_{year}0601_0_L2A", f"S2B_FAKE_{year}0815_0_L2A"]
    return out


def _candidate(**changes: Any) -> Candidate:
    lat, lon = 24.0, 32.0
    fields: dict[str, Any] = dict(
        id="blind-07/c0012", region_id="blind-07", lat=lat, lon=lon,
        bbox=io.point_bbox(lat, lon, 300.0), signature="crash", detector="optical_change",
        score=0.71, area_m2=41000.0, absent_until="2019-06-01", present_from="2020-03-01",
        sensors=["optical_s2"],
        measurements={"brightness_change": -0.21, "series": {
            "dates": ["2018-07-01", "2019-07-01", "2020-07-01", "2021-07-01"],
            "inside": {"brightness": [0.30, 0.30, 0.09, None], "ndvi": [0.08, 0.08, 0.02, 0.02],
                       "nbr": [0.0, 0.0, -0.1]},
            "ring": {"brightness": [0.30, 0.31, 0.30, 0.30], "ndvi": [0.08, 0.08, 0.08, 0.08],
                     "nbr": [0.0, 0.0, 0.0, 0.0]}}},
        checks=[
            CheckResult("osm_infrastructure", "infrastructure", "does_not_explain",
                        "No mapped feature within 500 m.", "OpenStreetMap API"),
            CheckResult("landcover", "natural", "inconclusive",
                        "Bare ground class; cannot tell quarrying from erosion.", "ESA WorldCover"),
            CheckResult("wikidata_nearby", "infrastructure", "not_run",
                        "Wikidata endpoint timed out after 3 tries.", "Wikidata"),
        ])
    fields.update(changes)
    return Candidate(**fields)


def _png_sizes(folder: Path) -> dict[str, int]:
    return {p.name: p.stat().st_size for p in folder.glob("*.png")}


# --------------------------------------------------------------------------
# hires: tile arithmetic, cap, cache, failure
# --------------------------------------------------------------------------

@pytest.mark.parametrize("lat,lon,size_m,cap", [(24.456, 32.739, 1200.0, 36), (64.1, -21.9, 800.0, 4),
                                                 (-33.9, 151.2, 3000.0, 9), (0.0, 0.0, 1200.0, 4)])
def test_zoom_choice_fills_the_tile_cap_without_exceeding_it(lat: float, lon: float,
                                                             size_m: float, cap: int) -> None:
    zoom = hires._zoom_for_cap(lat, lon, size_m, cap, hires.MAX_ZOOM)
    plan = hires._plan(lat, lon, size_m, zoom)
    assert 1 <= plan.n_tiles <= cap
    if zoom < hires.MAX_ZOOM:
        assert hires._plan(lat, lon, size_m, zoom + 1).n_tiles > cap
    # The requested point is the centre of the chip, to within a pixel.
    col, row = hires.chip_xy({"zoom": zoom, "origin_px": [plan.left, plan.top]}, lat, lon)
    assert abs(col - plan.size / 2) <= 1 and abs(row - plan.size / 2) <= 1
    assert plan.size * hires.ground_resolution(lat, zoom) == pytest.approx(size_m, rel=0.02, abs=20)


def test_zoom_choice_refuses_a_uselessly_coarse_chip() -> None:
    # (0, 0) is a tile corner at every zoom: one tile can never hold a chip centred there.
    with pytest.raises(hires.TileCapExceeded):
        hires._zoom_for_cap(0.0, 0.0, 1200.0, 1, hires.MAX_ZOOM)
    with pytest.raises(hires.TileCapExceeded):
        hires._zoom_for_cap(10.0, 10.0, 1200.0, 0, hires.MAX_ZOOM)


def test_hires_chip_uses_highest_zoom_with_real_imagery_and_caches(esri: FakeEsri) -> None:
    image, meta = hires.hires_chip(*BENBAN)
    # The cap alone would allow zoom 17; the availability map stops at 15.
    assert hires._zoom_for_cap(*BENBAN, 1200.0, hires.CHIP_TILE_CAP, hires.MAX_ZOOM) > 15
    assert meta["zoom"] == 15 and meta["imagery_verified"] is True
    assert image.shape == (meta["shape"][0], meta["shape"][1], 3) and image.dtype == np.uint8
    assert np.abs(image.reshape(-1, 3).mean(0) - np.array(_COLOURS[15 % len(_COLOURS)])).max() < 4
    assert meta["tiles"] <= hires.CHIP_TILE_CAP and esri.tile_requests == meta["tiles"]
    assert meta["ground_res_m"] == pytest.approx(4.35, abs=0.05)
    assert meta["acquisition_date"] == "2025-02-19" and meta["sensor"] == "WV03"
    assert "Esri" in meta["attribution"] and meta["source"].startswith("Esri World Imagery")
    west, south, east, north = meta["bbox"]
    assert west < BENBAN[1] < east and south < BENBAN[0] < north
    again, _ = hires.hires_chip(*BENBAN)
    assert esri.tile_requests == meta["tiles"], "second call must be served from the disk cache"
    assert np.array_equal(image, again)


def test_hires_chip_network_failure_raises_instead_of_returning_a_blank(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(hires, "_http_get", _offline)
    monkeypatch.setattr(hires, "CACHE_DIR", tmp_path / "cache")
    with pytest.raises(hires.HiresError):
        hires.hires_chip(*BENBAN)
    with pytest.raises(hires.HiresError):
        hires.wayback_series(*BENBAN)
    assert not list((tmp_path / "cache").rglob("*.jpg")), "a failed fetch must cache nothing"


def test_undecodable_tile_is_fatal_and_not_cached(esri: FakeEsri, monkeypatch: pytest.MonkeyPatch,
                                                  tmp_path: Path) -> None:
    def garbage(url: str, params: dict[str, Any] | None = None) -> bytes:
        return b"<html>blocked</html>" if "/tile/" in url else esri(url, params)
    monkeypatch.setattr(hires, "_http_get", garbage)
    with pytest.raises(hires.HiresError):
        hires.hires_chip(*BENBAN)
    assert not list((tmp_path / "cache" / "tiles").rglob("*.jpg"))


@pytest.mark.parametrize("lat,lon,size_m", [(float("nan"), 10.0, 1200.0), (95.0, 10.0, 1200.0),
                                            (10.0, 10.0, 0.0), (10.0, 10.0, float("inf"))])
def test_hires_rejects_invalid_input(esri: FakeEsri, lat: float, lon: float, size_m: float) -> None:
    with pytest.raises(ValueError):
        hires.hires_chip(lat, lon, size_m)
    with pytest.raises(ValueError):
        hires.wayback_series(lat, lon, size_m)


def test_tile_budget_is_a_hard_per_candidate_limit(esri: FakeEsri) -> None:
    with hires.tile_budget() as budget:
        hires.hires_chip(*BENBAN)
        hires.wayback_series(*BENBAN)
        assert budget.used == esri.tile_requests <= hires.MAX_TILES_PER_CANDIDATE == 60
    with hires.tile_budget(1) as budget:
        _, meta = hires.hires_chip(*BENBAN)
        assert meta["tiles"] == 1 and budget.remaining == 0
        with pytest.raises(hires.TileCapExceeded):
            hires.wayback_series(*BENBAN)
        with pytest.raises(hires.TileCapExceeded):
            hires.hires_chip(*BENBAN)
    with hires.tile_budget(10_000) as budget:
        assert budget.limit == hires.MAX_TILES_PER_CANDIDATE, "the limit can only be lowered"
    assert hires.CHIP_TILE_CAP + hires.SERIES_TILE_CAP <= hires.MAX_TILES_PER_CANDIDATE


# --------------------------------------------------------------------------
# hires: Wayback
# --------------------------------------------------------------------------

def test_wayback_releases_are_parsed_oldest_first(esri: FakeEsri) -> None:
    releases = hires.wayback_releases()
    assert [r["id"] for r in releases] == [ident for ident, _, _ in _RELEASES]
    assert [r["num"] for r in releases] == _NUMS
    first = releases[0]
    assert first["date"] == "2014-02-20" and "NOT the date the picture was taken" in first["date_meaning"]
    assert first["tile_url"].format(z=3, y=2, x=1).endswith("/default028mm/MapServer/tile/10/3/2/1")


def test_wayback_series_keeps_only_releases_with_new_pixels(esri: FakeEsri) -> None:
    series = hires.wayback_series(*BENBAN, n=6)
    # The tile changed in releases 0, 2, 3 and 5, but 3 republished the pixels of 2.
    assert [c["release_id"] for c in series] == ["WB_2014_R01", "WB_2018_R02", "WB_2024_R09"]
    assert [c["release_date"] for c in series] == sorted(c["release_date"] for c in series)
    for earlier, later in zip(series, series[1:]):
        assert not np.array_equal(earlier["image"], later["image"])
    for chip in series:
        assert "not the acquisition date" in chip["label"] and chip["release_date"] in chip["label"]
        assert chip["date_meaning"] == hires.RELEASE_DATE_MEANING
        assert chip["image"].ndim == 3 and chip["tiles"] * 6 <= hires.SERIES_TILE_CAP
    assert esri.tile_requests <= hires.SERIES_TILE_CAP


def test_wayback_series_without_change_record_samples_evenly_and_dedups(esri: FakeEsri) -> None:
    esri.change_record = False
    series = hires.wayback_series(*BENBAN, n=6)
    assert [c["release_id"] for c in series] == ["WB_2014_R01", "WB_2018_R02", "WB_2024_R09"]
    assert all("evenly spaced" in c["selection"] for c in series)
    assert esri.tile_requests <= hires.SERIES_TILE_CAP


def test_wayback_series_empty_when_no_release_has_imagery(esri: FakeEsri) -> None:
    esri.versions = ()
    assert hires.wayback_series(*BENBAN) == []
    assert hires.wayback_series(*BENBAN, n=0) == []


def test_spread_keeps_both_ends_and_never_repeats() -> None:
    dates = ["2014-01-01", "2014-02-01", "2014-03-01", "2019-01-01", "2023-12-01", "2024-01-01"]
    assert hires._spread(dates, 3) == [0, 3, 5]
    assert hires._spread(dates, 10) == list(range(6))
    assert hires._spread(dates, 1) == [5] and hires._spread([], 4) == []
    picked = hires._spread(["2020-01-01"] * 5 + ["2021-01-01"], 4)
    assert len(set(picked)) == 4 and picked == sorted(picked)


# --------------------------------------------------------------------------
# build: dossier contents
# --------------------------------------------------------------------------

def test_dossier_is_complete_and_auditable(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(build.io, "s2_composite", _fake_composite)
    candidate = _candidate()
    folder = build.build_dossier(candidate, out_dir=tmp_path, hires=False)
    assert folder == tmp_path / "blind-07_c0012", "the id must be made safe for a folder name"
    sizes = _png_sizes(folder)
    assert set(sizes) == {"before.png", "after.png", "falsecolor_before.png", "falsecolor_after.png",
                          "difference.png", "context.png", "timeseries.png"}
    assert max(sizes.values()) <= build.MAX_PNG_BYTES and min(sizes.values()) > 5000

    doc = json.loads((folder / "dossier.json").read_text())
    assert Candidate.from_json(doc["candidate"]) == candidate, "the full candidate must round-trip"
    assert [c["check"] for c in doc["checks"]] == [c.check for c in candidate.checks]
    assert {f["name"] for f in doc["files"]} == set(sizes) | {"dossier.md", "dossier.json"}
    assert all(len(f["sha256"]) == 64 for f in doc["files"] if f["name"] != "dossier.json")
    for phase in ("before", "after", "context"):
        record = doc["provenance"]["sentinel2"][phase]
        assert record["scene_ids"] and all(
            url.startswith("https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a/items/S2")
            for url in record["scene_urls"])
    assert doc["provenance"]["sentinel2"]["before"]["window"] == ["2018-06-01", "2019-06-01"]
    assert doc["provenance"]["sentinel2"]["after"]["window"][0] == "2020-03-01"
    zones = doc["statistics"]["footprint_vs_surroundings"]
    assert zones["after"]["inside"]["brightness"] < zones["before"]["inside"]["brightness"] - 0.05
    assert zones["after"]["surroundings"]["brightness"] == pytest.approx(
        zones["before"]["surroundings"]["brightness"], abs=0.02)
    assert {m["panel"] for m in doc["panels_missing"]} == {"hires.png", "wayback_strip.png"}

    # Checks that did not run are listed with their reason, and so is every
    # mandatory check that was never attempted.
    not_run = {item["check"]: item["reason"] for item in doc["checks_not_run"]}
    assert not_run["wikidata_nearby"] == "Wikidata endpoint timed out after 3 tries."
    assert set(not_run) == {"wikidata_nearby", "fire_history", "artefact_screen", "natural_process"}
    assert doc["tier"]["tier"] == "T1" and doc["closing_statement"] == build.CLOSING_STATEMENT

    text = (folder / "dossier.md").read_text()
    for check in candidate.checks:
        assert check.check in text and check.detail in text
    section = text.split("## Checks that were NOT run")[1].split("## Evidence tier")[0]
    for name in not_run:
        assert name in section
    tested = text.split("## Conventional explanations tested")[1].split("## Checks that were NOT run")[0]
    wikidata_line = next(line for line in tested.splitlines() if "wikidata_nearby" in line)
    assert "NOT RUN" in wikidata_line and "did not explain" not in wikidata_line
    assert "**T1**" in text and "seen in one sensor only" in text
    assert "24.00000 N, 32.00000 E" in text and "2019-06-01" in text and "2020-03-01" in text
    assert "not a probability" in text
    assert text.rstrip().endswith(build.CLOSING_STATEMENT)
    assert candidate.tier is None and len(candidate.sensors) == 1, "the candidate must not be modified"


def test_figures_show_the_feature_in_the_right_place(monkeypatch: pytest.MonkeyPatch,
                                                     tmp_path: Path) -> None:
    monkeypatch.setattr(build.io, "s2_composite", _fake_composite)
    folder = build.build_dossier(_candidate(), out_dir=tmp_path, hires=False)

    def centre_and_corner(name: str) -> tuple[float, float]:
        img = np.asarray(Image.open(folder / name).convert("L"), dtype="float32")
        height, width = img.shape
        # Axes occupy the middle of the canvas; sample its centre and a point well off it.
        return (float(img[int(height * 0.50) - 6:int(height * 0.50) + 6,
                          int(width * 0.50) - 6:int(width * 0.50) + 6].mean()),
                float(img[int(height * 0.30) - 6:int(height * 0.30) + 6,
                          int(width * 0.25) - 6:int(width * 0.25) + 6].mean()))

    before_centre, before_corner = centre_and_corner("before.png")
    after_centre, after_corner = centre_and_corner("after.png")
    assert after_centre < before_centre - 60, "the dark square must appear only after the onset"
    assert abs(after_corner - before_corner) < 12, "identical stretch: unchanged ground looks the same"


def test_candidate_without_onset_gets_a_single_current_view(monkeypatch: pytest.MonkeyPatch,
                                                            tmp_path: Path) -> None:
    monkeypatch.setattr(build.io, "s2_composite", _fake_composite)
    candidate = _candidate(id="thermal-1", signature="thermal", absent_until=None, present_from=None,
                           measurements={}, sensors=["thermal_landsat", "radar_s1"])
    folder = build.build_dossier(candidate, out_dir=tmp_path, hires=False)
    assert set(_png_sizes(folder)) == {"current.png", "falsecolor_current.png", "context.png"}
    doc = json.loads((folder / "dossier.json").read_text())
    assert doc["onset"]["dated"] is False and "current" in doc["provenance"]["sentinel2"]
    missing = {m["panel"]: m["reason"] for m in doc["panels_missing"]}
    assert "no dated onset" in missing["difference.png"] and "no time series" in missing["timeseries.png"]
    text = (folder / "dossier.md").read_text()
    assert "No dated onset" in text and "no dated onset window" in text
    thumb = build.thumbnail(candidate, tmp_path / "thumb" / "t.png", size_px=128)
    assert Image.open(thumb).size == (128, 128)


def test_dossier_completes_when_every_data_source_fails(monkeypatch: pytest.MonkeyPatch,
                                                        tmp_path: Path) -> None:
    monkeypatch.setattr(build.io, "s2_composite", _fake_composite)
    first = build.build_dossier(_candidate(), out_dir=tmp_path, hires=False)
    assert (first / "before.png").exists()

    def broken(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("STAC search failed for sentinel-2-l2a after 4 tries")
    monkeypatch.setattr(build.io, "s2_composite", broken)
    monkeypatch.setattr(hires, "_http_get", _offline)
    monkeypatch.setattr(hires, "CACHE_DIR", tmp_path / "cache")
    candidate = _candidate(measurements={"series": {"dates": ["2020-01-01"], "inside": {}, "ring": {}}})
    folder = build.build_dossier(candidate, out_dir=tmp_path, hires=True)
    assert folder == first and not _png_sizes(folder), "panels of the older build must be removed"
    doc = json.loads((folder / "dossier.json").read_text())
    missing = {m["panel"]: m["reason"] for m in doc["panels_missing"]}
    assert set(missing) == {"before.png", "falsecolor_before.png", "after.png", "falsecolor_after.png",
                            "difference.png", "context.png", "timeseries.png", "hires.png",
                            "wayback_strip.png"}
    assert "STAC search failed" in missing["before.png"] and "HiresError" in missing["hires.png"]
    assert "no finite value" in missing["timeseries.png"]
    assert {f["name"] for f in doc["files"]} == {"dossier.md", "dossier.json"}
    text = (folder / "dossier.md").read_text()
    assert "No Sentinel-2 composite could be read." in text
    assert all(f"`{panel}`" in text for panel in missing)
    assert text.rstrip().endswith(build.CLOSING_STATEMENT)
    # A failed data read must never be worded as a check that ruled something out.
    assert text.count("ran and did not explain") == 1


@pytest.mark.parametrize("composite", [
    lambda grid, start, end, **_: None,
    lambda grid, start, end, **_: {**{b: np.full(grid.shape, np.nan, "float32") for b in io.S2_BANDS},
                                   "count": np.zeros(grid.shape, "uint8"), "dates": [], "scene_ids": []},
])
def test_empty_or_all_nan_imagery_is_reported_not_drawn(monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
                                                        composite: Any) -> None:
    monkeypatch.setattr(build.io, "s2_composite", composite)
    folder = build.build_dossier(_candidate(), out_dir=tmp_path, hires=False)
    assert set(_png_sizes(folder)) == {"timeseries.png"}
    doc = json.loads((folder / "dossier.json").read_text())
    reasons = {m["panel"]: m["reason"] for m in doc["panels_missing"]}
    assert "Sentinel-2" in reasons["before.png"] and "Sentinel-2" in reasons["context.png"]
    thumb = build.thumbnail(_candidate(), tmp_path / "t.png")
    assert np.asarray(Image.open(thumb).convert("RGB"))[10, 10].tolist() == [128, 128, 128]


def test_dossier_before_the_sentinel2_record_and_bad_inputs(monkeypatch: pytest.MonkeyPatch,
                                                            tmp_path: Path) -> None:
    monkeypatch.setattr(build.io, "s2_composite", _fake_composite)
    nan = float("nan")
    candidate = _candidate(id="../odd id", absent_until="2009-05-01", present_from="2020-03-01",
                           bbox=(nan, nan, nan, nan), score=nan, tier="T3", tier_reason="claimed",
                           measurements={"ratio": np.float32(1.5), "bad": nan, "arr": np.arange(3)})
    folder = build.build_dossier(candidate, out_dir=tmp_path, hires=False)
    assert folder.parent == tmp_path and folder.name == "odd_id"
    assert "after.png" in _png_sizes(folder) and "before.png" not in _png_sizes(folder)
    raw = (folder / "dossier.json").read_text()
    assert "NaN" not in raw, "the record must be strict JSON"
    doc = json.loads(raw)
    reasons = {m["panel"]: m["reason"] for m in doc["panels_missing"]}
    assert "outside the Sentinel-2 record" in reasons["before.png"]
    assert "needs both" in reasons["difference.png"]
    assert doc["candidate"]["measurements"] == {"ratio": 1.5, "bad": None, "arr": [0, 1, 2]}
    # A recorded tier that the evidence does not support is flagged, not repeated blindly.
    assert doc["tier"]["tier"] == "T3" and doc["tier"]["recomputed_tier"] == "T1"
    assert doc["tier"]["consistent"] is False
    assert "Warning: recomputing the tier" in (folder / "dossier.md").read_text()


def test_dossier_with_hires_marks_esri_dates_as_publication_dates(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path, esri: FakeEsri) -> None:
    monkeypatch.setattr(build.io, "s2_composite", _fake_composite)
    candidate = _candidate()
    folder = build.build_dossier(candidate, out_dir=tmp_path, hires=True)
    sizes = _png_sizes(folder)
    assert {"hires.png", "wayback_strip.png"} <= set(sizes) and max(sizes.values()) <= build.MAX_PNG_BYTES
    doc = json.loads((folder / "dossier.json").read_text())
    record = doc["provenance"]["esri"]
    assert record["tiles_used"] == esri.tile_requests <= 60 and record["tile_limit"] == 60
    assert record["hires"]["acquisition_date"] == "2025-02-19"
    assert [w["release_id"] for w in record["wayback"]] == ["WB_2014_R01", "WB_2018_R02", "WB_2024_R09"]
    assert all("image" not in w for w in record["wayback"])
    text = (folder / "dossier.md").read_text()
    assert "NOT the dates on which the pictures were taken" in text
    assert "not counted as an independent sensor" in text
    assert candidate.sensors == ["optical_s2"], "viewing imagery must not add a sensor"


def test_thumbnail_is_a_bare_before_after_pair(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(build.io, "s2_composite", _fake_composite)
    path = build.thumbnail(_candidate(), tmp_path / "nested" / "thumb.png", size_px=320)
    img = np.asarray(Image.open(path).convert("RGB"), dtype="float32")
    assert img.shape == (320, 644, 3)
    assert img[:, 320:324].min() == 255, "white gap between the two halves"
    before, after = img[:, :320], img[:, 324:]
    assert after[150:170, 150:170].mean() < before[150:170, 150:170].mean() - 80
    assert abs(after[20:60, 20:60].mean() - before[20:60, 20:60].mean()) < 10
    assert path.stat().st_size < build.MAX_PNG_BYTES


def test_png_writer_holds_the_size_limit_and_keeps_outline_colours(tmp_path: Path) -> None:
    rng = np.random.default_rng(3)
    noise = rng.integers(0, 256, (900, 900, 3), dtype=np.uint8)
    noise[400:404, 100:800] = (255, 230, 0)
    size = build._save_png(Image.fromarray(noise), tmp_path / "noise.png", max_bytes=300_000)
    assert size == (tmp_path / "noise.png").stat().st_size <= 300_000
    # A thin yellow outline on busy terrain survives the palette reduction.
    terrain = (rng.normal(150, 25, (400, 400, 3))).clip(0, 255).astype(np.uint8)
    terrain[300:302, 100:350] = (255, 230, 0)
    build._save_png(Image.fromarray(terrain), tmp_path / "terrain.png", max_bytes=220_000)
    saved = Image.open(tmp_path / "terrain.png")
    assert saved.mode == "P" and saved.size == (400, 400), "palette alone must be enough here"
    assert np.asarray(saved.convert("RGB"))[300, 200].tolist() == [255, 230, 0]


# --------------------------------------------------------------------------
# Live data
# --------------------------------------------------------------------------

@pytest.mark.network
def test_live_wayback_release_list() -> None:
    releases = hires.wayback_releases()
    assert len(releases) >= 150 and releases[0]["date"] == "2014-02-20"
    assert [r["date"] for r in releases] == sorted(r["date"] for r in releases)
    assert len({r["num"] for r in releases}) == len(releases)


@pytest.mark.network
def test_live_hires_chip_land_versus_open_ocean() -> None:
    image, meta = hires.hires_chip(*BENBAN)
    assert meta["zoom"] >= 16 and meta["imagery_verified"] and meta["tiles"] <= hires.CHIP_TILE_CAP
    assert image.shape[0] >= 500 and float(image.std()) > 8.0, "real terrain has texture"
    assert meta["acquisition_date"] is None or re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta["acquisition_date"])
    # Known negative: no high-resolution imagery exists in the open South Pacific.
    try:
        _, ocean = hires.hires_chip(-40.0, -120.0)
    except hires.HiresError:
        return
    assert ocean["zoom"] < meta["zoom"]


@pytest.mark.network
def test_live_wayback_series_shows_different_imagery_over_time() -> None:
    series = hires.wayback_series(*BENBAN, n=4)
    assert 2 <= len(series) <= 4 and sum(c["tiles"] for c in series) <= hires.SERIES_TILE_CAP
    assert [c["release_date"] for c in series] == sorted(c["release_date"] for c in series)
    for earlier, later in zip(series, series[1:]):
        assert not np.array_equal(earlier["image"], later["image"])


@pytest.mark.network
def test_live_dossier_for_the_benban_solar_park(tmp_path: Path) -> None:
    lat, lon = BENBAN
    candidate = Candidate(
        id="validation-benban", region_id="validation", lat=lat, lon=lon,
        bbox=io.point_bbox(lat, lon, 1000.0), signature="installation", detector="hand-made",
        score=0.9, area_m2=4.0e6, absent_until="2018-01-01", present_from="2019-12-31",
        sensors=["optical_s2"])
    folder = build.build_dossier(candidate, out_dir=tmp_path, hires=True)
    sizes = _png_sizes(folder)
    assert {"before.png", "after.png", "falsecolor_before.png", "falsecolor_after.png",
            "difference.png", "context.png", "hires.png", "wayback_strip.png"} <= set(sizes)
    assert max(sizes.values()) <= build.MAX_PNG_BYTES
    doc = json.loads((folder / "dossier.json").read_text())
    s2 = doc["provenance"]["sentinel2"]
    assert all(d < "2018-01-02" for d in s2["before"]["acquisition_dates"])
    assert all(d >= "2019-12-31" for d in s2["after"]["acquisition_dates"])
    assert doc["provenance"]["esri"]["tiles_used"] <= 60
    # The panels were built over the south-west of the detail area; the
    # north-east stayed open desert. The thumbnail shares the stretch.
    thumb = np.asarray(Image.open(build.thumbnail(candidate, tmp_path / "thumb.png", 320)).convert("L"),
                       dtype="float32")
    before, after = thumb[:, :320], thumb[:, 324:]
    assert after[230:310, 10:150].mean() < 0.7 * before[230:310, 10:150].mean()
    assert abs(after[10:90, 230:310].mean() / before[10:90, 230:310].mean() - 1.0) < 0.15
