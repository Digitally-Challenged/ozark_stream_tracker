import numpy as np
import pandas as pd
import pytest

from spring_river.hydro.recession import (
    event_k_table,
    fit_k,
    master_recession,
    recession_segments,
)


def _frame(values, start="2020-01-01"):
    dates = pd.date_range(start, periods=len(values), freq="D")
    return pd.DataFrame({"date": dates, "value": values, "approved": True})


def _exp_recession(q0=5000.0, k=20.0, n=40):
    t = np.arange(n)
    return list(q0 * np.exp(-t / k))


def _event(k=20.0, n=60, base=300.0, lead=5):
    """Flat baseflow, then a peak with exponential recession."""
    return [base] * lead + _exp_recession(k=k, n=n)


def test_exponential_recession_recovers_k():
    segs = recession_segments(_frame(_event()), min_peak_cfs=1000)
    assert len(segs) == 1
    seg = segs[0]
    assert list(seg.columns) == ["date", "value", "t_days"]
    assert seg["t_days"].iloc[0] == 0
    assert seg["value"].iloc[0] == pytest.approx(5000.0)
    k, r2 = fit_k(seg)
    assert k == pytest.approx(20.0, abs=0.5)
    assert r2 > 0.99


def test_long_gap_splits_segments():
    v = _event() + [np.nan] * 20 + _event()
    segs = recession_segments(_frame(v), min_peak_cfs=1000)
    assert len(segs) == 2
    assert segs[0]["date"].iloc[0] == pd.Timestamp("2020-01-06")
    assert segs[1]["date"].iloc[0] == pd.Timestamp("2020-03-31")


def test_rise_over_max_rise_frac_ends_segment():
    rec = _exp_recession(n=20)
    v = [200.0] * 3 + rec + [rec[-1] * 1.5] + [100.0] * 3
    segs = recession_segments(_frame(v), min_peak_cfs=1000, min_days=5)
    assert len(segs) == 1
    assert len(segs[0]) == 20
    assert segs[0]["value"].iloc[-1] == pytest.approx(rec[-1])


def test_small_rise_within_tolerance_continues():
    rec = _exp_recession(n=15)
    v = [200.0] * 3 + rec + [rec[-1] * 1.01] + [rec[-1] * 0.9] * 4
    segs = recession_segments(_frame(v), min_peak_cfs=1000, min_days=5)
    assert len(segs) == 1
    assert len(segs[0]) == 20


def test_short_runs_dropped_and_small_peaks_ignored():
    v = [200.0] * 3 + _exp_recession(q0=500, n=30) + [200.0] * 3 + _exp_recession(n=5) + [10000.0] * 3
    segs = recession_segments(_frame(v), min_peak_cfs=1000, min_days=10)
    assert segs == []


def test_non_positive_value_ends_segment():
    v = [200.0] * 3 + _exp_recession(n=12) + [0.0] * 5
    segs = recession_segments(_frame(v), min_peak_cfs=1000, min_days=5)
    assert len(segs) == 1
    assert len(segs[0]) == 12
    assert (segs[0]["value"] > 0).all()


def test_fit_k_too_few_points_is_nan():
    seg = pd.DataFrame({"date": pd.date_range("2020-01-01", periods=6), "value": [5.0] * 6, "t_days": range(6)})
    k, r2 = fit_k(seg, skip_days=3)
    assert np.isnan(k) and np.isnan(r2)


def test_event_k_table_one_row_per_peak():
    v = _event(k=20) + _event(k=10, n=30)
    tbl = event_k_table(_frame(v), min_peak_cfs=1000)
    assert list(tbl.columns) == ["peak_date", "peak_cfs", "n_days", "k_days", "r2", "wy"]
    assert len(tbl) == 2
    assert tbl["peak_cfs"].tolist() == pytest.approx([5000.0, 5000.0])
    assert tbl["n_days"].tolist() == [60, 30]
    assert tbl["k_days"].tolist() == pytest.approx([20.0, 10.0], abs=0.5)
    assert (tbl["r2"] > 0.99).all()
    assert tbl["wy"].tolist() == [2020, 2020]
    assert tbl["peak_date"].iloc[0] == pd.Timestamp("2020-01-06")


def test_event_k_table_empty():
    tbl = event_k_table(_frame([100.0] * 30), min_peak_cfs=1000)
    assert tbl.empty
    assert list(tbl.columns) == ["peak_date", "peak_cfs", "n_days", "k_days", "r2", "wy"]


def test_master_recession_median_of_normalised_curves():
    segs = recession_segments(_frame(_event(k=20) + _event(k=10, n=30)), min_peak_cfs=1000)
    mrc = master_recession(segs, n_points=20)
    assert list(mrc.columns) == ["t_days", "ln_ratio_median", "ln_ratio_q25", "ln_ratio_q75", "n"]
    assert len(mrc) == 20
    assert mrc["t_days"].iloc[0] == 3  # skip_days default
    assert mrc["ln_ratio_median"].iloc[0] == pytest.approx(0.0)
    assert mrc["n"].iloc[0] == 2
    # at t=13 (10 days past skip): median of -10/20 and -10/10
    row = mrc.set_index("t_days").loc[13]
    assert row["ln_ratio_median"] == pytest.approx(-0.75, abs=1e-6)
    assert row["ln_ratio_q25"] <= row["ln_ratio_median"] <= row["ln_ratio_q75"]
    assert (mrc["ln_ratio_median"].diff().dropna() <= 0).all()


def test_master_recession_empty():
    mrc = master_recession([])
    assert mrc.empty
