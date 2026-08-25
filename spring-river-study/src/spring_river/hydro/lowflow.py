"""Q1: is base flow declining secularly or tracking precipitation? (spec §2.2)

Attribution model: log(min7) ~ P_trailing(t) + P_trailing(t-1) + ONI_trailing.
The residual Mann-Kendall/Sen trend isolates non-climatic decline.

Temporal-leakage fix (adversarial review, 2026-08-25). The original model used
the fixed Sep-Feb recharge total of the same water year as the predictor. But
min7 usually occurs BEFORE that season ends (32/43 Mammoth years ended before
Feb), so the predictor contained precipitation that fell AFTER the response
was realised — non-causal leakage that inflates apparent precip control.
Predictors are now strictly antecedent to each water year's own min7 window:

- `p_trailing_in`      basin precip over the 365 days ending the day BEFORE
                       the 7-day min7 window STARTS (end_date - 7 days);
- `p_trailing_prev_in` the 365 days before that;
- `oni_trailing`       mean ONI anomaly over the 6 center-months ending in the
                       month before the end date.

A precip predictor is NaN when its window has < `min_precip_coverage` of days
observed; ONI is NaN with fewer than `min_oni_months` months present.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm

from spring_river.hydro.baseflow import bfi_by_wy
from spring_river.hydro.wateryear import min7_dated, water_year
from spring_river.stats.trends import TrendResult, trend_test

PREDICTORS = ["p_trailing_in", "p_trailing_prev_in", "oni_trailing"]
SON_MONTHS = [9, 10, 11]
TRAILING_DAYS = 365
MIN7_WINDOW_DAYS = 7  # predictors end the day before the 7-day window starts
ONI_MONTHS = 6


@dataclass(frozen=True)
class AttributionFit:
    n: int
    coef: dict[str, float]
    ci: dict[str, tuple[float, float]]
    r2: float
    residual_trend: TrendResult
    min7_trend: TrendResult


def _daily_precip(basin_precip: pd.DataFrame) -> pd.Series:
    """Basin precip on a complete daily index over its span (missing days NaN)."""
    p = basin_precip.assign(date=pd.to_datetime(basin_precip["date"]))
    s = p.set_index("date")["pcpn_in"].sort_index()
    return s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="D"))


def _trailing_precip(
    daily: pd.Series, end_date: pd.Timestamp, lag_days: int, min_coverage: float
) -> float:
    """Precip total over the `TRAILING_DAYS` window ending `lag_days` before
    `end_date` (lag 1 = the day before). NaN below `min_coverage` of days."""
    if pd.isna(end_date):
        return float("nan")
    last = end_date - pd.DateOffset(days=lag_days)
    first = last - pd.DateOffset(days=TRAILING_DAYS - 1)
    w = daily.loc[first:last]
    if w.notna().sum() < min_coverage * TRAILING_DAYS:
        return float("nan")
    return float(w.sum())


def _trailing_oni(
    oni_monthly: pd.Series, end_date: pd.Timestamp, min_months: int
) -> float:
    """Mean ONI over the `ONI_MONTHS` center-months ending the month before
    `end_date`; NaN with fewer than `min_months` values present."""
    if pd.isna(end_date):
        return float("nan")
    last = end_date.normalize().replace(day=1) - pd.DateOffset(months=1)
    first = last - pd.DateOffset(months=ONI_MONTHS - 1)
    w = oni_monthly.loc[first:last].dropna()
    return float(w.mean()) if len(w) >= min_months else float("nan")


def _complete_by_wy(q: pd.DataFrame) -> pd.Series:
    """True when the water year's record reaches its Sep 30 end date."""
    last = q.groupby("wy")["date"].max()
    ends = pd.Series(
        [pd.Timestamp(int(y), 9, 30) for y in last.index], index=last.index
    )
    return (last >= ends).rename("complete")


def attribution_table(
    dv_q: pd.DataFrame,
    basin_precip: pd.DataFrame,
    oni: pd.DataFrame,
    min_precip_coverage: float = 0.9,
    min_oni_months: int = 4,
) -> pd.DataFrame:
    """One row per water year of discharge record: low-flow responses plus
    strictly-antecedent predictors anchored on that WY's min7 end date
    (see module docstring)."""
    q = dv_q.assign(date=pd.to_datetime(dv_q["date"]))
    q = q.assign(wy=water_year(q["date"]))
    m7 = min7_dated(q[["date", "value"]]).set_index("wy")
    son = q[q["date"].dt.month.isin(SON_MONTHS)].groupby("wy")["value"].mean()
    bfi = bfi_by_wy(q[["date", "value"]])
    daily_p = _daily_precip(basin_precip)
    o = oni.assign(date=pd.to_datetime(oni["date"])).set_index("date")["anom"].sort_index()
    complete = _complete_by_wy(q)

    wys = pd.Series(sorted(q["wy"].unique()), name="wy")
    end_dates = wys.map(m7["end_date"])
    return pd.DataFrame(
        {
            "wy": wys,
            "min7_cfs": wys.map(m7["min7"]),
            "min7_end_date": end_dates,
            "son_mean_cfs": wys.map(son),
            "bfi": wys.map(bfi),
            # Windows end the day BEFORE the 7-day min7 window STARTS
            # (end_date - 7 days), so no response day overlaps a predictor.
            "p_trailing_in": [
                _trailing_precip(daily_p, d, MIN7_WINDOW_DAYS, min_precip_coverage)
                for d in end_dates
            ],
            "p_trailing_prev_in": [
                _trailing_precip(daily_p, d, MIN7_WINDOW_DAYS + TRAILING_DAYS, min_precip_coverage)
                for d in end_dates
            ],
            "oni_trailing": [
                _trailing_oni(o, d - pd.DateOffset(days=MIN7_WINDOW_DAYS), min_oni_months)
                if pd.notna(d) else float("nan")
                for d in end_dates
            ],
            "complete": wys.map(complete).fillna(False).astype(bool),
        }
    )


