import numpy as np
import pandas as pd

from spring_river.climate.seasonal import circular_stats, peak_timing_by_period


def test_identical_dates_concentrate_on_apr_15():
    dates = pd.Series(pd.to_datetime([f"{y}-04-15" for y in range(2000, 2010)]))
    s = circular_stats(dates)
    assert s["n"] == 10
    # Leap years shift Apr 15 by one day-of-year, so R is ~0.99997, not exactly 1.
    assert s["R"] > 0.999
    assert abs(s["mean_doy"] - 105) < 1.0
    assert s["mean_date_label"] == "15 Apr"
    assert s["rayleigh_p"] < 0.01


def test_uniform_monthly_dates_are_not_concentrated():
    dates = pd.Series(pd.to_datetime([f"2005-{m:02d}-15" for m in range(1, 13)]))
    s = circular_stats(dates)
    assert s["n"] == 12
    assert s["R"] < 0.1
    assert s["rayleigh_p"] > 0.05


def test_dec_jan_straddle_averages_near_new_year():
    dates = pd.Series(pd.to_datetime(["2001-12-20", "2002-01-10", "2003-12-20", "2004-01-10"]))
    s = circular_stats(dates)
    # Mean of Dec 20 / Jan 10 wraps to ~Dec 31 / Jan 1, not July.
    assert s["mean_doy"] > 355 or s["mean_doy"] < 10
    assert s["R"] > 0.9


def test_too_few_dates_gives_nan_p():
    dates = pd.Series(pd.to_datetime(["2001-04-01", "2002-04-02"]))
    s = circular_stats(dates)
    assert s["n"] == 2
    assert np.isnan(s["rayleigh_p"])


def test_peak_timing_by_period_labels_and_all_row():
    dates = pd.Series(pd.to_datetime([f"{y}-04-15" for y in range(2008, 2028)]))
    out = peak_timing_by_period(dates, period_years=10)
    assert list(out.columns) == ["period", "n", "mean_doy", "mean_date_label", "R", "rayleigh_p"]
    assert list(out["period"]) == ["2008–2017", "2018–2027", "all"]
    assert list(out["n"]) == [10, 10, 20]
    assert out.iloc[-1]["n"] == 20


def test_peak_timing_by_period_explicit_start_year():
    dates = pd.Series(pd.to_datetime([f"{y}-05-01" for y in range(2003, 2012)]))
    out = peak_timing_by_period(dates, period_years=5, start_year=2000)
    assert list(out["period"]) == ["2000–2004", "2005–2009", "2010–2014", "all"]
    assert list(out["n"]) == [2, 5, 2, 9]


def _dates(center_doy, n, sd_days, seed):
    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(seed)
    base = pd.Timestamp("2001-01-01") + pd.Timedelta(days=center_doy - 1)
    return pd.Series(base + pd.to_timedelta(rng.normal(0, sd_days, n), "D"))


def test_watson_williams_does_not_reject_a_common_mean():
    from spring_river.climate.seasonal import watson_williams

    groups = [_dates(32, 12, 30, s) for s in range(4)]
    r = watson_williams(groups)
    assert r["k"] == 4 and r["N"] == 48
    assert r["p"] > 0.05


def test_watson_williams_rejects_clearly_separated_means():
    from spring_river.climate.seasonal import watson_williams

    groups = [_dates(1 + 60 * i, 12, 20, i) for i in range(4)]
    assert watson_williams(groups)["p"] < 0.01


def test_watson_williams_needs_two_usable_groups():
    import numpy as np
    import pandas as pd

    from spring_river.climate.seasonal import watson_williams

    r = watson_williams([_dates(32, 12, 30, 0), pd.Series(pd.to_datetime([]))])
    assert r["k"] == 1 and np.isnan(r["F"])


def test_circular_se_shrinks_with_n_and_concentration():
    from spring_river.climate.seasonal import circular_se_days

    assert circular_se_days(40, 0.5) < circular_se_days(10, 0.5)
    assert circular_se_days(10, 0.9) < circular_se_days(10, 0.5)
    assert 10 < circular_se_days(10, 0.5) < 60      # ~a month at decade-scale n
