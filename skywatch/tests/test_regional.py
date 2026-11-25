"""Region-wide recurrence of a change signature and its natural-process test."""
from skywatch.core.models import Candidate
from skywatch.eliminate import natural, regional


def _cand(i: int, year: int = 2022, kind: str = "step", detector: str = "optical_change",
          lon: float = 10.0, shape: dict | None = None, **vec) -> Candidate:
    m = {"kind": kind, "break_year": year, "d_brightness": -0.05, "d_ndvi": 0.2, "d_nbr": 0.0, "d_swir": -0.02}
    m.update(vec)
    return Candidate(id=f"c{i}", region_id="r", lat=20.0, lon=lon + i * 0.05, bbox=(0, 0, 1, 1),
                     signature="unknown", detector=detector, score=0.5, area_m2=2000, measurements=m, shape=shape)


def test_census_counts_same_year_same_direction_only():
    family = [_cand(i) for i in range(5)]
    other_year = _cand(5, year=2023)
    opposite = _cand(6, d_brightness=0.05, d_ndvi=-0.2)
    too_big = _cand(7, d_brightness=-0.2, d_ndvi=0.8)        # same direction, 4x the size
    event = _cand(8, detector="optical_event", kind="event_window")
    thermal = Candidate(id="t", region_id="r", lat=20, lon=10, bbox=(0, 0, 1, 1), signature="thermal",
                        detector="landsat_thermal", score=0.5, area_m2=1e5, measurements={"median_anomaly_K": 3})
    census = regional.annotate_siblings(family + [other_year, opposite, too_big, event, thermal])
    assert census["c0"]["count"] == 4 and census["c0"]["compared"] == 7
    assert set(census["c0"]["ids"]) == {"c1", "c2", "c3", "c4"}
    assert census["c0"]["spread_km"] > 15
    assert census["c5"]["count"] == 0 and census["c6"]["count"] == 0 and census["c7"]["count"] == 0
    assert "c8" not in census and "t" not in census
    assert "regional_siblings" not in event.measurements


def test_regional_pattern_explains_unless_outline_is_regular():
    family = [_cand(i) for i in range(5)]
    regional.annotate_siblings(family)
    result = natural._regional_pattern(natural._Context(family[0]))
    assert result.status == "explains" and "4 of 4" in result.detail

    pads = [_cand(i, shape={"rectangularity": 0.95, "straight_edge_fraction": 0.8}) for i in range(5)]
    regional.annotate_siblings(pads)
    assert natural._regional_pattern(natural._Context(pads[0])).status == "inconclusive"

    pair = [_cand(i) for i in range(3)]
    regional.annotate_siblings(pair)
    assert natural._regional_pattern(natural._Context(pair[0])).status == "inconclusive"
    alone = _cand(0)
    regional.annotate_siblings([alone, _cand(1, year=2019)])
    assert natural._regional_pattern(natural._Context(alone)).status == "does_not_explain"
    assert natural._regional_pattern(natural._Context(_cand(9))).status == "not_run"


def test_copy_census_matches_by_id():
    raw = [_cand(i) for i in range(5)]
    regional.annotate_siblings(raw)
    kept = [_cand(0), _cand(3), _cand(99)]
    assert regional.copy_census(raw, kept) == 2
    assert kept[0].measurements["regional_siblings"]["count"] == 4
    assert "regional_siblings" not in kept[2].measurements
