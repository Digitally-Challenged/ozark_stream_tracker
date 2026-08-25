import numpy as np
import pandas as pd

from spring_river.hydro.lowflow import attribution_table, fit_attribution

COLUMNS = [
    "wy",
    "min7_cfs",
    "son_mean_cfs",
    "bfi",
    "p_recharge_in",
    "p_recharge_prev_in",
    "oni_recharge",
    "complete",
]


def _synthetic(n_years=30, seed=0):
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("1990-10-01")
    dates = pd.date_range(start, periods=365 * n_years, freq="D")
    wy = dates.year + (dates.month >= 10).astype(int)
    precip_by_wy = {y: 15 + rng.normal(0, 3) for y in np.unique(wy)}
    # flow driven by that WY's recharge precip, no time trend
    q = np.array([200 + 10 * precip_by_wy[y] for y in wy]) + rng.normal(0, 5, len(dates))
    dv_q = pd.DataFrame({"date": dates, "value": q, "approved": True})
    daily_p = np.array(
        [
            precip_by_wy[y] / 182 if m in (9, 10, 11, 12, 1, 2) else 0.05
            for y, m in zip(wy, dates.month)
        ]
    )
    basin = pd.DataFrame({"date": dates, "pcpn_in": daily_p})
    oni_dates = pd.date_range(start, periods=12 * n_years, freq="MS")
    oni = pd.DataFrame({"date": oni_dates, "anom": rng.normal(0, 0.8, len(oni_dates))})
    return dv_q, basin, oni


def test_attribution_table_columns_and_precip_gate():
    dv_q, basin, oni = _synthetic()
    tbl = attribution_table(dv_q, basin, oni)
    assert list(tbl.columns) == COLUMNS
    assert tbl["p_recharge_in"].notna().sum() >= 28
    # first WY has no prior-year precip
    assert np.isnan(tbl.iloc[0]["p_recharge_prev_in"])


def test_complete_flag_requires_sep30():
    dv_q, basin, oni = _synthetic()
    tbl = attribution_table(dv_q, basin, oni)
    assert tbl["complete"].dtype == bool
    # 30*365 days from 1990-10-01 ends before 2020-09-30 (leap days), so the
    # last WY is incomplete; every interior WY reaches Sep 30.
    assert not tbl.iloc[-1]["complete"]
    assert tbl.iloc[1:-1]["complete"].all()


def test_precip_gate_marks_short_seasons_nan():
    dv_q, basin, oni = _synthetic()
    # knock out most of the WY 1995 recharge season (Sep 1994 - Feb 1995)
    mask = (basin["date"] >= "1994-10-01") & (basin["date"] <= "1995-01-31")
    basin.loc[mask, "pcpn_in"] = np.nan
    tbl = attribution_table(dv_q, basin, oni)
    row = tbl.set_index("wy")
    assert np.isnan(row.loc[1995, "p_recharge_in"])
    assert np.isnan(row.loc[1996, "p_recharge_prev_in"])
    assert not np.isnan(row.loc[1994, "p_recharge_in"])


def test_fit_recovers_positive_precip_effect_and_no_residual_trend():
    dv_q, basin, oni = _synthetic()
    tbl = attribution_table(dv_q, basin, oni)
    fit = fit_attribution(tbl)
    assert fit.coef["p_recharge_in"] > 0
    lo, hi = fit.ci["p_recharge_in"]
    assert lo > 0
    assert fit.residual_trend.slope_lo < 0 < fit.residual_trend.slope_hi
    assert fit.n >= 25
    assert 0 <= fit.r2 <= 1
    assert fit.min7_trend.n == fit.n


def test_fit_drops_incomplete_and_nan_rows():
    dv_q, basin, oni = _synthetic()
    tbl = attribution_table(dv_q, basin, oni)
    usable = tbl[tbl["complete"]].dropna(
        subset=["min7_cfs", "p_recharge_in", "p_recharge_prev_in", "oni_recharge"]
    )
    fit = fit_attribution(tbl)
    assert fit.n == len(usable)
