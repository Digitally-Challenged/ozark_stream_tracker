import numpy as np
import pandas as pd
import pytest

from spring_river.hydro.interarrival import antecedent_conditions, interarrival_test


def test_regular_cadence_rejects_exponential():
    dates = pd.Series(pd.to_datetime([f"{y}-04-01" for y in range(1980, 2024, 4)]))
    r = interarrival_test(dates, n_boot=500)
    assert r["n_events"] == 11
    assert abs(r["mean_gap_yr"] - 4.0) < 0.05
    assert r["cv"] < 0.1
    assert r["p_boot"] < 0.05


def test_poisson_cadence_is_consistent_with_exponential():
    rng = np.random.default_rng(0)
    gaps = rng.exponential(3.0, 40)
    dates = pd.Series(pd.Timestamp("1900-01-01") + pd.to_timedelta(np.cumsum(gaps) * 365.25, unit="D"))
    r = interarrival_test(dates, n_boot=500)
    assert r["p_boot"] > 0.05


def test_interarrival_is_deterministic_for_seed():
    dates = pd.Series(pd.to_datetime(["2000-01-01", "2003-05-01", "2004-02-01", "2009-09-01", "2011-01-01"]))
    a = interarrival_test(dates, n_boot=200, seed=3)
    b = interarrival_test(dates, n_boot=200, seed=3)
    assert a == b


def test_interarrival_requires_three_events():
    with pytest.raises(ValueError):
        interarrival_test(pd.Series(pd.to_datetime(["2000-01-01", "2004-01-01"])))


def test_antecedent_conditions_windows():
    d = pd.date_range("2019-10-01", periods=400, freq="D")
    dv_q = pd.DataFrame({"date": d, "value": 300.0, "approved": True})
    basin = pd.DataFrame({"date": d, "pcpn_in": 0.1})
    out = antecedent_conditions(dv_q, basin, pd.Series([pd.Timestamp("2020-06-01")]))
    assert list(out.columns) == ["event_date", "bfi_prior", "precip_prior_in", "baseflow_prior_cfs"]
    assert abs(out.iloc[0]["precip_prior_in"] - 3.0) < 1e-9
    assert 0 < out.iloc[0]["bfi_prior"] <= 1
    assert 0 < out.iloc[0]["baseflow_prior_cfs"] <= 300.0


def test_antecedent_conditions_nan_when_no_flow_in_window():
    d = pd.date_range("2019-10-01", periods=400, freq="D")
    dv_q = pd.DataFrame({"date": d, "value": 300.0, "approved": True})
    basin = pd.DataFrame({"date": d, "pcpn_in": 0.1})
    out = antecedent_conditions(dv_q, basin, pd.Series([pd.Timestamp("2015-01-01")]))
    assert np.isnan(out.iloc[0]["bfi_prior"])
    assert np.isnan(out.iloc[0]["baseflow_prior_cfs"])
    assert out.iloc[0]["precip_prior_in"] == 0.0
