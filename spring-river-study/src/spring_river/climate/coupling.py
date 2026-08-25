"""Monthly basin precip vs monthly spring/river flow, lags 0–12 months →
aquifer response time (spec §2.4). Anomalies (climatology removed) so the
shared seasonal cycle does not masquerade as coupling."""
import numpy as np
import pandas as pd


def monthly_series(precip: pd.DataFrame, dv_q: pd.DataFrame, min_days: int = 25) -> pd.DataFrame:
    p = precip.set_index("date")["pcpn_in"].astype("float64")
    q = dv_q.set_index("date")["value"].astype("float64")
    pm = p.resample("MS").agg(["sum", "count"])
    qm = q.resample("MS").agg(["mean", "count"])
    idx = pm.index.union(qm.index)
    out = pd.DataFrame({"month": idx})
    out["p_in"] = pm["sum"].where(pm["count"] >= min_days).reindex(idx).to_numpy()
    out["q_cfs"] = qm["mean"].where(qm["count"] >= min_days).reindex(idx).to_numpy()
    return out.reset_index(drop=True)


def _anomalies(m: pd.DataFrame) -> pd.DataFrame:
    d = m.copy()
    mon = d["month"].dt.month
    d["p_a"] = d["p_in"] - d.groupby(mon)["p_in"].transform("mean")
    lq = np.log(d["q_cfs"])
    d["q_a"] = lq - lq.groupby(mon).transform("mean")
    return d


def _lag_r(d: pd.DataFrame, lag: int) -> tuple[float, int]:
    x = d["p_a"].shift(lag)
    ok = x.notna() & d["q_a"].notna()
    if ok.sum() < 24:
        return float("nan"), int(ok.sum())
    return float(np.corrcoef(x[ok], d["q_a"][ok])[0, 1]), int(ok.sum())


def lag_correlation(m: pd.DataFrame, max_lag: int = 12, n_boot: int = 1000, seed: int = 0) -> pd.DataFrame:
    d = _anomalies(m)
    rng = np.random.default_rng(seed)
    n_blocks = len(d) // 12
    rows = []
    for lag in range(max_lag + 1):
        r, n = _lag_r(d, lag)
        boots = []
        for _ in range(n_boot):
            starts = rng.integers(0, len(d) - 12, n_blocks)
            sample = pd.concat([d.iloc[s : s + 12] for s in starts], ignore_index=True)
            boots.append(_lag_r(sample, lag)[0])
        boots = np.array([b for b in boots if not np.isnan(b)])
        lo, hi = (np.percentile(boots, [2.5, 97.5]) if len(boots) else (float("nan"), float("nan")))
        rows.append({"lag": lag, "r": r, "r_lo": float(min(lo, r)), "r_hi": float(max(hi, r)), "n": n})
    return pd.DataFrame(rows)


def response_lag(lc: pd.DataFrame) -> int:
    return int(lc.loc[lc["r"].idxmax(), "lag"])
