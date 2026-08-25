import numpy as np
import pandas as pd

from spring_river.analysis.compare_sources import agreement_rows, to_markdown_table


def _daily(seed: int, scale: float) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    d = pd.date_range("2000-01-01", "2004-12-31", freq="D")
    return pd.DataFrame({"date": d, "pcpn_in": rng.gamma(0.5, scale, len(d))})


def test_agreement_rows_report_annual_r_and_ratio():
    a = _daily(0, 0.2)
    b = a.assign(pcpn_in=a["pcpn_in"] * 1.1)
    rows = agreement_rows("aorc", a, "prism_polygon", b)
    by = {r["metric"]: r for r in rows}
    assert by["annual_total_r"]["value"] > 0.99
    assert abs(by["annual_total_ratio"]["value"] - 1.1) < 1e-6
    assert by["daily_r"]["value"] > 0.99
    assert all(r["source"] == "aorc vs prism_polygon" and r["block"] == "agreement" for r in rows)
    assert by["annual_total_r"]["n"] == 5


def test_to_markdown_table_pivots_sources_wide():
    df = pd.DataFrame([
        {"source": "aorc", "block": "q3", "metric": "total_in slope/decade", "value": 2.0, "lo": 0.5, "hi": 3.5, "n": 45},
        {"source": "prism_buffer", "block": "q3", "metric": "total_in slope/decade", "value": 2.4, "lo": 0.4, "hi": 4.5, "n": 45},
    ])
    md = to_markdown_table(df)
    assert "| metric" in md and "aorc" in md and "prism_buffer" in md
    assert "2 (0.5 to 3.5; n=45)" in md and "2.4 (0.4 to 4.5; n=45)" in md
