import numpy as np
import pandas as pd

from spring_river.hydro.lowflow import attribution_table, fit_attribution

COLUMNS = [
    "wy",
    "min7_cfs",
    "min7_end_date",
    "son_mean_cfs",
    "bfi",
    "p_trailing_in",
    "p_trailing_prev_in",
    "oni_trailing",
    "complete",
]


def _synthetic(n_years=30, seed=0):
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("1990-10-01")
    dates = pd.date_range(start, periods=365 * n_years, freq="D")
    # daily precip with real day-to-day variability; flow driven by the
    # trailing 365-day precip total (strictly antecedent), no time trend
    daily_p = rng.gamma(shape=0.5, scale=0.25, size=len(dates))
    trailing = pd.Series(daily_p).rolling(365, min_periods=1).sum().to_numpy()
    q = 200 + 10 * trailing + rng.normal(0, 5, len(dates))
    dv_q = pd.DataFrame({"date": dates, "value": q, "approved": True})
    basin = pd.DataFrame({"date": dates, "pcpn_in": daily_p})
    oni_dates = pd.date_range(start, periods=12 * n_years, freq="MS")
    oni = pd.DataFrame({"date": oni_dates, "anom": rng.normal(0, 0.8, len(oni_dates))})
    return dv_q, basin, oni


def test_attribution_table_columns_and_window_availability():
    dv_q, basin, oni = _synthetic()
    tbl = attribution_table(dv_q, basin, oni)
    assert list(tbl.columns) == COLUMNS
    assert tbl["min7_end_date"].notna().all()
    assert tbl["p_trailing_in"].notna().sum() >= 27
    # first WY: no 365 antecedent days of precip exist before its min7
    assert np.isnan(tbl.iloc[0]["p_trailing_in"])
    assert np.isnan(tbl.iloc[0]["p_trailing_prev_in"])


def test_predictors_are_strictly_antecedent_to_min7_window():
    dv_q, basin, oni = _synthetic()
    tbl = attribution_table(dv_q, basin, oni)
    row = tbl.dropna(subset=["p_trailing_in", "p_trailing_prev_in", "oni_trailing"]).iloc[3]
    end = pd.Timestamp(row["min7_end_date"])
    p = basin.set_index("date")["pcpn_in"]
    # the 7-day min7 window spans end-6 .. end; predictors must end at end-7
    last = end - pd.DateOffset(days=7)
    expected = p.loc[last - pd.DateOffset(days=364) : last].sum()
    assert abs(row["p_trailing_in"] - expected) < 1e-9
    prev_last = last - pd.DateOffset(days=365)
    expected_prev = p.loc[prev_last - pd.DateOffset(days=364) : prev_last].sum()
    assert abs(row["p_trailing_prev_in"] - expected_prev) < 1e-9
    o = oni.set_index("date")["anom"]
    last_m = end.replace(day=1) - pd.DateOffset(months=1)
    expected_oni = o.loc[last_m - pd.DateOffset(months=5) : last_m].mean()
    assert abs(row["oni_trailing"] - expected_oni) < 1e-9
    # nothing on or after the min7 end date can enter the predictors
    assert (o.loc[end.replace(day=1) :].index > last_m).all()


def test_complete_flag_requires_sep30():
    dv_q, basin, oni = _synthetic()
    tbl = attribution_table(dv_q, basin, oni)
    assert tbl["complete"].dtype == bool
    # 30*365 days from 1990-10-01 ends before 2020-09-30 (leap days), so the
    # last WY is incomplete; every interior WY reaches Sep 30.
    assert not tbl.iloc[-1]["complete"]
    assert tbl.iloc[1:-1]["complete"].all()


def test_precip_coverage_gate_marks_windows_nan():
    dv_q, basin, oni = _synthetic()
    before = attribution_table(dv_q, basin, oni)
    # knock out 123 days (> 10% of a 365-day window)
    gap_start, gap_end = pd.Timestamp("1994-10-01"), pd.Timestamp("1995-01-31")
    basin = basin.copy()
    basin.loc[(basin["date"] >= gap_start) & (basin["date"] <= gap_end), "pcpn_in"] = np.nan
    after = attribution_table(dv_q, basin, oni)
    touches = (after["min7_end_date"] > gap_start) & (
        after["min7_end_date"] <= gap_end + pd.DateOffset(days=2 * 365 + 1)
    )
    assert after.loc[touches, "p_trailing_in"].isna().any() or after.loc[
        touches, "p_trailing_prev_in"
    ].isna().any()
    untouched = after["min7_end_date"] <= gap_start
    pd.testing.assert_frame_equal(after[untouched], before[untouched])


