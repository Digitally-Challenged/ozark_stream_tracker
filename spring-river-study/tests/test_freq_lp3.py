import numpy as np
import pandas as pd
from scipy import stats

from spring_river.hydro.freq_lp3 import (
    bootstrap_quantiles,
    fit_lp3,
    flow_to_stage,
    grubbs_beck_threshold,
    quantile,
    return_period,
    skew_mse,
    stage_flow_fit,
    stage_to_flow,
    station_skew,
    weighted_skew,
)


def _lp3_sample(n=80, seed=0, mean=4.3, sd=0.3, skew=-0.3):
    rng = np.random.default_rng(seed)
    return 10 ** stats.pearson3.rvs(skew, loc=mean, scale=sd, size=n, random_state=rng)


def test_station_skew_symmetric_sample_near_zero():
    x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=float)
    assert abs(station_skew(x)) < 1e-9


def test_skew_mse_b17b_values():
    # B17B eq 6: |G|=0.2, n=50 -> A=-0.314, B=0.888 -> MSE=10^(A - B*log10(5))
    assert abs(skew_mse(0.2, 50) - 10 ** (-0.314 - 0.888 * np.log10(5))) < 1e-9


def test_weighted_skew_between_station_and_regional():
    gw = weighted_skew(0.4, 30, gr=-0.2, mse_r=0.302)
    assert -0.2 < gw < 0.4


def test_grubbs_beck_flags_low_outlier():
    logq = np.log10(_lp3_sample())
    logq[0] = 2.0  # absurdly low peak
    thr = grubbs_beck_threshold(logq)
    assert logq[0] < thr < np.median(logq)


def test_fit_flags_but_keeps_low_outliers_by_default():
    x = _lp3_sample()
    x[0] = 100.0  # absurdly low peak
    fit = fit_lp3(x, regional_skew=None)
    assert fit.n_low_outliers_flagged == 1
    assert fit.n == len(x)
    assert 100.0 < fit.low_outlier_threshold_cfs
    dropped = fit_lp3(x, regional_skew=None, drop_low_outliers=True)
    assert dropped.n_low_outliers_flagged == 1
    assert dropped.n == len(x) - 1
    assert dropped.mean_log > fit.mean_log


def test_fit_and_quantile_roundtrip():
    x = _lp3_sample(n=200)
    fit = fit_lp3(x, regional_skew=None)
    q100 = quantile(fit, 100)
    assert abs(return_period(fit, q100) - 100) < 1e-6
    assert quantile(fit, 2) < quantile(fit, 10) < q100
    assert abs(fit.mean_log - 4.3) < 0.05


def test_bootstrap_ci_brackets_point_estimate():
    x = _lp3_sample()
    tbl = bootstrap_quantiles(x, (2, 10, 100), n_boot=200, regional_skew=None)
    assert list(tbl.columns) == ["return_period", "q_cfs", "q_lo", "q_hi"]
    assert (tbl["q_lo"] <= tbl["q_cfs"]).all() and (tbl["q_cfs"] <= tbl["q_hi"]).all()


def test_stage_flow_fit_roundtrip():
    h = np.linspace(6, 23, 24)
    q = 10 ** (2.0 + 1.8 * np.log10(h))
    a, b, r2 = stage_flow_fit(pd.DataFrame({"peak_cfs": q, "gage_ht_ft": h}))
    assert abs(a - 2.0) < 1e-9 and abs(b - 1.8) < 1e-9 and r2 > 0.999
    assert abs(flow_to_stage(a, b, stage_to_flow(a, b, 16.0)) - 16.0) < 1e-9
