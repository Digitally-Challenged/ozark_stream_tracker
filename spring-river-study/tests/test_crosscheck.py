import numpy as np
import pandas as pd

from spring_river.qa.crosscheck import hardy_vs_imboden, precip_overlap


def test_hardy_vs_imboden_flags_planted_outlier():
    rng = np.random.default_rng(1)
    dates = pd.date_range("2020-01-01", periods=400, freq="D")
    imboden = pd.Series(10 ** rng.normal(3, 0.4, size=400))
    hardy = imboden * 0.6 * 10 ** rng.normal(0, 0.02, size=400)
    hardy.iloc[200] *= 40  # planted bad Hardy value
    h = pd.DataFrame({"date": dates, "value": hardy.values})
    i = pd.DataFrame({"date": dates, "value": imboden.values})
    out = hardy_vs_imboden(h, i)
    z = (out["residual"] - out["residual"].mean()) / out["residual"].std()
    assert dates[200] in set(out.loc[z.abs() > 4, "date"])


def test_precip_overlap_stats():
    dates = pd.date_range("2020-01-01", periods=100, freq="D")
    a = pd.DataFrame({"date": dates, "pcpn_in": np.linspace(0, 1, 100)})
    b = pd.DataFrame({"date": dates, "pcpn_in": np.linspace(0, 1, 100) * 1.1})
    out = precip_overlap(a, b)
    assert out["n_days"] == 100
    assert out["corr"] > 0.99
    assert 1.05 < out["mean_ratio"] < 1.15  # b/a
