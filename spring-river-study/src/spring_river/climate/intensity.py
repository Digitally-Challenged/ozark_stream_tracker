"""Q3: precipitation regime indices per calendar year (spec §2.4) with a
coverage gate — a year missing >10% of days yields NaN, never a low total."""
import numpy as np
import pandas as pd

from spring_river.stats.multiple import benjamini_hochberg
from spring_river.stats.trends import trend_test

INDEX_COLUMNS = ["total_in", "recharge_in", "growing_in", "days_ge_0p5", "days_ge_1", "days_ge_2",
                 "max1_in", "max3_in", "top5_frac", "sdii_in"]
WET_DAY_IN = 0.01


def annual_indices(precip: pd.DataFrame, min_coverage: float = 0.9) -> pd.DataFrame:
    s = precip.set_index("date")["pcpn_in"].sort_index().astype("float64")
    s = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="D"))
    roll3 = s.rolling(3, min_periods=3).sum()
    rows = []
    for year in range(s.index.min().year, s.index.max().year + 1):
        y = s[str(year)]
        n_in_year = len(pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D"))
        cov = float(y.notna().sum() / n_in_year)
        row = {"year": year, "n_days": int(y.notna().sum()), "coverage": cov}
        if cov < min_coverage or y.dropna().empty:
            rows.append({**row, **{c: float("nan") for c in INDEX_COLUMNS}})
            continue
        rech = s[f"{year - 1}-09-01":f"{year}-02-28"]
        grow = s[f"{year}-03-01":f"{year}-08-31"]
        total = float(y.sum())
        wet = y[y >= WET_DAY_IN]
        rows.append({**row,
            "total_in": total,
            "recharge_in": float(rech.sum()) if rech.notna().mean() >= min_coverage else float("nan"),
            "growing_in": float(grow.sum()),
            "days_ge_0p5": int((y >= 0.5).sum()), "days_ge_1": int((y >= 1.0).sum()), "days_ge_2": int((y >= 2.0).sum()),
            "max1_in": float(y.max()), "max3_in": float(roll3[str(year)].max()),
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
