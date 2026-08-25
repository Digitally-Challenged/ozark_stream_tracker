import pandas as pd

from spring_river.qa.gaps import approval_summary, find_gaps


def _series_with_gap() -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", "2020-02-29", freq="D")
    df = pd.DataFrame({"date": dates, "value": 100.0, "approved": True})
    # 10-day NaN run (> 7 flag threshold)
    df.loc[10:19, "value"] = pd.NA
    # 3-day NaN run (below threshold)
    df.loc[40:42, "value"] = pd.NA
    # drop 9 calendar days entirely (missing rows count as a gap too)
    return df.drop(index=range(25, 34)).reset_index(drop=True)


def test_find_gaps_flags_long_runs_only():
    gaps = find_gaps(_series_with_gap(), max_days=7)
    assert list(gaps.columns) == ["gap_start", "gap_end", "days"]
    assert len(gaps) == 2  # the 10-day NaN run and the 9 missing days
    assert set(gaps["days"]) == {10, 9}


def test_approval_summary():
    df = pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=4),
            "value": 1.0,
            "approved": [True, True, False, False],
        }
    )
    out = approval_summary(df)
    assert out["approved_frac"] == 0.5
    assert out["provisional_from"] == pd.Timestamp("2020-01-03")
