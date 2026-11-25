"""Shape descriptors and the per-pixel step / transient statistics."""
import numpy as np

from skywatch.detect import optical_change as oc
from skywatch.detect import shape


def _disc(radius: int, size: int = 80) -> np.ndarray:
    yy, xx = np.mgrid[:size, :size]
    return (xx - size / 2) ** 2 + (yy - size / 2) ** 2 <= radius ** 2


def test_disc_is_circular_and_rectangle_is_rectilinear():
    disc = shape.describe_blob(_disc(20), 10.0)
    assert disc["circularity"] > 0.85
    assert abs(disc["equivalent_diameter_m"] - 400) < 25
    rect = np.zeros((80, 80), bool)
    rect[20:40, 10:70] = True
    r = shape.describe_blob(rect, 10.0)
    assert r["rectangularity"] > 0.9 and r["straight_edge_fraction"] > 0.6
    assert 2.5 < r["elongation"] < 3.6
    assert r["area_m2"] == 20 * 60 * 100


def test_ring_has_hole_fraction_and_tiny_blobs_do_not_raise():
    ring = _disc(20) & ~_disc(14)
    assert shape.describe_blob(ring, 10.0)["hole_fraction"] > 0.3
    for n in (0, 1, 3):
        tiny = np.zeros((5, 5), bool)
        tiny.flat[:n] = True
        assert shape.describe_blob(tiny, 10.0)["area_m2"] == n * 100


def test_find_rings_and_scars_on_synthetic_images():
    rng = np.random.default_rng(0)
    image = rng.normal(0, 0.01, (120, 120)).astype("float32")
    image[_disc(18, 120)] += 0.3
    image[5, 5] = np.nan
    rings = shape.find_rings(image, 10.0, 200, 600)
    assert rings and abs(rings[0]["diameter_m"] - 360) < 60
    assert abs(rings[0]["col"] - 60) < 4 and abs(rings[0]["row"] - 60) < 4
    flat = rng.normal(0, 0.01, (120, 120)).astype("float32")
    assert shape.find_rings(flat, 10.0, 200, 600) == []
    line = flat.copy()
    line[60:62, 10:110] += 0.3
    scars = shape.find_linear_scars(line, 10.0, 400)
    assert scars and scars[0]["length_m"] > 700 and scars[0]["polarity"] == 1
    assert shape.find_linear_scars(np.full((20, 20), np.nan, "float32"), 10.0, 100) == []


def test_classify_signature_rules():
    assert shape.classify_signature({}, {"origin": "thermal"}) == "thermal"
    scar = {"elongation": 5.0, "area_m2": 5000, "equivalent_diameter_m": 80}
    assert shape.classify_signature(scar, {"d_ndvi": -0.2}) == "crash"
    disc = {"circularity": 0.9, "equivalent_diameter_m": 120, "area_m2": 11000}
    assert shape.classify_signature(disc, {"d_ndvi": -0.1}) == "landing_trace"
    pad = {"rectangularity": 0.95, "straight_edge_fraction": 0.8, "area_m2": 40000}
    assert shape.classify_signature(pad, {"d_brightness": 0.1}) == "installation"
    assert shape.classify_signature({}, {}) == "unknown"


def test_season_window_wraps_new_year():
    assert oc.season_window(2020, ("06-01", "08-31")) == ("2020-06-01", "2020-08-31")
    assert oc.season_window(2020, ("12-01", "02-28")) == ("2020-12-01", "2021-02-28")


def _stack(years: int = 10, size: int = 40) -> np.ndarray:
    rng = np.random.default_rng(1)
    stack = np.empty((years, 4, size, size), "float32")
    for f, (level, noise) in enumerate(((0.3, 0.004), (0.1, 0.01), (0.05, 0.01), (0.35, 0.005))):
        stack[:, f] = level + rng.normal(0, noise, (years, size, size))
    return stack


def test_step_found_with_right_year_and_quiet_elsewhere():
    stack = _stack()
    stack[5:, 0, 10:20, 10:20] += 0.12          # persistent brightening from year index 5
    stats = oc.step_statistics(stack)
    patch = stats["step_z"][10:20, 10:20]
    assert (patch >= oc.Z_STEP).mean() > 0.95
    assert (stats["step_k"][10:20, 10:20] == 5).mean() > 0.95
    outside = np.ones((40, 40), bool)
    outside[10:20, 10:20] = False
    assert (stats["step_z"][outside] >= oc.Z_STEP).mean() < 0.01
    assert abs(float(np.median(stats["step_delta"][0][10:20, 10:20])) - 0.12) < 0.01


def test_first_year_oddity_is_not_a_step_or_transient():
    stack = _stack()
    stack[0, 0, 5:15, 5:15] += 0.15             # only the first year differs
    stats = oc.step_statistics(stack)
    assert (stats["step_z"][5:15, 5:15] >= oc.Z_STEP).mean() < 0.02
    assert (stats["trans_z"][5:15, 5:15] >= oc.Z_TRANSIENT).mean() < 0.02


def test_single_year_transient_and_nan_tolerance():
    stack = _stack()
    stack[4, 1, 25:32, 25:32] -= 0.4            # NDVI collapses in one year, then recovers
    stack[2, :, 0:3, 0:3] = np.nan
    stats = oc.step_statistics(stack)
    assert (stats["trans_z"][25:32, 25:32] >= oc.Z_TRANSIENT).mean() > 0.9
    assert (stats["trans_k"][25:32, 25:32] == 4).mean() > 0.9
    assert int(stats["n_valid"][0, 0]) == 9
    empty = oc.step_statistics(np.full((6, 4, 8, 8), np.nan, "float32"))
    assert float(empty["step_z"].max()) == 0.0


def test_earliest_significant_step_dates_the_event():
    stack = _stack()
    stack[3:, 2, 10:20, 10:20] -= 0.3          # burn index drops in year 3 and stays down
    stack[4:, 0, 10:20, 10:20] += 0.12         # brightness rises a year later (bigger z)
    stats = oc.step_statistics(stack)
    assert (stats["step_k"][10:20, 10:20] == 3).mean() > 0.95
