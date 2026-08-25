"""West Plains composite station series: COOP spliced with KUNO ASOS.

The composite substitutes a co-located measurement for missing volunteer
readings. It never interpolates: a day missing at both stations stays NaN.
"""
import numpy as np
import pandas as pd
import pytest

from spring_river.climate import composite


def _days(start: str, n: int) -> pd.DatetimeIndex:
    return pd.date_range(start, periods=n, freq="D")


def _frame(start: str, values) -> pd.DataFrame:
    return pd.DataFrame({"date": _days(start, len(values)), "pcpn_in": list(values)})


def test_catch_ratio_uses_only_months_complete_at_both_stations():
    # Two complete months (Jan 31 d, Feb 28 d in 2001) plus a partial March
    # that must be excluded. COOP reads 1.5x KUNO on the complete months.
    coop = _frame("2001-01-01", [0.3] * 59 + [9.0] * 5)
    kuno = _frame("2001-01-01", [0.2] * 59 + [0.1] * 5)
    r = composite.catch_ratio(coop, kuno)
    assert r == pytest.approx(1.5)


def test_catch_ratio_ignores_months_with_missing_days():
    coop = _frame("2001-01-01", [0.3] * 31 + [np.nan] * 10 + [0.3] * 18)
    kuno = _frame("2001-01-01", [0.2] * 59)
    # Only January qualifies at both stations.
    assert composite.catch_ratio(coop, kuno) == pytest.approx(1.5)


def test_splice_prefers_coop_before_kuno_start():
    coop = _frame("1998-03-30", [1.0, 2.0, 3.0, 4.0])
    kuno = _frame("1998-03-30", [10.0, 20.0, 30.0, 40.0])
    out = composite.splice(coop, kuno, ratio=2.0, kuno_start="1998-04-01")
    assert list(out["source"]) == ["coop", "coop", "kuno", "kuno"]
    assert list(out["pcpn_in"]) == [1.0, 2.0, 60.0, 80.0]


def test_splice_falls_back_to_unscaled_coop_when_kuno_missing():
    coop = _frame("1998-04-01", [1.0, 5.0])
    kuno = _frame("1998-04-01", [10.0, np.nan])
    out = composite.splice(coop, kuno, ratio=2.0, kuno_start="1998-04-01")
    assert list(out["source"]) == ["kuno", "coop"]
    assert list(out["pcpn_in"]) == [20.0, 5.0]


def test_splice_never_interpolates_a_day_missing_at_both_stations():
    coop = _frame("1998-04-01", [1.0, np.nan, 3.0])
    kuno = _frame("1998-04-01", [np.nan, np.nan, 6.0])
    out = composite.splice(coop, kuno, ratio=1.0, kuno_start="1998-04-01")
    assert list(out["source"]) == ["coop", "none", "kuno"]
    assert out["pcpn_in"].iloc[0] == 1.0
    assert np.isnan(out["pcpn_in"].iloc[1])
    assert out["pcpn_in"].iloc[2] == 6.0


def test_splice_index_is_complete_daily_to_the_later_last_date():
    coop = _frame("1998-01-01", [1.0, 2.0])  # ends 1998-01-02
    kuno = pd.DataFrame({"date": [pd.Timestamp("1998-04-05")], "pcpn_in": [7.0]})
    out = composite.splice(coop, kuno, ratio=1.0, kuno_start="1998-04-01")
    expect = pd.date_range("1998-01-01", "1998-04-05", freq="D")
    assert list(out["date"]) == list(expect)
    assert len(out) == len(expect)
    # The uncovered middle is NaN, not filled.
    assert out.loc[out["date"] == pd.Timestamp("1998-02-15"), "pcpn_in"].isna().all()
    assert out["pcpn_in"].iloc[-1] == 7.0


def test_splice_returns_the_documented_columns():
    coop = _frame("1998-01-01", [1.0])
    kuno = _frame("1998-04-01", [1.0])
    out = composite.splice(coop, kuno, ratio=1.0)
    assert list(out.columns) == ["date", "pcpn_in", "source"]
