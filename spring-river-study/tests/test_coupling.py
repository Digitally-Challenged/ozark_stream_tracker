import numpy as np
import pandas as pd

from spring_river.climate.coupling import lag_correlation, monthly_series, response_lag


def _coupled(lag_months=2, seed=0):
    rng = np.random.default_rng(seed)
    d = pd.date_range("1995-01-01", "2020-12-31", freq="D")
    p = np.where(rng.random(len(d)) < 0.3, rng.exponential(0.3, len(d)), 0.0)
    precip = pd.DataFrame({"date": d, "pcpn_in": p})
    mp = precip.set_index("date")["pcpn_in"].resample("MS").sum()
    q_month = 200 + 40 * mp.shift(lag_months).fillna(mp.mean())
    q = q_month.reindex(d, method="ffill") + rng.normal(0, 3, len(d))
    return precip, pd.DataFrame({"date": d, "value": q.to_numpy(), "approved": True})


def test_monthly_series_columns():
    m = monthly_series(*_coupled())
    assert list(m.columns) == ["month", "p_in", "q_cfs"]
    assert m["p_in"].notna().sum() > 300


def test_lag_correlation_peaks_at_true_lag():
    m = monthly_series(*_coupled(lag_months=2))
    lc = lag_correlation(m, max_lag=6, n_boot=100)
    assert list(lc.columns) == ["lag", "r", "r_lo", "r_hi", "n"]
    assert response_lag(lc) == 2
    best = lc[lc["lag"] == 2].iloc[0]
    assert best["r_lo"] <= best["r"] <= best["r_hi"]
