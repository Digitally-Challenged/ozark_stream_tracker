import math

import pandas as pd

import pytest

from spring_river.ingest.prism import _bbox_around, _mean_grid_series, _year_chunks


def test_bbox_around_west_plains():
    w, s, e, n = _bbox_around(36.7439, -91.8524, 30)
    assert s < 36.7439 < n
    assert w < -91.8524 < e
    # 30 km of latitude ~ 0.27 deg
    assert math.isclose(n - s, 2 * 30 / 111.32, rel_tol=1e-3)


def test_mean_grid_series_ignores_missing_cells():
    payload = {
        "data": [
            ["2020-01-01", [[0.5, 0.7], [-999, 0.9]]],
            ["2020-01-02", [[-999, -999], [-999, -999]]],
        ]
    }
    out = _mean_grid_series(payload)
    assert list(out.columns) == ["date", "pcpn_in"]
    assert math.isclose(out["pcpn_in"].iloc[0], (0.5 + 0.7 + 0.9) / 3)
    assert pd.isna(out["pcpn_in"].iloc[1])


def test_year_chunks_mid_year_multi_year():
    assert _year_chunks("2019-11-01", "2021-02-01") == [
        ("2019-11-01", "2019-12-31"),
        ("2020-01-01", "2020-12-31"),
        ("2021-01-01", "2021-02-01"),
    ]


def test_year_chunks_single_month_same_year():
    assert _year_chunks("2024-01-01", "2024-01-31") == [
        ("2024-01-01", "2024-01-31"),
    ]


def test_year_chunks_end_before_start_raises():
    with pytest.raises(ValueError):
        _year_chunks("2024-02-01", "2024-01-01")


def test_mean_grid_series_empty_payload():
    out = _mean_grid_series({"data": []})
    assert list(out.columns) == ["date", "pcpn_in"]
    assert out["date"].dtype == "datetime64[ns]"
    assert out["pcpn_in"].dtype == "float64"
    assert len(out) == 0
