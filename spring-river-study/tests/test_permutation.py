import numpy as np

from spring_river.stats.permutation import conditional_rate_test


def test_strong_pattern_is_significant():
    # every major year followed by a quiet year; no other quiet years
    major = np.array([True, False] * 10)
    quiet = np.array([False, True] * 10)
    r = conditional_rate_test(major, quiet, n_perm=2000, seed=1)
    assert r.rate_after_major == 1.0
    assert r.diff > 0
    assert r.p < 0.05
    assert r.n_major == 10


def test_no_pattern_is_not_significant():
    rng = np.random.default_rng(5)
    major = rng.random(60) < 0.25
    quiet = rng.random(60) < 0.3
    r = conditional_rate_test(major, quiet, n_perm=2000, seed=2)
    assert r.p > 0.05


def test_no_major_years_gives_nan_rate():
    r = conditional_rate_test(np.zeros(10, bool), np.ones(10, bool), n_perm=100)
    assert np.isnan(r.rate_after_major)
