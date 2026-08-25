import numpy as np
import pandas as pd

from spring_river.climate.intensity import INDEX_COLUMNS, annual_indices, index_trends


def _precip(years=range(1990, 2020), seed=0):
    rng = np.random.default_rng(seed)
    d = pd.date_range(f"{min(years)}-01-01", f"{max(years)}-12-31", freq="D")
    p = np.where(rng.random(len(d)) < 0.25, rng.exponential(0.4, len(d)), 0.0)
    return pd.DataFrame({"date": d, "pcpn_in": p})


def test_annual_indices_shape_and_values():
    idx = annual_indices(_precip())
    assert list(idx.columns) == ["year", "n_days", "coverage"] + INDEX_COLUMNS
    row = idx[idx["year"] == 2000].iloc[0]
    assert row["coverage"] == 1.0
    assert row["days_ge_0p5"] >= row["days_ge_1"] >= row["days_ge_2"]
    assert row["max3_in"] >= row["max1_in"]
    assert 0 < row["top5_frac"] < 1


def test_coverage_gate_nulls_indices():
    p = _precip()
    p.loc[(p["date"].dt.year == 2005) & (p["date"].dt.month <= 3), "pcpn_in"] = np.nan
    idx = annual_indices(p, min_coverage=0.9)
    row = idx[idx["year"] == 2005].iloc[0]
    assert row["coverage"] < 0.9 and np.isnan(row["total_in"])


def test_index_trends_has_bh_column():
    tr = index_trends(annual_indices(_precip()))
    assert set(tr["index"]) == set(INDEX_COLUMNS)
    assert {"slope_per_decade", "lo", "hi", "p_bh", "significant_bh"} <= set(tr.columns)
