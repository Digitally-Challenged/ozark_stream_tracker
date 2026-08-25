"""Partial-duration series: declustered peaks-over-threshold with 7-day
independence, annual counts, Poisson dispersion test (spec §2.3)."""
import pandas as pd
from scipy import stats

from spring_river.hydro.wateryear import water_year


def pot_events(daily: pd.DataFrame, threshold: float, min_sep_days: int = 7) -> pd.DataFrame:
    d = daily.sort_values("date").reset_index(drop=True)
    exc = d[d["value"] >= threshold]
    if exc.empty:
        return pd.DataFrame({"start": pd.Series(dtype="datetime64[ns]"), "end": pd.Series(dtype="datetime64[ns]"),
                             "peak_date": pd.Series(dtype="datetime64[ns]"), "peak_value": pd.Series(dtype="float64")})
    gap = exc["date"].diff().dt.days.fillna(0)
    cluster = (gap > min_sep_days).cumsum()
    rows = []
    for _, grp in exc.groupby(cluster):
        peak = grp.loc[grp["value"].idxmax()]
        rows.append({"start": grp["date"].min(), "end": grp["date"].max(),
                     "peak_date": peak["date"], "peak_value": float(peak["value"])})
    return pd.DataFrame(rows)


def annual_counts(events: pd.DataFrame, wys: list[int]) -> pd.Series:
    if events.empty:
        return pd.Series(0, index=pd.Index(wys, name="wy"), name="count")
    wy = water_year(events["peak_date"])
    c = wy.value_counts()
    return pd.Series([int(c.get(y, 0)) for y in wys], index=pd.Index(wys, name="wy"), name="count")


def dispersion_test(counts: pd.Series) -> dict:
    n = int(len(counts))
    mean = float(counts.mean())
    var = float(counts.var(ddof=1))
    if mean == 0:
        return {"n": n, "mean": mean, "var": var, "dispersion": float("nan"), "p": float("nan")}
    d = var / mean
    stat = (n - 1) * d
    cdf = stats.chi2.cdf(stat, n - 1)
    p = float(2 * min(cdf, 1 - cdf))
    return {"n": n, "mean": mean, "var": var, "dispersion": float(d), "p": p}
