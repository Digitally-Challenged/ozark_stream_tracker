"""Peak-timing circular statistics (Phase 7). Dates are mapped onto the
annual circle so a Dec 20 / Jan 10 pair averages near New Year, not July.

Rayleigh test p-value uses the Zar (1999) approximation
    p = exp( sqrt(1 + 4n + 4(n^2 - R_n^2)) - (1 + 2n) ),   R_n = n*R,
which is accurate to ~3 decimals for n >= 10 and adequate for n >= 3.
"""
import math

import numpy as np
import pandas as pd

DAYS_PER_YEAR = 365.25
MIN_N_FOR_TEST = 3
COLUMNS = ["period", "n", "mean_doy", "mean_date_label", "R", "rayleigh_p"]
ALL_PERIOD = "all"


def _to_angles(dates: pd.Series) -> np.ndarray:
    doy = pd.to_datetime(dates).dt.dayofyear.to_numpy(dtype="float64")
    return 2 * math.pi * (doy - 1) / DAYS_PER_YEAR


def _rayleigh_p(n: int, R: float) -> float:
    if n < MIN_N_FOR_TEST:
        return float("nan")
    R_n = n * R
    p = math.exp(math.sqrt(1 + 4 * n + 4 * (n * n - R_n * R_n)) - (1 + 2 * n))
    return float(min(1.0, p))


def _doy_label(mean_doy: float) -> str:
    # Non-leap reference year keeps "1..365" labels stable; doy 366 -> 31 Dec.
    day = min(365, max(1, int(round(mean_doy))))
    return (pd.Timestamp(2001, 1, 1) + pd.Timedelta(days=day - 1)).strftime("%d %b")


def circular_stats(dates: pd.Series) -> dict:
    dates = pd.Series(pd.to_datetime(dates)).dropna()
    n = int(len(dates))
    if n == 0:
        return {"n": 0, "mean_doy": float("nan"), "mean_date_label": "",
                "R": float("nan"), "rayleigh_p": float("nan")}
    theta = _to_angles(dates)
    c, s = float(np.cos(theta).mean()), float(np.sin(theta).mean())
    R = math.hypot(c, s)
    mean_angle = math.atan2(s, c) % (2 * math.pi)
    mean_doy = mean_angle * DAYS_PER_YEAR / (2 * math.pi) + 1
    return {"n": n, "mean_doy": float(mean_doy), "mean_date_label": _doy_label(mean_doy),
            "R": float(R), "rayleigh_p": _rayleigh_p(n, R)}


def peak_timing_by_period(dates: pd.Series, period_years: int = 10,
                          start_year: int | None = None) -> pd.DataFrame:
    dates = pd.Series(pd.to_datetime(dates)).dropna().sort_values().reset_index(drop=True)
    if dates.empty:
        return pd.DataFrame(columns=COLUMNS)
    years = dates.dt.year
    first = int(years.min()) if start_year is None else int(start_year)
    rows = []
    for p0 in range(first, int(years.max()) + 1, period_years):
        p1 = p0 + period_years - 1
        sel = dates[(years >= p0) & (years <= p1)]
        rows.append({"period": f"{p0}–{p1}", **circular_stats(sel)})
    rows.append({"period": ALL_PERIOD, **circular_stats(dates)})
    return pd.DataFrame(rows, columns=COLUMNS)


def watson_williams(groups: list[pd.Series]) -> dict:
    """Watson–Williams test for a common circular mean across groups.

    Phase 8 (review.md item 13). "No decadal drift in peak timing" was
    asserted, never tested: decade means swing widely with n≈10 per decade,
    where the circular standard error is a month or more. This is the standard
    one-way circular ANOVA (von Mises, assumes a shared concentration and is
    reliable for R̄ > 0.45 — `r_bar` is reported so the caller can judge).

    Returns F, p, degrees of freedom, N, k and R̄.
    """
    from scipy import stats as st

    vectors, ns = [], []
    for g in groups:
        d = pd.Series(pd.to_datetime(g)).dropna()
        if len(d) < MIN_N_FOR_TEST:
            continue
        theta = _to_angles(d)
        vectors.append((float(np.cos(theta).sum()), float(np.sin(theta).sum())))
        ns.append(len(d))
    k = len(vectors)
    if k < 2:
        return {"k": k, "N": int(sum(ns)), "F": float("nan"), "p": float("nan"),
                "df1": 0, "df2": 0, "r_bar": float("nan")}
    N = int(sum(ns))
    r_each = [math.hypot(c, s) for c, s in vectors]
    R = sum(r_each)
    total = math.hypot(sum(c for c, _ in vectors), sum(s for _, s in vectors))
    r_bar = R / N
    # Stephens' correction factor, standard for the Watson-Williams statistic
    kappa_corr = 1 + 3 / (8 * _kappa(r_bar)) if r_bar > 0 else 1.0
    denom = (N - R)
    if denom <= 0 or k < 2 or N - k <= 0:
        return {"k": k, "N": N, "F": float("nan"), "p": float("nan"),
                "df1": k - 1, "df2": N - k, "r_bar": r_bar}
    f = kappa_corr * ((N - k) * (R - total)) / ((k - 1) * denom)
    p = float(st.f.sf(f, k - 1, N - k)) if np.isfinite(f) and f >= 0 else float("nan")
    return {"k": k, "N": N, "F": float(f), "p": p, "df1": k - 1, "df2": N - k, "r_bar": r_bar}


def _kappa(r_bar: float) -> float:
    """Maximum-likelihood von Mises concentration from R̄ (Fisher 1993)."""
    if r_bar < 0.53:
        return 2 * r_bar + r_bar**3 + 5 * r_bar**5 / 6
    if r_bar < 0.85:
        return -0.4 + 1.39 * r_bar + 0.43 / (1 - r_bar)
    return 1 / (r_bar**3 - 4 * r_bar**2 + 3 * r_bar) if r_bar < 1 else float("inf")


def circular_se_days(n: int, r_bar: float) -> float:
    """Approximate circular standard error of a mean date, in days."""
    if n <= 0 or not (0 < r_bar <= 1):
        return float("nan")
    return float(DAYS_PER_YEAR / (2 * math.pi) / math.sqrt(n * r_bar * _kappa(r_bar)))
