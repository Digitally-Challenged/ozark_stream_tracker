import numpy as np
import pandas as pd

from spring_river.hydro.pot import annual_counts, dispersion_test, pot_events


def _stage():
    d = pd.date_range("2019-10-01", periods=400, freq="D")
    v = np.full(400, 5.0)
    v[10:13] = 9.0           # event 1
    v[15:16] = 8.5           # 2 days later -> merged into event 1
    v[100:101] = 12.0        # event 2
    v[370:372] = 8.2         # event 3 (2020-10-05, WY 2021)
    return pd.DataFrame({"date": d, "value": v, "approved": True})


def test_declustering_merges_close_exceedances():
    ev = pot_events(_stage(), threshold=8.0, min_sep_days=7)
    assert len(ev) == 3
    assert ev.iloc[0]["peak_value"] == 9.0
    assert ev.iloc[0]["end"] == pd.Timestamp("2019-10-16")


def test_annual_counts_fills_zero_years():
    ev = pot_events(_stage(), threshold=8.0)
    c = annual_counts(ev, [2020, 2021, 2022])
    assert c.tolist() == [2, 1, 0]


def test_dispersion_test_poisson_like():
    rng = np.random.default_rng(0)
    c = pd.Series(rng.poisson(2.0, 40))
    r = dispersion_test(c)
    assert 0.5 < r["dispersion"] < 1.6 and r["p"] > 0.01
