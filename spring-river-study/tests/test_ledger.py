import pandas as pd

from spring_river.hydro.ledger import build_ledger


def _one_wy_inputs():
    dates = pd.date_range("2019-10-01", "2020-09-30", freq="D")
    dv_q = pd.DataFrame({"date": dates, "value": 400.0, "approved": True})
    stage = pd.Series(5.0, index=range(len(dates)))
    stage.iloc[100:112] = 11.0  # 12 days >= 10 ft (and >= 8 ft)
    dv_stage = pd.DataFrame({"date": dates, "value": stage.values, "approved": True})
    peaks = pd.DataFrame(
        {
            "date": [pd.Timestamp("2020-01-15")],
            "peak_cfs": [22000.0],
            "gage_ht_ft": [11.2],
        }
    )
    pdates = pd.date_range("2019-01-01", "2020-12-31", freq="D")
    precip = pd.DataFrame({"date": pdates, "pcpn_in": 0.1})
    basin = pd.DataFrame({"date": pdates, "pcpn_in": 0.1})
    thresholds = {"action": 8.0, "minor": 10.0, "moderate": 14.0, "major": 16.0}
    return dv_q, dv_stage, peaks, precip, basin, thresholds


def test_ledger_one_water_year():
    ledger = build_ledger(*_one_wy_inputs())
    row = ledger[ledger["wy"] == 2020].iloc[0]
    assert row["peak_cfs"] == 22000.0
    assert row["peak_stage_ft"] == 11.2
    assert row["days_ge_8ft"] == 12
    assert row["days_ge_10ft"] == 12
    assert row["days_ge_14ft"] == 0
    assert row["min7_cfs"] == 400.0
    assert 0 < row["bfi"] <= 1
    # recharge season Sep 2019 - Feb 2020 = 182 days * 0.1
    assert abs(row["precip_recharge_in"] - 18.2) < 0.11
    # calendar 2020 station total = 366 * 0.1
    assert abs(row["precip_cal_in"] - 36.6) < 1e-6
    # 2020 is a leap year; all 366 calendar days have non-NaN pcpn_in
    assert row["precip_cal_days"] == 366
    # discharge runs through 2020-09-30 -> water year is complete
    assert row["complete"] == True


def test_ledger_missing_stage_yields_na_threshold_counts():
    dv_q, _dv_stage, peaks, precip, basin, thresholds = _one_wy_inputs()
    empty_stage = pd.DataFrame({"date": pd.Series([], dtype="datetime64[ns]"), "value": [], "approved": []})
    ledger = build_ledger(dv_q, empty_stage, peaks, precip, basin, thresholds)
    row = ledger[ledger["wy"] == 2020].iloc[0]
    assert pd.isna(row["days_ge_8ft"])
    assert pd.isna(row["days_ge_10ft"])
    assert pd.isna(row["days_ge_14ft"])
    assert pd.isna(row["days_ge_16ft"])


def test_ledger_partial_water_year_is_not_complete():
    dv_q, dv_stage, peaks, precip, basin, thresholds = _one_wy_inputs()
    cutoff = pd.Timestamp("2020-08-24")
    dv_q = dv_q[dv_q["date"] <= cutoff].reset_index(drop=True)
    dv_stage = dv_stage[dv_stage["date"] <= cutoff].reset_index(drop=True)
    ledger = build_ledger(dv_q, dv_stage, peaks, precip, basin, thresholds)
    row = ledger[ledger["wy"] == 2020].iloc[0]
    assert row["complete"] == False


def test_ledger_min7_window_spans_water_year_boundary():
    """C1: a per-WY-group min7 (old, buggy behavior) reindexes each WY's
    discharge to its own extent, so rolling(7, min_periods=7) can never
    produce a window ending on days 1-6 of that WY (no prior-WY days exist
    to fill the window). The whole-series min7 must be computed once before
    grouping so windows that end early in a WY but start in the prior WY are
    still considered, and are correctly assigned to the ENDING day's WY.

    Two consecutive water years (WY2020: Oct 2019-Sep 2020; WY2021: Oct
    2020-Sep 2021) with low flow 2020-09-28..2020-10-04 (7 days spanning the
    WY boundary). The window ending 2020-10-04 (all 7 low days) belongs to
    WY2021 and is lower than anything else in WY2021, so it must be
    WY2021's min7_cfs. Fails on the old per-WY-group implementation because
    that window straddles the WY2020/WY2021 boundary and never exists when
    each WY is reindexed independently.
    """
    dates = pd.date_range("2019-10-01", "2021-09-30", freq="D")
    values = pd.Series(400.0, index=dates)
    low_dates = pd.date_range("2020-09-28", "2020-10-04", freq="D")
    values.loc[low_dates] = 50.0
    dv_q = pd.DataFrame({"date": dates, "value": values.values, "approved": True})

    stage = pd.Series(5.0, index=range(len(dates)))
    dv_stage = pd.DataFrame({"date": dates, "value": stage.values, "approved": True})

    peaks = pd.DataFrame(
        {
            "date": pd.Series([], dtype="datetime64[ns]"),
            "peak_cfs": pd.Series([], dtype="float64"),
            "gage_ht_ft": pd.Series([], dtype="float64"),
        }
    )
    pdates = pd.date_range("2019-01-01", "2021-12-31", freq="D")
    precip = pd.DataFrame({"date": pdates, "pcpn_in": 0.1})
    basin = pd.DataFrame({"date": pdates, "pcpn_in": 0.1})
    thresholds = {"action": 8.0, "minor": 10.0, "moderate": 14.0, "major": 16.0}

    ledger = build_ledger(dv_q, dv_stage, peaks, precip, basin, thresholds)
    row_2021 = ledger[ledger["wy"] == 2021].iloc[0]
    # the 7-day window ending 2020-10-04 is entirely the low-flow days -> mean 50.0
    assert row_2021["min7_cfs"] == 50.0
