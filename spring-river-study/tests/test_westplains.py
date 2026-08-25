"""West Plains two-instrument daily record: COOP through Mar 1998, then KUNO.

Each period's value is a real measurement from that period's own instrument.
The airport gauge is raised by the measured COOP/KUNO catch ratio so the whole
record sits on the town gauge's level; nothing else is adjusted. No day is
borrowed between gauges: a day the period's instrument missed stays NaN.
"""
import numpy as np
import pandas as pd
import pytest

from spring_river.climate import westplains


def _days(start: str, n: int) -> pd.DatetimeIndex:
    return pd.date_range(start, periods=n, freq="D")


def _frame(start: str, values) -> pd.DataFrame:
    return pd.DataFrame({"date": _days(start, len(values)), "pcpn_in": list(values)})


def test_catch_ratio_uses_only_months_complete_at_both_stations():
    # Two complete months (Jan 31 d, Feb 28 d in 2001) plus a partial March
    # that must be excluded. COOP reads 1.5x KUNO on the complete months.
    coop = _frame("2001-01-01", [0.3] * 59 + [9.0] * 5)
    kuno = _frame("2001-01-01", [0.2] * 59 + [0.1] * 5)
    assert westplains.catch_ratio(coop, kuno) == pytest.approx(1.5)


def test_catch_ratio_ignores_months_with_missing_days():
    coop = _frame("2001-01-01", [0.3] * 31 + [np.nan] * 10 + [0.3] * 18)
    kuno = _frame("2001-01-01", [0.2] * 59)
    # Only January qualifies at both stations.
    assert westplains.catch_ratio(coop, kuno) == pytest.approx(1.5)


def test_boundary_day_switches_to_scaled_kuno():
    coop = _frame("1998-03-30", [1.0, 2.0, 3.0, 4.0])
    kuno = _frame("1998-03-30", [10.0, 20.0, 30.0, 40.0])
    out = westplains.splice(coop, kuno, ratio=2.0, kuno_start="1998-04-01")
    assert list(out["source"]) == ["coop", "coop", "kuno", "kuno"]
    assert list(out["pcpn_in"]) == [1.0, 2.0, 60.0, 80.0]


def test_coop_era_values_are_never_scaled():
    coop = _frame("1998-03-31", [2.5])
    kuno = _frame("1998-04-01", [4.0])
    out = westplains.splice(coop, kuno, ratio=1.068)
    assert out["pcpn_in"].iloc[0] == 2.5
    assert out["pcpn_in"].iloc[1] == pytest.approx(4.272)


def test_no_fallback_to_coop_after_the_boundary():
    coop = _frame("1998-04-01", [1.0, 5.0])
    kuno = _frame("1998-04-01", [10.0, np.nan])
    out = westplains.splice(coop, kuno, ratio=2.0)
    assert list(out["source"]) == ["kuno", "none"]
    assert out["pcpn_in"].iloc[0] == 20.0
    assert np.isnan(out["pcpn_in"].iloc[1])


def test_missing_coop_day_before_the_boundary_stays_nan():
    coop = _frame("1998-03-29", [1.0, np.nan, 3.0])
    kuno = _frame("1998-03-29", [9.0, 9.0, 9.0])
    out = westplains.splice(coop, kuno, ratio=1.0, kuno_start="1998-04-01")
    assert list(out["source"]) == ["coop", "none", "coop"]
    assert np.isnan(out["pcpn_in"].iloc[1])


def test_index_is_complete_daily_to_the_later_last_date():
    coop = _frame("1998-01-01", [1.0, 2.0])  # ends 1998-01-02
    kuno = pd.DataFrame({"date": [pd.Timestamp("1998-04-05")], "pcpn_in": [7.0]})
    out = westplains.splice(coop, kuno, ratio=1.0, kuno_start="1998-04-01")
    expect = pd.date_range("1998-01-01", "1998-04-05", freq="D")
    assert list(out["date"]) == list(expect)
    assert len(out) == len(expect)
    assert out.loc[out["date"] == pd.Timestamp("1998-02-15"), "pcpn_in"].isna().all()
    assert out["pcpn_in"].iloc[-1] == 7.0


def test_returns_the_documented_columns():
    coop = _frame("1998-01-01", [1.0])
    kuno = _frame("1998-04-01", [1.0])
    out = westplains.splice(coop, kuno, ratio=1.0)
    assert list(out.columns) == ["date", "pcpn_in", "source"]
    assert set(out["source"]) <= {"coop", "kuno", "none"}
