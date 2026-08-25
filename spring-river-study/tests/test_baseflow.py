import math

import numpy as np
import pytest

from spring_river.hydro.baseflow import bfi, eckhardt


def test_eckhardt_never_exceeds_streamflow():
    rng = np.random.default_rng(7)
    q = np.exp(rng.normal(5, 1, size=500))
    b = eckhardt(q)
    assert np.all(b <= q + 1e-9)
    assert np.all(b >= 0)


def test_constant_flow_converges_to_bfi_max():
    q = np.full(400, 250.0)
    b = eckhardt(q, bfi_max=0.8)
    # fixed point of the recursion under constant flow is bfi_max * q
    assert abs(b[-1] - 0.8 * 250.0) < 1e-6


def test_bfi_between_0_and_1():
    rng = np.random.default_rng(7)
    q = np.exp(rng.normal(5, 1, size=500))
    assert 0 < bfi(q) < 1


def test_eckhardt_empty_input():
    b = eckhardt(np.array([]))
    assert len(b) == 0


def test_bfi_empty_input():
    result = bfi(np.array([]))
    assert math.isnan(result)


def test_bfi_all_zero():
    q = np.zeros(10)
    result = bfi(q)
    assert math.isnan(result)


def test_eckhardt_nan_raises():
    q = np.array([100.0, 200.0, float("nan"), 150.0])
    with pytest.raises(ValueError, match="q contains NaN"):
        eckhardt(q)


# --- Task 3: segmented filtering and BFI by water year ---

import pandas as pd  # noqa: E402

from spring_river.hydro.baseflow import bfi_by_wy, eckhardt_segmented, lyne_hollick  # noqa: E402


def test_lyne_hollick_bounded():
    rng = np.random.default_rng(2)
    q = np.exp(rng.normal(5, 1, size=400))
    b = lyne_hollick(q)
    assert np.all(b <= q + 1e-9) and np.all(b >= 0)


def test_eckhardt_segmented_resets_and_spins_up():
    dates = pd.date_range("2019-10-01", periods=400, freq="D")
    v = np.full(400, 300.0)
    v[100:120] = np.nan  # 20-day gap -> two segments
    df = pd.DataFrame({"date": dates, "value": v, "approved": True})
    out = eckhardt_segmented(df, spinup_days=30)
    # Output holds only gap-free segment rows (380), so align by date to
    # check positions in the original calendar.
    assert len(out) == 380
    b = out.set_index("date")["baseflow"].reindex(dates)
    assert b.iloc[:30].isna().all()  # spin-up of segment 1
    assert b.iloc[30:100].notna().all()  # filtered part of segment 1
    assert b.iloc[100:120].isna().all()  # gap itself (rows absent)
    assert b.iloc[120:150].isna().all()  # spin-up of segment 2
    assert b.iloc[150:].notna().all()
    assert abs(b.iloc[-1] - 0.8 * 300.0) < 1e-6


def test_bfi_by_wy_requires_min_days():
    dates = pd.date_range("2019-10-01", "2021-09-30", freq="D")
    df = pd.DataFrame({"date": dates, "value": 300.0, "approved": True})
    s = bfi_by_wy(df, min_days=300)
    assert set(s.index) == {2020, 2021}
    assert 0 < s.loc[2021] <= 1
    short = df[df["date"] < "2020-03-01"]
    assert np.isnan(bfi_by_wy(short, min_days=300).loc[2020])
