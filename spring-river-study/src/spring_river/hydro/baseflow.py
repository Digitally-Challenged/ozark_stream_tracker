"""Eckhardt recursive base-flow filter (spec §2.2) plus the Lyne-Hollick
check, gap-segmented filtering, and trend-safe BFI by water year (Phase 4)."""
import numpy as np
import pandas as pd

from spring_river.hydro.segments import segment_gapfree
from spring_river.hydro.wateryear import water_year


def eckhardt(q: np.ndarray, alpha: float = 0.98, bfi_max: float = 0.8) -> np.ndarray:
    """Recursive base-flow filter.

    Raises ValueError if q contains NaN; segment or drop gaps before filtering
    (project rule: never interpolate across gaps > 7 days).
    """
    q = np.asarray(q, dtype="float64")
    if len(q) == 0:
        return np.empty(0, dtype="float64")
    if np.isnan(q).any():
        raise ValueError("q contains NaN; segment or drop gaps before filtering")
    b = np.empty_like(q)
    b[0] = q[0] * bfi_max
    denom = 1.0 - alpha * bfi_max
    for t in range(1, len(q)):
        b[t] = ((1 - bfi_max) * alpha * b[t - 1] + (1 - alpha) * bfi_max * q[t]) / denom
        b[t] = min(b[t], q[t])
    return b


def bfi(q: np.ndarray, **kw) -> float:
    """Base Flow Index: sum(eckhardt(q)) / sum(q).

    Returns nan when total flow is zero or q is empty.
    """
    q = np.asarray(q, dtype="float64")
    total = q.sum()
    if total == 0.0:
        return float("nan")
    return float(eckhardt(q, **kw).sum() / total)


def lyne_hollick(q: np.ndarray, alpha: float = 0.925, passes: int = 3) -> np.ndarray:
    """Lyne-Hollick one-parameter filter, forward/backward passes (check on Eckhardt)."""
    q = np.asarray(q, dtype="float64")
    if len(q) == 0:
        return np.empty(0, dtype="float64")
    if np.isnan(q).any():
        raise ValueError("q contains NaN; segment or drop gaps before filtering")
    b = q.copy()
    for p in range(passes):
        src = b if p % 2 == 0 else b[::-1]
        quick = np.zeros_like(src)
        for t in range(1, len(src)):
            quick[t] = alpha * quick[t - 1] + (1 + alpha) / 2 * (src[t] - src[t - 1])
            quick[t] = min(max(quick[t], 0.0), src[t])
        base = src - quick
        b = base if p % 2 == 0 else base[::-1]
    return np.clip(b, 0.0, q)


def eckhardt_segmented(df: pd.DataFrame, spinup_days: int = 30, **kw) -> pd.DataFrame:
    """Eckhardt on each gap-free segment; filter state resets at every gap
    boundary (> 7 days); first `spinup_days` of each segment set to NaN."""
    frames = []
    for seg in segment_gapfree(df):
        b = eckhardt(seg["value"].to_numpy(), **kw)
        b[:spinup_days] = float("nan")
        frames.append(seg.assign(baseflow=b))
    if not frames:
        return pd.DataFrame({"date": pd.Series(dtype="datetime64[ns]"), "value": [], "baseflow": []})
    return pd.concat(frames, ignore_index=True)


def bfi_by_wy(df: pd.DataFrame, min_days: int = 300, method: str = "eckhardt") -> pd.Series:
    """Trend-safe annual BFI: sum(baseflow)/sum(flow) over days with a defined
    baseflow; NaN when fewer than `min_days` such days in the water year."""
    if method == "eckhardt":
        bf = eckhardt_segmented(df)
    elif method == "lyne_hollick":
        frames = []
        for seg in segment_gapfree(df):
            b = lyne_hollick(seg["value"].to_numpy())
            b[:30] = float("nan")
            frames.append(seg.assign(baseflow=b))
        bf = pd.concat(frames, ignore_index=True)
    else:
        raise ValueError(f"unknown method {method}")
    bf = bf.assign(wy=water_year(bf["date"]))
    ok = bf.dropna(subset=["baseflow"])
    g = ok.groupby("wy")
    out = g["baseflow"].sum() / g["value"].sum()
    out[g.size() < min_days] = float("nan")
    return out.reindex(sorted(bf["wy"].unique())).rename("bfi")
