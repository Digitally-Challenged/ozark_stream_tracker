"""Q5: is the stage-floor decline a rating artifact? Stage at fixed discharge
per water year from IV pairs (spec §2.2, risk #4). This is the IV-derived
substitute for USGS shift records, which have not been obtained.

Stage at a target flow is estimated by a local log-linear fit
(stage = a + b*log10(q)) over pairs within ±tol of the target, evaluated
at the target -- not by the median of the band, which biases toward
whichever side of the target has more samples."""
import numpy as np
import pandas as pd

from spring_river.config import RATING_FLOWS_CFS, RATING_TOLERANCE
from spring_river.hydro.wateryear import water_year


def pair_iv(iv_q: pd.DataFrame, iv_h: pd.DataFrame) -> pd.DataFrame:
    m = iv_q.merge(iv_h, on="datetime", suffixes=("_q", "_h"))
    return pd.DataFrame(
        {
            "datetime": m["datetime"],
            "q_cfs": m["value_q"].astype("float64"),
            "stage_ft": m["value_h"].astype("float64"),
            "approved": m["approved_q"] & m["approved_h"],
        }
    ).dropna(subset=["q_cfs", "stage_ft"]).reset_index(drop=True)


def _stage_at(pairs_subset: pd.DataFrame, flow: float, tol: float, min_pairs: int) -> tuple[float, float, int]:
    """Local fit stage = a + b*log10(q) within [flow*(1-tol), flow*(1+tol)].

    Returns (stage_at_flow_ft, residual_std_ft, n_pairs); NaNs when n < min_pairs."""
    band = pairs_subset[(pairs_subset["q_cfs"] >= flow * (1 - tol)) & (pairs_subset["q_cfs"] <= flow * (1 + tol))]
    band = band[band["q_cfs"] > 0]
    n = int(len(band))
    if n < min_pairs:
        return float("nan"), float("nan"), n
    x = np.log10(band["q_cfs"].to_numpy(dtype="float64"))
    y = band["stage_ft"].to_numpy(dtype="float64")
    b, a = np.polyfit(x, y, 1)
    resid = y - (a + b * x)
    dof = max(n - 2, 1)
    se = float(np.sqrt((resid**2).sum() / dof))
    return float(a + b * np.log10(flow)), se, n


def stage_at_flow(
    pairs: pd.DataFrame,
    flows: tuple[float, ...] = RATING_FLOWS_CFS,
    tol: float = RATING_TOLERANCE,
    min_pairs: int = 30,
) -> pd.DataFrame:
    p = pairs.assign(wy=water_year(pairs["datetime"]))
    rows = []
    for wy, grp in p.groupby("wy"):
        for f in flows:
            stage, se, n = _stage_at(grp, f, tol, min_pairs)
            rows.append({"wy": int(wy), "flow_cfs": float(f), "stage_at_flow_ft": stage, "stage_se_ft": se, "n_pairs": n})
    return pd.DataFrame(rows, columns=["wy", "flow_cfs", "stage_at_flow_ft", "stage_se_ft", "n_pairs"])


def rating_shift_at_events(
    pairs: pd.DataFrame,
    event_dates: pd.Series,
    flows: tuple[float, ...] = RATING_FLOWS_CFS,
    window_days: int = 365,
    **fit_kw,
) -> pd.DataFrame:
    """Stage-at-flow in [event - window, event) vs (event, event + window]."""
    tol = fit_kw.get("tol", RATING_TOLERANCE)
    min_pairs = fit_kw.get("min_pairs", 30)
    win = pd.to_timedelta(int(window_days), unit="D")
    t = pd.to_datetime(pairs["datetime"])
    rows = []
    for d in pd.to_datetime(event_dates):
        before = pairs[(t >= d - win) & (t < d)]
        after = pairs[(t > d) & (t <= d + win)]
        for f in flows:
            s_b, _, n_b = _stage_at(before, f, tol, min_pairs)
            s_a, _, n_a = _stage_at(after, f, tol, min_pairs)
            rows.append(
                {
                    "event_date": d,
                    "flow_cfs": float(f),
                    "stage_before_ft": s_b,
                    "stage_after_ft": s_a,
                    "shift_ft": s_a - s_b,
                    "n_before": n_b,
                    "n_after": n_a,
                }
            )
    return pd.DataFrame(
        rows, columns=["event_date", "flow_cfs", "stage_before_ft", "stage_after_ft", "shift_ft", "n_before", "n_after"]
    )
