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


def test_daily_lag_correlation_peaks_within_days():
    """A synthetic aquifer: flow is a fast-onset, slowly-decaying response to
    rain. The daily cross-correlation must peak within a few days, not at 30."""
    import numpy as np
    import pandas as pd

    from spring_river.climate.coupling import daily_lag_correlation

    rng = np.random.default_rng(0)
    d = pd.date_range("2000-01-01", "2010-12-31", freq="D")
    p = np.where(rng.random(len(d)) < 0.2, rng.exponential(0.3, len(d)), 0.0)
    # exponential memory kernel, peak response 2 days after the rain
    k = np.exp(-np.arange(120) / 40.0)
    q = 100 + np.convolve(p, k)[: len(d)] * 20
    out = daily_lag_correlation(pd.DataFrame({"date": d, "pcpn_in": p}),
                                pd.DataFrame({"date": d, "value": q}), max_lag_days=60)
    assert len(out) == 61
    best = int(out.loc[out["r"].idxmax(), "lag_days"])
    assert best <= 5
    # monotone decay: no local maximum out near a month
    assert out.loc[out["lag_days"] == 30, "r"].iloc[0] > out.loc[out["lag_days"] == 60, "r"].iloc[0]
