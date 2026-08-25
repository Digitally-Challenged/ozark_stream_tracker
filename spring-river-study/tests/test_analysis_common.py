import pandas as pd

from spring_river.analysis.common import approval_variants, caption, fmt_trend, sensitivity_lines
from spring_river.stats.trends import TrendResult


def _df():
    d = pd.date_range("2020-01-01", periods=10, freq="D")
    return pd.DataFrame({"date": d, "value": 1.0, "approved": [True] * 7 + [False] * 3})


def test_approval_variants():
    v = approval_variants(_df())
    assert len(v["all"]) == 10 and len(v["approved"]) == 7


def test_caption_mentions_provisional():
    c = caption("USGS DV", _df())
    assert "period 2020-01-01–2020-01-10" in c and "approved 70%" in c and "provisional from 2020-01-08" in c


def test_fmt_trend_has_ci_and_n():
    r = TrendResult(30, 10, 1.5, 0.13, -2.0, -4.5, 0.4, 100)
    s = fmt_trend(r, "cfs")
    assert "-2 cfs/yr" in s and "95% CI -4.5 to 0.4" in s and "n=30" in s


def test_sensitivity_flags_sign_change():
    a = TrendResult(30, 10, 1.5, 0.13, -2.0, -4.5, 0.4, 100)
    b = TrendResult(28, -3, -0.5, 0.6, 0.5, -1.0, 2.0, 100)
    lines = sensitivity_lines("min7", a, b)
    assert any("CHANGED" in l for l in lines)
    assert not any("CHANGED" in l for l in sensitivity_lines("min7", a, a))
