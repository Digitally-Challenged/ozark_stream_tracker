"""Recession analysis: per-event recession constants and a master recession
curve from daily discharge.

Recession runs are extracted only within gap-free segments (`segment_gapfree`,
project rule: never interpolate across long gaps). The recession constant k
(days) comes from OLS on ln q vs t after skipping the quickflow crest.
"""
import numpy as np
import pandas as pd

from spring_river.hydro.segments import segment_gapfree
from spring_river.hydro.wateryear import water_year

DEFAULT_SKIP_DAYS = 3
MIN_FIT_POINTS = 5
K_TABLE_COLUMNS = ["peak_date", "peak_cfs", "n_days", "k_days", "r2", "wy"]
MRC_COLUMNS = ["t_days", "ln_ratio_median", "ln_ratio_q25", "ln_ratio_q75", "n"]


def _is_local_peak(q: np.ndarray, i: int, min_peak_cfs: float) -> bool:
    if q[i] < min_peak_cfs:
        return False
    left = q[i - 1] if i > 0 else -np.inf
    right = q[i + 1] if i < len(q) - 1 else -np.inf
    return q[i] >= left and q[i] >= right


def _run_end(q: np.ndarray, start: int, max_rise_frac: float) -> int:
    """Exclusive end index of the recession run starting at `start`."""
    if q[start] <= 0:
        return start
    j = start + 1
    while j < len(q) and q[j] > 0 and q[j] <= q[j - 1] * (1 + max_rise_frac):
        j += 1
    return j


def recession_segments(
    dv_q: pd.DataFrame,
    min_peak_cfs: float,
    min_days: int = 10,
    max_rise_frac: float = 0.02,
) -> list[pd.DataFrame]:
    """Recession runs after each local peak >= `min_peak_cfs`.

    Within each gap-free segment, a local peak is a day whose value is >= both
    neighbours. The run continues while q[t] <= q[t-1]*(1+max_rise_frac) and
    q[t] > 0. Runs shorter than `min_days` are dropped; peaks inside an
    already-consumed run are skipped. Frames have columns date, value, t_days
    (0 at the peak).
    """
    out = []
    for seg in segment_gapfree(dv_q):
        q = seg["value"].to_numpy()
        i = 0
        while i < len(q):
            if not _is_local_peak(q, i, min_peak_cfs):
                i += 1
                continue
            end = _run_end(q, i, max_rise_frac)
            if end - i >= min_days:
                run = seg.iloc[i:end][["date", "value"]].reset_index(drop=True)
                out.append(run.assign(t_days=np.arange(end - i)))
            i = max(end, i + 1)
    return out


def fit_k(seg: pd.DataFrame, skip_days: int = DEFAULT_SKIP_DAYS) -> tuple[float, float]:
    """(k_days, r2) from OLS ln q = a - t/k on days with t_days >= skip_days.

    Returns (nan, nan) with fewer than MIN_FIT_POINTS usable points or a
    non-negative slope (no recession).
    """
    part = seg[(seg["t_days"] >= skip_days) & (seg["value"] > 0)]
    if len(part) < MIN_FIT_POINTS:
        return float("nan"), float("nan")
    t = part["t_days"].to_numpy(dtype="float64")
    y = np.log(part["value"].to_numpy(dtype="float64"))
    slope, intercept = np.polyfit(t, y, 1)
    if slope >= 0:
        return float("nan"), float("nan")
    resid = y - (intercept + slope * t)
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - float(np.sum(resid**2)) / ss_tot if ss_tot > 0 else float("nan")
    return float(-1.0 / slope), r2


def event_k_table(dv_q: pd.DataFrame, min_peak_cfs: float, **kw) -> pd.DataFrame:
    """One row per qualifying recession event: peak_date, peak_cfs, n_days,
    k_days, r2, wy. `kw` is forwarded to `recession_segments`; `skip_days`
    (if given) goes to `fit_k`."""
    skip_days = kw.pop("skip_days", DEFAULT_SKIP_DAYS)
    rows = []
    for seg in recession_segments(dv_q, min_peak_cfs, **kw):
        k, r2 = fit_k(seg, skip_days=skip_days)
        rows.append(
            {
                "peak_date": seg["date"].iloc[0],
                "peak_cfs": float(seg["value"].iloc[0]),
                "n_days": int(len(seg)),
                "k_days": k,
                "r2": r2,
            }
        )
    if not rows:
        return pd.DataFrame(columns=K_TABLE_COLUMNS)
    tbl = pd.DataFrame(rows)
    tbl["wy"] = water_year(tbl["peak_date"]).to_numpy()
    return tbl[K_TABLE_COLUMNS]


def master_recession(
    segments: list[pd.DataFrame],
    n_points: int = 60,
    skip_days: int = DEFAULT_SKIP_DAYS,
) -> pd.DataFrame:
    """Matching-strip approximation of the master recession curve.

    Each segment is normalised by its flow on day `skip_days`; at each t in
    [skip_days, skip_days + n_points) the median and quartiles of ln(q/q0) are
    taken across the segments that reach that day. Columns: t_days,
    ln_ratio_median, ln_ratio_q25, ln_ratio_q75, n.
    """
    t_grid = np.arange(skip_days, skip_days + n_points)
    curves = []
    for seg in segments:
        s = seg.set_index("t_days")["value"]
        if skip_days not in s.index or s.loc[skip_days] <= 0:
            continue
        ratio = np.log(s.reindex(t_grid).to_numpy() / s.loc[skip_days])
        curves.append(ratio)
    if not curves:
        return pd.DataFrame(columns=MRC_COLUMNS)
    m = np.vstack(curves)
    return pd.DataFrame(
        {
            "t_days": t_grid,
            "ln_ratio_median": np.nanmedian(m, axis=0),
            "ln_ratio_q25": np.nanpercentile(m, 25, axis=0),
            "ln_ratio_q75": np.nanpercentile(m, 75, axis=0),
            "n": np.sum(~np.isnan(m), axis=0),
        }
    )
