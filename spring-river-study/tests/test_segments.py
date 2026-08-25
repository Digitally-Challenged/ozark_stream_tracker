import numpy as np
import pandas as pd

from spring_river.hydro.segments import segment_gapfree


def _frame(values, start="2020-01-01"):
    dates = pd.date_range(start, periods=len(values), freq="D")
    return pd.DataFrame({"date": dates, "value": values, "approved": True})


def test_short_gap_is_interpolated():
    v = [10.0, np.nan, np.nan, 40.0]
    segs = segment_gapfree(_frame(v))
    assert len(segs) == 1
    assert segs[0]["value"].tolist() == [10.0, 20.0, 30.0, 40.0]


def test_long_gap_splits_segments():
    v = [1.0] * 5 + [np.nan] * 8 + [2.0] * 5
    segs = segment_gapfree(_frame(v))
    assert len(segs) == 2
    assert len(segs[0]) == 5 and len(segs[1]) == 5
    assert segs[1]["date"].iloc[0] == pd.Timestamp("2020-01-14")


def test_missing_rows_count_as_gap():
    df = _frame([1.0] * 5)
    later = _frame([2.0] * 5, start="2020-02-01")
    segs = segment_gapfree(pd.concat([df, later]))
    assert len(segs) == 2
