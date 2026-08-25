import json
import math

import numpy as np
import pandas as pd

import pytest

from shapely.geometry import Polygon

from spring_river.ingest import cache
from spring_river.ingest.prism import (
    _bbox_around,
    _grid_latlon,
    _mean_grid_series,
    _polygon_mask_from_meta,
    _year_chunks,
    get_basin_pcpn,
)


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


def test_grid_latlon_from_meta():
    payload = {"meta": {"lat": [[36.5, 36.5], [36.6, 36.6]], "lon": [[-91.8, -91.7], [-91.8, -91.7]]}, "data": []}
    lat, lon = _grid_latlon(payload)
    assert lat.shape == lon.shape == (2, 2)
    assert lat[1, 0] == 36.6 and lon[0, 1] == -91.7


def test_polygon_mask_from_meta_selects_inside_cells():
    payload = {"meta": {"lat": [[36.5, 36.5], [36.6, 36.6]], "lon": [[-91.8, -91.7], [-91.8, -91.7]]}, "data": []}
    poly = Polygon([(-91.75, 36.55), (-91.65, 36.55), (-91.65, 36.65), (-91.75, 36.65)])
    m = _polygon_mask_from_meta(payload, poly)
    assert m.tolist() == [[False, False], [False, True]]


def test_mean_grid_series_with_mask():
    payload = {"data": [["2020-01-01", [[0.5, 0.7], [-999, 0.9]]]]}
    out = _mean_grid_series(payload, mask=np.array([[False, True], [True, True]]))
    assert math.isclose(out["pcpn_in"].iloc[0], (0.7 + 0.9) / 2)


def test_mean_grid_series_mask_shape_mismatch_raises():
    payload = {"data": [["2020-01-01", [[0.5, 0.7], [0.1, 0.9]]]]}
    with pytest.raises(ValueError):
        _mean_grid_series(payload, mask=np.array([[True, True, True]]))


def test_get_basin_pcpn_polygon_spans_multiple_year_chunks(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "RAW_DIR", tmp_path)

    poly = Polygon([(-91.75, 36.55), (-91.65, 36.55), (-91.65, 36.65), (-91.75, 36.65)])
    calls = {"count": 0}

    def fake_post(body):
        calls["count"] += 1
        if calls["count"] == 1:
            return {
                "meta": {
                    "lat": [[36.5, 36.5], [36.6, 36.6]],
                    "lon": [[-91.8, -91.7], [-91.8, -91.7]],
                },
                "data": [
                    ["2019-12-30", [[1.0, 2.0], [3.0, 4.0]]],
                    ["2019-12-31", [[5.0, 6.0], [7.0, 8.0]]],
                ],
            }
        # second chunk: no meta at all — proves the mask from chunk 1 is reused,
        # not recomputed (recomputing would raise via _grid_latlon).
        return {
            "data": [
                ["2020-01-01", [[9.0, 10.0], [11.0, 12.0]]],
                ["2020-01-02", [[13.0, 14.0], [15.0, 16.0]]],
            ]
        }

    monkeypatch.setattr("spring_river.ingest.prism._post", fake_post)

    out = get_basin_pcpn("2019-12-30", "2020-01-02", polygon=poly)

    assert calls["count"] == 2
    assert len(out) == 4
    # inside cell is [1, 1] (lat 36.6, lon -91.7) for every day's grid
    assert out["pcpn_in"].tolist() == [4.0, 8.0, 12.0, 16.0]

    meta = json.loads((tmp_path / "prism_basin_pcpn_polygon.meta.json").read_text())
    assert meta["cells_in_polygon"] == 1
    assert meta["cells_in_bbox"] == 4
