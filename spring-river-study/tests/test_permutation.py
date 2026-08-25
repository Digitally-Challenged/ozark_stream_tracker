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
    assert r.diff_lo <= r.diff <= r.diff_hi
    assert r.diff_hi == 1.0 - r.base_rate  # k == n -> upper bound exactly 1


def test_zero_successes_gives_lower_bound_of_minus_base_rate():
    # major years are never followed by a quiet year
    major = np.array([True, False] * 8)
    quiet = np.array([True, False] * 8)  # quiet only on major years themselves
    r = conditional_rate_test(major, quiet, n_perm=200, seed=3)
    assert r.rate_after_major == 0.0
    assert r.diff_lo == -r.base_rate
    assert r.diff_lo <= r.diff <= r.diff_hi


def test_no_pattern_is_not_significant():
    rng = np.random.default_rng(5)
    major = rng.random(60) < 0.25
    quiet = rng.random(60) < 0.3
    r = conditional_rate_test(major, quiet, n_perm=2000, seed=2)
    assert r.p > 0.05


def test_no_major_years_gives_nan_rate():
    r = conditional_rate_test(np.zeros(10, bool), np.ones(10, bool), n_perm=100)
    assert np.isnan(r.rate_after_major)


def test_conditional_rate_power_is_negligible_at_small_n_major():
    from spring_river.stats.permutation import conditional_rate_power

    p = conditional_rate_power(5, 19, 2 / 19, alt_rates=(0.2, 0.8), n_sim=800).set_index(
        "true_rate_given_major")
    assert p.loc[0.2, "power"] < 0.15         # a 2x effect is undetectable
    assert p.loc[0.8, "power"] > p.loc[0.2, "power"]


def test_conditional_rate_power_improves_with_more_major_years():
    from spring_river.stats.permutation import conditional_rate_power

    few = conditional_rate_power(5, 19, 0.1, alt_rates=(0.6,), n_sim=800)["power"].iloc[0]
    many = conditional_rate_power(40, 100, 0.1, alt_rates=(0.6,), n_sim=800)["power"].iloc[0]
    assert many > few