def fit_attribution(tbl: pd.DataFrame, response: str = "min7_cfs") -> AttributionFit:
    """OLS log(response) ~ predictors with HC3 robust CIs, plus Mann-Kendall/
    Sen trend on the residuals and on log(response) itself for comparison.
    Drops incomplete water years and rows with any NaN predictor/response."""
    d = tbl[tbl["complete"]].dropna(subset=[response, *PREDICTORS])
    d = d[d[response] > 0]
    y = np.log(d[response].to_numpy(dtype="float64"))
    X = sm.add_constant(d[PREDICTORS].to_numpy(dtype="float64"))
    res = sm.OLS(y, X).fit(cov_type="HC3")
    names = ["const", *PREDICTORS]
    ci_arr = np.asarray(res.conf_int())
    coef = {k: float(v) for k, v in zip(names, res.params)}
    ci = {k: (float(lo), float(hi)) for k, (lo, hi) in zip(names, ci_arr)}
    wy = d["wy"].to_numpy(dtype="float64")
    return AttributionFit(
        n=int(res.nobs),
        coef=coef,
        ci=ci,
        r2=float(res.rsquared),
        residual_trend=trend_test(np.asarray(res.resid), wy),
        min7_trend=trend_test(y, wy),
    )


PRECIP_ONLY_PREDICTORS = ["p_trailing_in", "p_trailing_prev_in"]


def ratio_series(numer: pd.DataFrame, denom: pd.DataFrame) -> pd.DataFrame:
    """log(numer min7 / denom min7) by water year.

    Phase 8 (review.md item 5). The best available climate control for Hardy
    is Mammoth Spring itself: the same recharge climate, absorbing
    precipitation, ENSO, PET and any gridded-precipitation bias at once. The
    ratio therefore tests Hardy's rise with NO precipitation model involved —
    if the rise were climate, it would vanish against Mammoth.

    `numer` and `denom` are attribution tables (see `attribution_table`).
    """
    a = numer.set_index("wy")["min7_cfs"]
    b = denom.set_index("wy")["min7_cfs"]
    j = pd.DataFrame({"numer_cfs": a, "denom_cfs": b}).dropna()
    j = j[(j["numer_cfs"] > 0) & (j["denom_cfs"] > 0)]
    j["ratio"] = j["numer_cfs"] / j["denom_cfs"]
    j["log_ratio"] = np.log(j["ratio"])
    return j.reset_index()


def ratio_trend(numer: pd.DataFrame, denom: pd.DataFrame) -> tuple[TrendResult, pd.DataFrame]:
    """Sen/MK trend on log(numer/denom) min7, plus the series itself."""
    s = ratio_series(numer, denom)
    return trend_test(s["log_ratio"].to_numpy(dtype="float64"),
                      s["wy"].to_numpy(dtype="float64")), s


def fit_attribution_precip_only(tbl: pd.DataFrame, response: str = "min7_cfs") -> AttributionFit:
    """`fit_attribution` without the ONI term.

    At n≈24 the never-significant ONI regressor costs a degree of freedom for
    nothing; dropping it is what makes the Hardy residual rise resolvable on
    all three basin sources rather than one.
    """
    d = tbl[tbl["complete"]].dropna(subset=[response, *PRECIP_ONLY_PREDICTORS])
    d = d[d[response] > 0]
    y = np.log(d[response].to_numpy(dtype="float64"))
    X = sm.add_constant(d[PRECIP_ONLY_PREDICTORS].to_numpy(dtype="float64"))
    res = sm.OLS(y, X).fit(cov_type="HC3")
    names = ["const", *PRECIP_ONLY_PREDICTORS]
    ci_arr = np.asarray(res.conf_int())
    wy = d["wy"].to_numpy(dtype="float64")
    return AttributionFit(
        n=int(res.nobs),
        coef={k: float(v) for k, v in zip(names, res.params)},
        ci={k: (float(lo), float(hi)) for k, (lo, hi) in zip(names, ci_arr)},
        r2=float(res.rsquared),
        residual_trend=trend_test(np.asarray(res.resid), wy),
        min7_trend=trend_test(y, wy),
    )
