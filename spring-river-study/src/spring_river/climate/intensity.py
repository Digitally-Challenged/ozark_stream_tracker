"""Q3: precipitation regime indices per calendar year (spec §2.4) with a
coverage gate — a year missing >10% of days yields NaN, never a low total.

Phase 8 additions (review.md items 1 and 9). A monotone trend test cannot
distinguish a trend from a step, and AORC's inputs change at the 2002 radar
onset. `step_term_test` fits OLS index ~ year + I(year ≥ step) with HC3
errors so the two are separated; `era_slopes` gives the Sen slope within each
era; `era_means` compares pre/post means of two series over identical years;
`max_t_permutation_count` replaces the BH count with a family-wise test that
respects the (mean |r| ≈ 0.5) correlation among the ten indices.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm

from spring_river.stats.multiple import benjamini_hochberg
from spring_river.stats.trends import trend_test

INDEX_COLUMNS = ["total_in", "recharge_in", "growing_in", "days_ge_0p5", "days_ge_1", "days_ge_2",
                 "max1_in", "max3_in", "top5_frac", "sdii_in"]
WET_DAY_IN = 0.01
AORC_RADAR_YEAR = 2002   # AORC v1.1 gains radar (Stage IV/MRMS) input here
KUNO_SPLICE_YEAR = 1998  # West Plains COOP → KUNO instrument change


def annual_indices(precip: pd.DataFrame, min_coverage: float = 0.9) -> pd.DataFrame:
    s = precip.set_index("date")["pcpn_in"].sort_index().astype("float64")
    s = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="D"))
    rows = []
    for year in range(s.index.min().year, s.index.max().year + 1):
        y = s[str(year)]
        n_in_year = len(pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D"))
        cov = float(y.notna().sum() / n_in_year)
        row = {"year": year, "n_days": int(y.notna().sum()), "coverage": cov}
        if cov < min_coverage or y.dropna().empty:
            rows.append({**row, **{c: float("nan") for c in INDEX_COLUMNS}})
            continue
        # Recharge season coverage is judged against the full calendar span
        # Sep 1 (year-1) .. end of Feb (year), not against whatever days the
        # series happens to contain, so a series starting Jan 1 cannot pass
        # Jan-Feb alone as a complete season.
        rech_start, rech_end = pd.Timestamp(year - 1, 9, 1), pd.Timestamp(year, 2, 1) + pd.offsets.MonthEnd(0)
        rech = s.reindex(pd.date_range(rech_start, rech_end, freq="D"))
        rech_cov = float(rech.notna().sum() / len(rech))
        grow = s[f"{year}-03-01":f"{year}-08-31"]
        total = float(y.sum())
        wet = y[y >= WET_DAY_IN]
        # 3-day max within the calendar year only, so a storm straddling
        # Dec 31 / Jan 1 does not bleed into the following year.
        roll3 = y.rolling(3, min_periods=3).sum()
        rows.append({**row,
            "total_in": total,
            "recharge_in": float(rech.sum()) if rech_cov >= min_coverage else float("nan"),
            "growing_in": float(grow.sum()),
            "days_ge_0p5": int((y >= 0.5).sum()), "days_ge_1": int((y >= 1.0).sum()), "days_ge_2": int((y >= 2.0).sum()),
            "max1_in": float(y.max()), "max3_in": float(roll3.max()),
            "top5_frac": float(y.nlargest(5).sum() / total) if total > 0 else float("nan"),
            "sdii_in": float(total / len(wet)) if len(wet) else float("nan")})
    return pd.DataFrame(rows)


def index_trends(idx: pd.DataFrame, q: float = 0.05) -> pd.DataFrame:
    rows = []
    for c in INDEX_COLUMNS:
        d = idx.dropna(subset=[c])
        r = trend_test(d[c].to_numpy(dtype="float64"), d["year"].to_numpy(dtype="float64"))
        rows.append({"index": c, "n": r.n, "slope_per_decade": 10 * r.slope, "lo": 10 * r.slope_lo,
                     "hi": 10 * r.slope_hi, "z": r.z, "p": r.p})
    out = pd.DataFrame(rows)
    rejected, adj = benjamini_hochberg(out["p"].to_numpy(), q)
    return out.assign(p_bh=adj, significant_bh=rejected)


def step_term_test(idx: pd.DataFrame, step_year: int = AORC_RADAR_YEAR,
                   q: float = 0.05) -> pd.DataFrame:
    """OLS index ~ year + I(year ≥ step_year), HC3.

    Separates a monotone trend from a level shift at a known input change.
    `slope_*_per_decade` is the residual trend after the step is allowed for;
    `step` is the level shift in the index's own units.
    """
    rows = []
    for c in INDEX_COLUMNS:
        d = idx.dropna(subset=[c])
        if len(d) < 3 or d["year"].nunique() < 3:
            continue
        year = d["year"].to_numpy(dtype="float64")
        step = (year >= step_year).astype("float64")
        if step.min() == step.max():          # step outside the series' span
            continue
        X = sm.add_constant(np.column_stack([year, step]))
        r = sm.OLS(d[c].to_numpy(dtype="float64"), X).fit(cov_type="HC3")
        ci = np.asarray(r.conf_int())
        rows.append({"index": c, "n": int(r.nobs),
                     "slope_per_decade": 10 * float(r.params[1]),
                     "slope_lo_per_decade": 10 * float(ci[1, 0]),
                     "slope_hi_per_decade": 10 * float(ci[1, 1]),
                     "slope_p": float(r.pvalues[1]),
                     "step": float(r.params[2]),
                     "step_lo": float(ci[2, 0]), "step_hi": float(ci[2, 1]),
                     "step_p": float(r.pvalues[2])})
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    rejected, adj = benjamini_hochberg(out["step_p"].to_numpy(), q)
    return out.assign(step_p_bh=adj, step_significant_bh=rejected)


def era_slopes(idx: pd.DataFrame, split_year: int = AORC_RADAR_YEAR) -> pd.DataFrame:
    """Sen slope per decade within each era, split at `split_year`."""
    valid = idx.dropna(subset=["total_in"])
    if valid.empty:
        return pd.DataFrame()
    lo_yr, hi_yr = int(valid["year"].min()), int(valid["year"].max())
    eras = {f"{lo_yr}–{split_year - 1}": idx["year"] < split_year,
            f"{split_year}–{hi_yr}": idx["year"] >= split_year}
    rows = []
    for era, mask in eras.items():
        part = idx[mask]
        for c in INDEX_COLUMNS:
            d = part.dropna(subset=[c])
            row = {"era": era, "index": c, "n": len(d)}
            try:
                r = trend_test(d[c].to_numpy(dtype="float64"), d["year"].to_numpy(dtype="float64"))
            except ValueError:                 # n below the trend-test minimum
                rows.append({**row, "slope_per_decade": float("nan"), "lo": float("nan"),
                             "hi": float("nan"), "p": float("nan")})
                continue
            rows.append({**row, "slope_per_decade": 10 * r.slope, "lo": 10 * r.slope_lo,
                         "hi": 10 * r.slope_hi, "p": r.p})
    return pd.DataFrame(rows)


def era_means(indices: dict[str, pd.DataFrame], split_year: int = AORC_RADAR_YEAR) -> pd.DataFrame:
    """Pre/post-`split_year` means of each index for each series, over the
    years all the given series have in common — so a product-vs-gauge
    comparison is not a comparison of different periods."""
    common = None
    for df in indices.values():
        yrs = set(df.dropna(subset=["total_in"])["year"].astype(int))
        common = yrs if common is None else (common & yrs)
    common = common or set()
    rows = []
    for series, df in indices.items():
        d = df[df["year"].astype(int).isin(common)]
        for c in INDEX_COLUMNS:
            pre = d.loc[d["year"] < split_year, c].dropna()
            post = d.loc[d["year"] >= split_year, c].dropna()
            pre_m = float(pre.mean()) if len(pre) else float("nan")
            post_m = float(post.mean()) if len(post) else float("nan")
            rows.append({"series": series, "index": c, "n_pre": len(pre), "n_post": len(post),
                         "pre_mean": pre_m, "post_mean": post_m,
                         "pct_change": 100.0 * (post_m - pre_m) / pre_m if pre_m else float("nan")})
    return pd.DataFrame(rows)


def max_t_permutation_count(idx: pd.DataFrame, n_perm: int = 5000, seed: int = 0,
                            alpha: float = 0.05) -> tuple[int, pd.DataFrame]:
    """Family-wise max-T permutation across the ten indices.

    Year labels are permuted JOINTLY across indices, so the permutation null
    preserves the correlation between them (mean |r| ≈ 0.5 here) that a
    per-index BH correction ignores. Statistic is |Kendall tau| via the MK z.
    Returns (number of indices surviving, per-index table).
    """
    from spring_river.stats.trends import mann_kendall

    cols = [c for c in INDEX_COLUMNS if idx[c].notna().sum() >= 3]
    d = idx.dropna(subset=["total_in"]).sort_values("year").reset_index(drop=True)
    obs = {}
    for c in cols:
        v = d[c].to_numpy(dtype="float64")
        obs[c] = abs(mann_kendall(v[~np.isnan(v)])[1])
    rng = np.random.default_rng(seed)
    n = len(d)
    max_null = np.empty(n_perm)
    arrays = {c: d[c].to_numpy(dtype="float64") for c in cols}
    for i in range(n_perm):
        order = rng.permutation(n)             # one joint relabelling for all indices
        best = 0.0
        for c in cols:
            v = arrays[c][order]
            v = v[~np.isnan(v)]
            best = max(best, abs(mann_kendall(v)[1]))
        max_null[i] = best
    rows = [{"index": c, "abs_z": obs[c],
             "p_maxt": float((max_null >= obs[c]).mean()),
             "survives": bool((max_null >= obs[c]).mean() <= alpha)} for c in cols]
    tbl = pd.DataFrame(rows)
    return int(tbl["survives"].sum()), tbl
