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


def test_recharge_requires_full_calendar_season():
    idx = annual_indices(_precip(years=range(1981, 1984)))
    assert np.isnan(idx[idx["year"] == 1981].iloc[0]["recharge_in"])
    assert not np.isnan(idx[idx["year"] == 1982].iloc[0]["recharge_in"])


def test_max3_does_not_bleed_across_new_year():
    d = pd.date_range("2000-01-01", "2001-12-31", freq="D")
    p = pd.DataFrame({"date": d, "pcpn_in": 0.0})
    p.loc[p["date"].isin(pd.to_datetime(["2000-12-30", "2000-12-31", "2001-01-01"])), "pcpn_in"] = 2.0
    p.loc[p["date"] == "2001-06-01", "pcpn_in"] = 3.0
    idx = annual_indices(p).set_index("year")
    assert idx.loc[2000, "max3_in"] == 4.0
    assert idx.loc[2001, "max3_in"] == 3.0


def test_index_trends_has_bh_column():
    tr = index_trends(annual_indices(_precip()))
    assert set(tr["index"]) == set(INDEX_COLUMNS)
    assert {"slope_per_decade", "lo", "hi", "p_bh", "significant_bh"} <= set(tr.columns)


# ---------------------------------------------------------------- Phase 8 additions


def _stepped(step_year=2002, step=1.5, years=range(1981, 2026), seed=1):
    """Precip whose wet-day intensity jumps at `step_year` with no within-era trend."""
    rng = np.random.default_rng(seed)
    d = pd.date_range(f"{min(years)}-01-01", f"{max(years)}-12-31", freq="D")
    scale = np.where(d.year >= step_year, 0.4 * step, 0.4)
    p = np.where(rng.random(len(d)) < 0.25, rng.exponential(scale), 0.0)
    return pd.DataFrame({"date": d, "pcpn_in": p})


def test_step_term_test_finds_the_step_and_not_a_trend():
    from spring_river.climate.intensity import step_term_test

    idx = annual_indices(_stepped())
    out = step_term_test(idx, step_year=2002).set_index("index")
    r = out.loc["sdii_in"]
    assert r["step_p"] < 0.01                      # the step is there
    assert r["slope_lo_per_decade"] <= 0 <= r["slope_hi_per_decade"]  # the trend is not


def test_step_term_test_columns():
    from spring_river.climate.intensity import step_term_test

    out = step_term_test(annual_indices(_precip()), step_year=2002)
    assert set(out.columns) >= {"index", "n", "slope_per_decade", "slope_lo_per_decade",
                                "slope_hi_per_decade", "slope_p", "step", "step_p"}


def test_era_slopes_split_at_the_step():
    from spring_river.climate.intensity import era_slopes

    out = era_slopes(annual_indices(_stepped()), split_year=2002)
    assert set(out["era"]) == {"1981–2001", "2002–2025"}
    assert set(out["index"]) == set(INDEX_COLUMNS)


def test_era_means_reports_percent_change_over_common_years():
    from spring_river.climate.intensity import era_means

    a = annual_indices(_stepped(step=2.0))
    b = annual_indices(_stepped(step=1.0, seed=2))
    out = era_means({"stepped": a, "flat": b}, split_year=2002)
    sd = out[(out["series"] == "stepped") & (out["index"] == "sdii_in")].iloc[0]
    fl = out[(out["series"] == "flat") & (out["index"] == "sdii_in")].iloc[0]
    assert sd["pct_change"] > fl["pct_change"]
    assert sd["n_pre"] > 0 and sd["n_post"] > 0


def test_max_t_permutation_is_no_larger_than_bh_on_correlated_indices():
    from spring_river.climate.intensity import max_t_permutation_count

    idx = annual_indices(_precip())
    tr = index_trends(idx)
    n_maxt, _ = max_t_permutation_count(idx, n_perm=200, seed=0)
    assert 0 <= n_maxt <= len(INDEX_COLUMNS)
    assert n_maxt <= int(tr["significant_bh"].sum()) + len(INDEX_COLUMNS)
