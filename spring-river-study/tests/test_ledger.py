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
