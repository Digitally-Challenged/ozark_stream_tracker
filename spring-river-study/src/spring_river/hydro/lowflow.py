"""Q1: is base flow declining secularly or tracking precipitation? (spec §2.2)

Attribution model: log(min7) ~ P_recharge(t) + P_recharge(t-1) + ONI.
The residual Mann-Kendall/Sen trend isolates non-climatic decline.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm

from spring_river.hydro.baseflow import bfi_by_wy
from spring_river.hydro.wateryear import min7, water_year
from spring_river.ingest.oni import recharge_season_oni
from spring_river.stats.trends import TrendResult, trend_test

PREDICTORS = ["p_recharge_in", "p_recharge_prev_in", "oni_recharge"]
RECHARGE_MONTHS = [9, 10, 11, 12, 1, 2]
SON_MONTHS = [9, 10, 11]


@dataclass(frozen=True)
class AttributionFit:
    n: int
    coef: dict[str, float]
    ci: dict[str, tuple[float, float]]
    r2: float
    residual_trend: TrendResult
    min7_trend: TrendResult


def _recharge_totals(basin_precip: pd.DataFrame, min_days: int) -> pd.Series:
    """Sep-Feb precipitation total per water year; NaN when fewer than
    `min_days` non-NaN days are present (181/182 possible)."""
    d = pd.to_datetime(basin_precip["date"])
    wy = d.dt.year + (d.dt.month >= 9).astype(int)  # Sep..Dec -> next WY's season
    in_season = d.dt.month.isin(RECHARGE_MONTHS)
    g = basin_precip.loc[in_season].groupby(wy[in_season])["pcpn_in"]
    total = g.sum(min_count=1)
    return total.where(g.count() >= min_days).rename("p_recharge_in")


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
    min_precip_days: int = 165,
) -> pd.DataFrame:
    """One row per water year of discharge record: low-flow responses plus
    recharge-season predictors (precip this WY, precip previous WY, ONI)."""
    q = dv_q.assign(date=pd.to_datetime(dv_q["date"]))
    q = q.assign(wy=water_year(q["date"]))
    m7 = min7(q[["date", "value"]])
    son = q[q["date"].dt.month.isin(SON_MONTHS)].groupby("wy")["value"].mean()
    bfi = bfi_by_wy(q[["date", "value"]])
    p = _recharge_totals(basin_precip, min_precip_days)
    o = recharge_season_oni(oni.assign(date=pd.to_datetime(oni["date"])))
    complete = _complete_by_wy(q)

    wys = pd.Series(sorted(q["wy"].unique()), name="wy")
    return pd.DataFrame(
        {
            "wy": wys,
            "min7_cfs": wys.map(m7),
            "son_mean_cfs": wys.map(son),
            "bfi": wys.map(bfi),
            "p_recharge_in": wys.map(p),
            "p_recharge_prev_in": (wys - 1).map(p),
            "oni_recharge": wys.map(o),
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
