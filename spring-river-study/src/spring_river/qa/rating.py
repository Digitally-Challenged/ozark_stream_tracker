"""Q5: is the stage-floor decline a rating artifact? Stage at fixed discharge
per water year from IV pairs (spec §2.2, risk #4). This is the IV-derived
substitute for USGS shift records, which have not been obtained.

Stage at a target flow is estimated by a local log-linear fit
(stage = a + b*log10(q)) over pairs within ±tol of the target, evaluated
at the target -- not by the median of the band, which biases toward
whichever side of the target has more samples."""
import numpy as np
import pandas as pd
from scipy import stats

from spring_river.config import RATING_FLOWS_CFS, RATING_TABLE_STAGES_FT, RATING_TOLERANCE
from spring_river.hydro.wateryear import water_year

FLOW_PERCENTILES = (5, 25, 50, 75, 95)


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


def _since(pairs: pd.DataFrame, since: str | None) -> pd.DataFrame:
    if since is None:
        return pairs
    return pairs[pd.to_datetime(pairs["datetime"]) >= pd.Timestamp(since)]


def rating_table(
    pairs: pd.DataFrame,
    stages: tuple[float, ...] = RATING_TABLE_STAGES_FT,
    tol_ft: float = 0.05,
    min_pairs: int = 20,
    since: str | None = None,
) -> pd.DataFrame:
    """Stage -> discharge lookup: median and IQR of q over pairs within ±tol_ft of each stage.

    NaN flow columns when fewer than `min_pairs` fall in the band; `since` keeps
    only pairs with datetime >= since (a "recent rating" variant)."""
    p = _since(pairs, since)
    h, q = p["stage_ft"].to_numpy(dtype="float64"), p["q_cfs"].to_numpy(dtype="float64")
    rows = []
    for s in stages:
        band = q[(h >= s - tol_ft) & (h <= s + tol_ft) & (q > 0)]
        n = int(len(band))
        med, lo, hi = (np.percentile(band, [50, 25, 75]) if n >= min_pairs else (np.nan,) * 3)
        rows.append({"stage_ft": float(s), "median_cfs": med, "q25_cfs": lo, "q75_cfs": hi, "n_pairs": n})
    return pd.DataFrame(rows, columns=["stage_ft", "median_cfs", "q25_cfs", "q75_cfs", "n_pairs"])


def loglog_correlation(pairs: pd.DataFrame) -> dict:
    """Pearson r of log10(stage) vs log10(q), Spearman rho of the raw pairs, and n."""
    p = pairs[(pairs["q_cfs"] > 0) & (pairs["stage_ft"] > 0)]
    r = float(np.corrcoef(np.log10(p["stage_ft"]), np.log10(p["q_cfs"]))[0, 1])
    rho = float(stats.spearmanr(p["stage_ft"], p["q_cfs"]).statistic)
    return {"r_loglog": r, "spearman": rho, "n": int(len(p))}


def flow_percentile_stages(
    pairs: pd.DataFrame,
    dv_q: pd.Series,
    percentiles: tuple[int, ...] = FLOW_PERCENTILES,
    tol: float = 0.03,
    since: str | None = None,
) -> pd.DataFrame:
    """Map flow percentiles of a daily series to stage: median stage of pairs within ±tol of each flow."""
    p = _since(pairs, since)
    h, q = p["stage_ft"].to_numpy(dtype="float64"), p["q_cfs"].to_numpy(dtype="float64")
    flows = np.nanpercentile(dv_q.to_numpy(dtype="float64"), percentiles)
    rows = []
    for pct, f in zip(percentiles, flows):
        band = h[(q >= f * (1 - tol)) & (q <= f * (1 + tol))]
        stage = float(np.median(band)) if len(band) else float("nan")
        rows.append({"percentile": int(pct), "q_cfs": float(f), "stage_ft": stage, "n_pairs": int(len(band))})
    return pd.DataFrame(rows, columns=["percentile", "q_cfs", "stage_ft", "n_pairs"])
