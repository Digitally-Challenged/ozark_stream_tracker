import numpy as np
import pytest
from scipy import stats

from spring_river.stats.trends import mann_kendall, pettitt, sen_slope, trend_test


def test_mann_kendall_monotone_increasing_is_positive_and_significant():
    x = np.arange(20, dtype=float)
    s, z, p = mann_kendall(x)
    assert s == 190  # n(n-1)/2 concordant pairs
    assert z > 0
    assert p < 0.001


def test_mann_kendall_constant_series_is_zero():
    s, z, p = mann_kendall(np.full(15, 3.0))
    assert s == 0
    assert z == 0
    assert p == 1.0


def test_mann_kendall_tie_correction_reduces_variance():
    # Known small example (Gilbert 1987 style): n=10 with ties
    x = np.array([1, 2, 2, 3, 3, 3, 4, 5, 5, 6], dtype=float)
    s, z, p = mann_kendall(x)
    # 45 pairs, 5 tied (one pair of 2s, three of 3s, one of 5s) -> 40 concordant
    assert s == 40
    # variance without ties would be 125; with ties it is smaller -> larger |z|
    assert z > (40 - 1) / np.sqrt(125)


def test_sen_slope_recovers_linear_slope():
    t = np.arange(30)
    x = 2.5 * t + 10
    slope, lo, hi, intercept = sen_slope(x, t)
    assert abs(slope - 2.5) < 1e-9
    assert lo <= slope <= hi
    assert abs(intercept - 10) < 1e-9


def test_sen_slope_ci_contains_true_slope_with_noise():
    rng = np.random.default_rng(1)
    t = np.arange(40)
    x = 0.8 * t + rng.normal(0, 3, 40)
    slope, lo, hi, _ = sen_slope(x, t)
    assert lo < 0.8 < hi
    assert lo < slope < hi


def test_sen_slope_matches_scipy_theilslopes():
    rng = np.random.default_rng(7)
    t = np.arange(35, dtype=float)
    x = 0.4 * t + rng.normal(0, 2, 35)
    slope, lo, hi, _ = sen_slope(x, t, alpha=0.05)
    ref = stats.theilslopes(x, t, alpha=0.95)
    assert slope == ref.slope
    assert lo == ref.low_slope
    assert hi == ref.high_slope


def test_trend_test_drops_nan_and_reports_n():
    x = np.array([1, 2, np.nan, 4, 5, 6, 7, 8, 9, 10], dtype=float)
    r = trend_test(x)
    assert r.n == 9
    assert r.slope > 0


def test_trend_test_requires_min_n():
    with pytest.raises(ValueError, match="n < 8"):
        trend_test(np.arange(5, dtype=float))


def test_pettitt_finds_step_change():
    x = np.concatenate([np.full(20, 10.0), np.full(20, 20.0)])
    r = pettitt(x)
    assert r.change_index == 19
    assert r.p < 0.01


def test_pettitt_no_change_is_not_significant():
    rng = np.random.default_rng(3)
    r = pettitt(rng.normal(size=60))
    assert r.p > 0.05
