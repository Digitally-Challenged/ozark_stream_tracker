"""Log-Pearson III flood frequency (spec §2.3).

This is LP3 by method of moments with Bulletin 17B/17C-style weighted skew,
a Grubbs-Beck low-outlier screen used for FLAGGING only by default, and
nonparametric-bootstrap CIs (resampling observed peaks with replacement). It
is NOT the full Expected Moments Algorithm (no censored/historical-period
likelihood); PeakFQ/EMA is the documented follow-up. Regional skew comes from
config.REGIONAL_SKEW (approximate; see config comment).

Low outliers: B17B drops peaks below the Grubbs-Beck threshold AND then
applies a conditional-probability adjustment to the fitted curve. Dropping
without that adjustment biases the quantiles, so the default fit keeps every
peak and only reports how many fall below the threshold
(`n_low_outliers_flagged`). `drop_low_outliers=True` reproduces the old
truncated fit, still WITHOUT the conditional-probability adjustment — use it
for sensitivity checks, not as the headline estimate.
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
    n_low_outliers_flagged: int


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
    drop_low_outliers: bool = False,
) -> LP3Fit:
    """Fit LP3 moments in log10 space.

    `n_low_outliers_flagged` is always the count of peaks below the
    Grubbs-Beck threshold. With `drop_low_outliers=False` (default) those
    peaks remain in the fit. With True they are removed before computing
    moments — NO B17B conditional-probability adjustment is applied, so the
    resulting quantiles are biased and should be treated as a sensitivity
    check only.
    """
    x = np.log10(np.asarray(peaks_cfs, dtype="float64"))
    x = x[np.isfinite(x)]
    thr = grubbs_beck_threshold(x)
    n_flagged = int((x < thr).sum())
    kept = x[x >= thr] if drop_low_outliers else x
    gs = station_skew(kept)
    gw = gs if regional_skew is None else weighted_skew(gs, len(kept), regional_skew, mse_r)
    return LP3Fit(len(kept), float(kept.mean()), float(kept.std(ddof=1)), gs, gw, float(10 ** thr), n_flagged)


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
    """Nonparametric bootstrap (resampling observed peaks with replacement)
    5-95% band on LP3 quantiles; `fit_kw` is forwarded to `fit_lp3`."""
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


def fit_lp3_historical(
    systematic_cfs: np.ndarray,
    historical_cfs: np.ndarray,
    historical_period_years: int,
    regional_skew: float | None = REGIONAL_SKEW,
    mse_r: float = REGIONAL_SKEW_MSE,
) -> LP3Fit:
    """LP3 moments with Bulletin 17B historical weighting (Appendix 6).

    Phase 8 (review.md item 4). The 1982-12-03 29.0 ft crest is KNOWN but sits
    outside the systematic record, and excluding a known extreme biases the
    return periods of exactly the "major exposure" tier long. B17B's remedy is
    to weight the systematic peaks BELOW the historical threshold by

        W = (H - Z) / (n - s)

    where H is the historical period length, Z the number of peaks at or above
    the threshold known in H, n the systematic record length and s the number
    of systematic peaks at or above the threshold. Peaks at or above the
    threshold (systematic or historical) carry weight 1: they are known to be
    the largest in H, so they must not be inflated.

    This is the historical-weighting approximation, not EMA: there is no
    censored-likelihood treatment and no conditional-probability adjustment.
    PeakFQ/EMA remains the documented follow-up.
    """
    sx = np.log10(np.asarray(systematic_cfs, dtype="float64"))
    sx = sx[np.isfinite(sx)]
    hx = np.log10(np.asarray(historical_cfs, dtype="float64"))
    hx = hx[np.isfinite(hx)]
    if hx.size == 0:
        return fit_lp3(systematic_cfs, regional_skew=regional_skew, mse_r=mse_r)
    threshold = float(hx.min())
    n = len(sx)
    s = int((sx >= threshold).sum())
    z = len(hx) + s
    if n - s <= 0 or historical_period_years <= z:
        raise ValueError("historical period too short, or every systematic peak exceeds the threshold")
    w_below = (historical_period_years - z) / (n - s)
    below, above = sx[sx < threshold], sx[sx >= threshold]
    weights = np.concatenate([np.full(len(below), w_below), np.ones(len(above)), np.ones(len(hx))])
    values = np.concatenate([below, above, hx])
    n_eff = float(weights.sum())
    mean = float((weights * values).sum() / n_eff)
    sd = float(np.sqrt((weights * (values - mean) ** 2).sum() / (n_eff - 1)))
    gs = float(n_eff * (weights * (values - mean) ** 3).sum() / ((n_eff - 1) * (n_eff - 2) * sd**3))
    gw = gs if regional_skew is None else weighted_skew(gs, int(round(n_eff)), regional_skew, mse_r)
    thr_cfs = float(10**grubbs_beck_threshold(sx))
    return LP3Fit(int(round(n_eff)), mean, sd, gs, gw, thr_cfs, int((sx < np.log10(thr_cfs)).sum()))
