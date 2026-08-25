import pytest
import pandas as pd

from spring_river.hydro.wateryear import min7, water_year


def test_water_year_boundaries():
    dates = pd.Series(pd.to_datetime(["2019-09-30", "2019-10-01", "2020-09-30"]))
    assert water_year(dates).tolist() == [2019, 2020, 2020]


def test_min7_finds_low_flow_window():
    dates = pd.date_range("2019-10-01", "2020-09-30", freq="D")
    values = pd.Series(500.0, index=range(len(dates)))
    values.iloc[300:307] = [100, 90, 80, 80, 80, 90, 100]  # 7-day low ~ 88.57
    df = pd.DataFrame({"date": dates, "value": values.values})
    out = min7(df)
    assert out.index.tolist() == [2020]
    assert abs(out.loc[2020] - (100 + 90 + 80 * 3 + 90 + 100) / 7) < 1e-9


def test_daily_max_stage_collapses_iv():
    from spring_river.hydro.wateryear import daily_max_stage

    iv = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                ["2020-01-01 00:15", "2020-01-01 12:00", "2020-01-02 06:00"]
            ),
            "value": [4.0, 9.5, 5.0],
            "approved": [True, False, True],
        }
    )
    out = daily_max_stage(iv)
    assert list(out.columns) == ["date", "value", "approved"]
    assert out["value"].tolist() == [9.5, 5.0]
    assert out["approved"].tolist() == [False, True]


def test_min7_nan_when_gap_at_minimum():
    dates = pd.date_range("2019-10-01", "2020-09-30", freq="D")
    values = pd.Series(500.0, index=range(len(dates)))
    values.iloc[300:307] = 50.0
    values.iloc[303] = float("nan")  # gap inside the minimum window
    df = pd.DataFrame({"date": dates, "value": values.values})
    # min over complete windows only; the NaN window must not silently win
    out = min7(df)
    assert out.loc[2020] >= 50.0  # computed from complete windows only


def test_daily_max_stage_tz_aware_raises():
    from spring_river.hydro.wateryear import daily_max_stage

    iv = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                ["2020-01-01 00:15", "2020-01-01 12:00"]
            ).tz_localize("US/Central"),
            "value": [4.0, 9.5],
            "approved": [True, False],
        }
    )
    with pytest.raises(ValueError, match="datetime must be tz-naive"):
        daily_max_stage(iv)