def test_oni_gate_requires_min_months():
    dv_q, basin, oni = _synthetic()
    tbl = attribution_table(dv_q, basin, oni)
    end = pd.Timestamp(tbl.iloc[5]["min7_end_date"])
    last_m = end.replace(day=1) - pd.DateOffset(months=1)
    oni = oni.copy()
    kill = (oni["date"] <= last_m) & (oni["date"] > last_m - pd.DateOffset(months=3))
    oni.loc[kill, "anom"] = np.nan  # 3 of 6 months left -> below the 4-month floor
    tbl2 = attribution_table(dv_q, basin, oni)
    assert np.isnan(tbl2.iloc[5]["oni_trailing"])
    assert not np.isnan(tbl.iloc[5]["oni_trailing"])


def test_fit_recovers_positive_precip_effect_and_no_residual_trend():
    dv_q, basin, oni = _synthetic()
    tbl = attribution_table(dv_q, basin, oni)
    fit = fit_attribution(tbl)
    assert fit.coef["p_trailing_in"] > 0
    lo, hi = fit.ci["p_trailing_in"]
    assert lo > 0
    assert fit.residual_trend.slope_lo < 0 < fit.residual_trend.slope_hi
    assert fit.n >= 25
    assert 0 <= fit.r2 <= 1
    assert fit.min7_trend.n == fit.n


def test_fit_drops_incomplete_and_nan_rows():
    dv_q, basin, oni = _synthetic()
    tbl = attribution_table(dv_q, basin, oni)
    usable = tbl[tbl["complete"]].dropna(
        subset=["min7_cfs", "p_trailing_in", "p_trailing_prev_in", "oni_trailing"]
    )
    fit = fit_attribution(tbl)
    assert fit.n == len(usable)


def _tbl(wy, min7, p=None, prev=None, oni=None):
    """Minimal attribution-table stub."""
    import numpy as np
    import pandas as pd

    n = len(wy)
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "wy": wy, "min7_cfs": min7, "complete": True,
        "p_trailing_in": rng.normal(45, 5, n) if p is None else p,
        "p_trailing_prev_in": rng.normal(45, 5, n) if prev is None else prev,
        "oni_trailing": rng.normal(0, 0.6, n) if oni is None else oni,
    })


def test_ratio_series_drops_nonpositive_and_unmatched_years():
    import numpy as np

    from spring_river.hydro.lowflow import ratio_series

    a = _tbl([2001, 2002, 2003, 2004], [100.0, 110.0, 0.0, 130.0])
    b = _tbl([2002, 2003, 2004, 2005], [100.0, 100.0, 100.0, 100.0])
    s = ratio_series(a, b)
    assert list(s["wy"]) == [2002, 2004]          # 2001 unmatched, 2003 non-positive
    assert np.isclose(s.set_index("wy").loc[2002, "ratio"], 1.1)
    assert np.isclose(s.set_index("wy").loc[2002, "log_ratio"], np.log(1.1))


def test_ratio_trend_finds_a_divergence_the_shared_climate_cannot_explain():
    """Both series driven by one climate signal, but the numerator also gains
    2 %/yr of its own. The ratio must recover that, climate cancelled."""
    import numpy as np

    from spring_river.hydro.lowflow import ratio_trend

    wy = list(range(1990, 2020))
    climate = np.exp(np.random.default_rng(1).normal(0, 0.25, len(wy)))
    denom = 100 * climate
    numer = 50 * climate * np.exp(0.02 * (np.array(wy) - 1990))
    t, s = ratio_trend(_tbl(wy, numer), _tbl(wy, denom))
    assert abs(t.slope - 0.02) < 0.003
    assert t.slope_lo > 0                          # detected despite the shared noise
    assert len(s) == len(wy)


def test_precip_only_fit_drops_the_oni_term():
    from spring_river.hydro.lowflow import PRECIP_ONLY_PREDICTORS, fit_attribution_precip_only

    f = fit_attribution_precip_only(_tbl(list(range(1990, 2020)), [100.0] * 30))
    assert set(f.coef) == {"const", *PRECIP_ONLY_PREDICTORS}
    assert "oni_trailing" not in f.coef
    assert f.n == 30
