"""Q6: is the ~4-year major-flood cadence real? Inter-arrival distribution vs
exponential (parametric-bootstrap KS, Lilliefors-style because the rate is
estimated). Plus antecedent conditions before >=14 ft events (spec §2.3)."""
import numpy as np
import pandas as pd
from scipy import stats

from spring_river.hydro.baseflow import eckhardt_segmented

DAYS_PER_YEAR = 365.25
MIN_EVENTS = 3


def _gaps_years(event_dates: pd.Series) -> np.ndarray:
    d = pd.to_datetime(event_dates).dropna().sort_values().to_numpy()
    if len(d) < MIN_EVENTS:
        raise ValueError(f"need at least {MIN_EVENTS} events for an inter-arrival test, got {len(d)}")
    return np.diff(d).astype("timedelta64[s]").astype(float) / (86400.0 * DAYS_PER_YEAR)


def _ks_vs_fitted_exponential(gaps: np.ndarray) -> float:
    return float(stats.kstest(gaps, "expon", args=(0.0, gaps.mean())).statistic)


def interarrival_test(event_dates: pd.Series, n_boot: int = 2000, seed: int = 0) -> dict:
    """KS statistic of inter-event gaps (years) against an exponential with the
    fitted rate; p_boot from a parametric bootstrap that re-fits the rate on
    each simulated sample."""
    gaps = _gaps_years(event_dates)
    n = len(gaps)
    ks = _ks_vs_fitted_exponential(gaps)
    rng = np.random.default_rng(seed)
    sims = np.fromiter(
        (_ks_vs_fitted_exponential(rng.exponential(gaps.mean(), n)) for _ in range(n_boot)),
        dtype="float64",
        count=n_boot,
    )
    return {
        "n_events": int(n + 1),
        "mean_gap_yr": float(gaps.mean()),
        "median_gap_yr": float(np.median(gaps)),
        "cv": float(gaps.std(ddof=1) / gaps.mean()),
        "ks_stat": ks,
        "p_boot": float((sims >= ks).mean()),
    }


def _window(df: pd.DataFrame, end: pd.Timestamp, days: int) -> pd.DataFrame:
    start = end - pd.DateOffset(days=days)
    return df[(df["date"] >= start) & (df["date"] < end)]


def antecedent_conditions(
    dv_q: pd.DataFrame,
    basin_precip: pd.DataFrame,
    event_dates: pd.Series,
    bfi_days: int = 60,
    precip_days: int = 30,
) -> pd.DataFrame:
    """Per event: BFI and mean base flow over the `bfi_days` before the event
    (days with a defined Eckhardt base flow only) and basin precipitation
    summed over the `precip_days` before it. Windows exclude the event day."""
    bf = eckhardt_segmented(dv_q)
    rows = []
    for d in pd.to_datetime(event_dates):
        w = _window(bf, d, bfi_days).dropna(subset=["baseflow"])
        p = _window(basin_precip, d, precip_days)
        total_q = float(w["value"].sum())
        rows.append(
            {
                "event_date": d,
                "bfi_prior": float(w["baseflow"].sum() / total_q) if total_q > 0 else float("nan"),
                "precip_prior_in": float(p["pcpn_in"].sum()),
                "baseflow_prior_cfs": float(w["baseflow"].mean()) if len(w) else float("nan"),
            }
        )
    return pd.DataFrame(rows, columns=["event_date", "bfi_prior", "precip_prior_in", "baseflow_prior_cfs"])


def interarrival_power(n_gaps: int, cvs: tuple[float, ...] = (0.7, 0.5, 0.35),
                       n_sim: int = 20_000, alpha: float = 0.05, seed: int = 1) -> pd.DataFrame:
    """Power of the exponential test to reject a REGULAR cadence, by CV.

    Phase 8 (review.md item 2). A high bootstrap p means the gaps are
    consistent with a memoryless process; it does not mean the process IS
    memoryless. With n=7 events the test has almost no power against anything
    but near-metronomic regularity, so the honest statement is "no cadence
    detectable, and none weaker than X could have been".

    Alternative is a gamma with the given coefficient of variation (CV = 1 is
    the exponential; CV < 1 is regular). The statistic is the CV itself,
    one-sided against the exponential null at `n_gaps`.
    """
    rng = np.random.default_rng(seed)
    null = rng.exponential(1.0, (n_sim, n_gaps))
    null_cv = null.std(axis=1, ddof=1) / null.mean(axis=1)
    crit = float(np.percentile(null_cv, 100 * alpha))
    rows = []
    for cv in cvs:
        k = 1.0 / cv**2
        g = rng.gamma(k, 1.0 / k, (n_sim, n_gaps))
        cvs_alt = g.std(axis=1, ddof=1) / g.mean(axis=1)
        rows.append({"cv": cv, "power": float((cvs_alt < crit).mean())})
    return pd.DataFrame(rows).assign(n_gaps=n_gaps, alpha=alpha, critical_cv=crit)


def null_cv_interval(n_gaps: int, n_sim: int = 20_000, seed: int = 1) -> tuple[float, float]:
    """Central 95 % interval of the CV under an exponential null at `n_gaps` —
    the range of CVs a memoryless process routinely produces at this n."""
    rng = np.random.default_rng(seed)
    s = rng.exponential(1.0, (n_sim, n_gaps))
    cv = s.std(axis=1, ddof=1) / s.mean(axis=1)
    lo, hi = np.percentile(cv, [2.5, 97.5])
    return float(lo), float(hi)
