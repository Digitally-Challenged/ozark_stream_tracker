"""Log-Pearson III flood frequency (spec §2.3).

This is LP3 by method of moments with Bulletin 17B/17C-style weighted skew,
a single Grubbs-Beck low-outlier screen, and parametric-bootstrap CIs. It is
NOT the full Expected Moments Algorithm (no censored/historical-period
likelihood); PeakFQ/EMA is the documented follow-up. Regional skew comes from
config.REGIONAL_SKEW (approximate; see config comment).
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from spring_river.config import REGIONAL_SKEW, REGIONAL_SKEW_MSE


@dataclass(frozen=True)
class LP3Fit:
    n: int
    mean_log: float
    sd_log: float
    station_skew: float
    weighted_skew: float
    low_outlier_threshold_cfs: float
    n_dropped: int


def station_skew(x: np.ndarray) -> float:
    x = np.asarray(x, dtype="float64")
    n = len(x)
    m, s = x.mean(), x.std(ddof=1)
    if s == 0:
        return 0.0
    return float(n / ((n - 1) * (n - 2)) * np.sum(((x - m) / s) ** 3))


def skew_mse(g: float, n: int) -> float:
    ag = abs(g)
    a = -0.33 + 0.08 * ag if ag <= 0.90 else -0.52 + 0.30 * ag
    b = 0.94 - 0.26 * ag if ag <= 1.50 else 0.55
    return float(10 ** (a - b * np.log10(n / 10)))


def weighted_skew(gs: float, n: int, gr: float = REGIONAL_SKEW, mse_r: float = REGIONAL_SKEW_MSE) -> float:
    mse_s = skew_mse(gs, n)
    return float((mse_r * gs + mse_s * gr) / (mse_r + mse_s))


def grubbs_beck_threshold(logq: np.ndarray) -> float:
    n = len(logq)
    kn = -0.9043 + 3.345 * np.sqrt(np.log10(n)) - 0.4046 * np.log10(n)
    return float(logq.mean() - kn * logq.std(ddof=1))


def fit_lp3(
    peaks_cfs: np.ndarray,
    regional_skew: float | None = REGIONAL_SKEW,
    mse_r: float = REGIONAL_SKEW_MSE,
) -> LP3Fit:
    x = np.log10(np.asarray(peaks_cfs, dtype="float64"))
    x = x[np.isfinite(x)]
    thr = grubbs_beck_threshold(x)
    kept = x[x >= thr]
    n_dropped = int(len(x) - len(kept))
    gs = station_skew(kept)
    gw = gs if regional_skew is None else weighted_skew(gs, len(kept), regional_skew, mse_r)
    return LP3Fit(len(kept), float(kept.mean()), float(kept.std(ddof=1)), gs, gw, float(10 ** thr), n_dropped)


def quantile(fit: LP3Fit, return_period: float) -> float:
    k = stats.pearson3.ppf(1 - 1 / return_period, fit.weighted_skew)
    return float(10 ** (fit.mean_log + k * fit.sd_log))


def return_period(fit: LP3Fit, q_cfs: float) -> float:
    k = (np.log10(q_cfs) - fit.mean_log) / fit.sd_log
    p_exc = 1 - stats.pearson3.cdf(k, fit.weighted_skew)
    return float(1 / p_exc) if p_exc > 0 else float("inf")


def bootstrap_quantiles(
    peaks_cfs: np.ndarray,
    return_periods: tuple[float, ...],
    n_boot: int = 2000,
    seed: int = 0,
    **fit_kw,
) -> pd.DataFrame:
    x = np.asarray(peaks_cfs, dtype="float64")
    fit = fit_lp3(x, **fit_kw)
    rng = np.random.default_rng(seed)
    sims = np.empty((n_boot, len(return_periods)))
    for i in range(n_boot):
        f = fit_lp3(rng.choice(x, len(x), replace=True), **fit_kw)
        sims[i] = [quantile(f, t) for t in return_periods]
    lo, hi = np.percentile(sims, [5, 95], axis=0)
    point = np.array([quantile(fit, t) for t in return_periods])
    return pd.DataFrame({"return_period": return_periods, "q_cfs": point,
                         "q_lo": np.minimum(lo, point), "q_hi": np.maximum(hi, point)})


def stage_flow_fit(peaks: pd.DataFrame) -> tuple[float, float, float]:
    d = peaks.dropna(subset=["peak_cfs", "gage_ht_ft"])
    d = d[(d["peak_cfs"] > 0) & (d["gage_ht_ft"] > 0)]
    x, y = np.log10(d["gage_ht_ft"].to_numpy()), np.log10(d["peak_cfs"].to_numpy())
    res = stats.linregress(x, y)
    return float(res.intercept), float(res.slope), float(res.rvalue**2)


def stage_to_flow(a: float, b: float, stage_ft: float) -> float:
    return float(10 ** (a + b * np.log10(stage_ft)))


def flow_to_stage(a: float, b: float, q_cfs: float) -> float:
    return float(10 ** ((np.log10(q_cfs) - a) / b))
