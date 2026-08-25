import numpy as np
import pandas as pd

from spring_river.hydro.postflood import (
    RECESSION_SKIP_DAYS,
    matched_comparison,
    paired_summary,
    post_event_baseflow,
)


def _data(n_years=12, seed=0):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2005-10-01", periods=365 * n_years, freq="D")
    q = np.full(len(dates), 400.0) + rng.normal(0, 10, len(dates))
    # flood year 2010: spike in April, then depressed base flow long enough to
    # cover the whole 6-month window that starts after the 30-day skip
    ev = pd.Timestamp("2010-04-15")
    i = np.searchsorted(dates, ev)
    q[i : i + 3] = 40000.0
    q[i + 3 : i + RECESSION_SKIP_DAYS + 200] = 250.0
    dv_q = pd.DataFrame({"date": dates, "value": q, "approved": True})
    basin = pd.DataFrame({"date": dates, "pcpn_in": 0.12})
    return dv_q, basin, pd.Series([ev])


def test_skip_is_30_days():
    assert RECESSION_SKIP_DAYS == 30


def test_post_event_baseflow_window():
    dv_q, _, ev = _data()
    out = post_event_baseflow(dv_q, ev, months=6)
    assert out.iloc[0]["post_days"] >= 150
    assert out.iloc[0]["post_baseflow_mean_cfs"] < 350


def test_matched_comparison_negative_diff_and_columns():
    dv_q, basin, ev = _data()
    cmp = matched_comparison(dv_q, basin, ev, months=6, k=3)
    assert len(cmp) == 1
    assert cmp.iloc[0]["diff_pct"] < -15
    assert "2010" not in cmp.iloc[0]["matched_years"]
    for col in ("pre_bf_cfs", "matched_pre_bf_cfs"):
        assert col in cmp.columns
        assert not np.isnan(cmp.iloc[0][col])
    # antecedent state before the flood was the undisturbed 400 cfs regime
    assert 300 < cmp.iloc[0]["pre_bf_cfs"] < 420
    assert 300 < cmp.iloc[0]["matched_pre_bf_cfs"] < 420


def test_matched_comparison_excludes_adjacent_years():
    dv_q, basin, ev = _data()
    cmp = matched_comparison(dv_q, basin, ev, months=6, k=3)
    years = cmp.iloc[0]["matched_years"].split(",")
    assert len(years) == 3
    assert not {"2009", "2010", "2011"} & set(years)


def test_matching_prefers_similar_antecedent_state():
    dv_q, basin, ev = _data()
    # make 2014 a low-antecedent year: base flow depressed in the 90 days before
    # the event's calendar date, so it should be the worst match on pre_bf
    lo = (dv_q["date"] >= "2014-01-15") & (dv_q["date"] < "2014-04-15")
    dv_q = dv_q.copy()
    dv_q.loc[lo, "value"] = 150.0
    cmp = matched_comparison(dv_q, basin, ev, months=6, k=3)
    assert "2014" not in cmp.iloc[0]["matched_years"].split(",")


def test_matched_comparison_leap_day_event():
    # window start lands on Feb 29 after the 30-day skip; candidate years must not raise
    dv_q, basin, _ = _data()
    ev = pd.Series([pd.Timestamp("2008-01-30")])
    cmp = matched_comparison(dv_q, basin, ev, months=6, k=3)
    assert len(cmp) == 1
    assert cmp.iloc[0]["matched_years"] != ""


def test_paired_summary_ci_and_unique_controls():
    cmp = pd.DataFrame(
        {
            "diff_pct": [-20.0, -25.0, -18.0, -30.0],
            "matched_years": ["2001,2002,2003", "2002,2003,2004", "2001,2004,2005", "2003,2004,2005"],
        }
    )
    s = paired_summary(cmp, n_boot=500)
    assert s["n"] == 4 and s["lo"] <= s["mean_diff_pct"] <= s["hi"] and s["hi"] < 0
    assert s["n_unique_controls"] == 5


def test_paired_summary_empty():
    s = paired_summary(pd.DataFrame({"diff_pct": [np.nan], "matched_years": [""]}), n_boot=10)
    assert s["n"] == 0 and np.isnan(s["mean_diff_pct"]) and s["n_unique_controls"] == 0
