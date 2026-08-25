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
