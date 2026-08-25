import subprocess
import sys

import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Polygon

from spring_river.config import RECHARGE_POLYGON_PATH
from spring_river.ingest import aorc, basin, prism
from spring_river.ingest.basin import cell_mask, load_recharge_polygon, polygon_bbox


def test_load_recharge_polygon_bounds_match_modnr_layer():
    poly = load_recharge_polygon(RECHARGE_POLYGON_PATH)
    w, s, e, n = poly.bounds
    assert -91.96 < w < -91.95 and -91.47 < e < -91.46
    assert 36.49 < s < 36.50 and 36.82 < n < 36.83
    assert poly.is_valid


def test_polygon_bbox_pads_bounds():
    poly = Polygon([(-91.9, 36.5), (-91.5, 36.5), (-91.5, 36.8), (-91.9, 36.8)])
    w, s, e, n = polygon_bbox(poly, pad_deg=0.02)
    assert (w, s, e, n) == pytest.approx((-91.92, 36.48, -91.48, 36.82))


def test_cell_mask_marks_centres_inside_only():
    poly = Polygon([(-91.9, 36.5), (-91.5, 36.5), (-91.5, 36.8), (-91.9, 36.8)])
    lats = np.array([36.4, 36.6, 36.9])
    lons = np.array([-92.0, -91.7, -91.4])
    m = cell_mask(lats, lons, poly)
    assert m.shape == (3, 3)
    assert m.sum() == 1 and m[1, 1]


def test_cell_mask_area_roughly_349_sq_mi():
    poly = load_recharge_polygon(RECHARGE_POLYGON_PATH)
    lats = np.arange(36.45, 36.85, 0.01)
    lons = np.arange(-91.96, -91.45, 0.01)
    m = cell_mask(lats, lons, poly)
    # 0.01° cell ≈ 1.113 km × 0.893 km at 36.66° N ≈ 0.994 km²; 349–361 mi² = 904–935 km²
    km2 = m.sum() * 1.113 * 0.893
    assert 850 < km2 < 990


def test_basin_and_aorc_import_first_without_cycle():
    """Either module must import cleanly as the first spring_river import in a fresh interpreter."""
    for mod in ("spring_river.ingest.basin", "spring_river.ingest.aorc"):
        subprocess.run([sys.executable, "-c", f"import {mod}"], check=True)


def test_get_basin_pcpn_dispatches_by_source(monkeypatch):
    seen = []
    df = pd.DataFrame({"date": pd.to_datetime(["2020-01-01"]), "pcpn_in": [0.1]})
    monkeypatch.setattr(aorc, "get_basin_pcpn", lambda s, e, refresh=False: (seen.append("aorc"), df)[1])
    monkeypatch.setattr(prism, "get_basin_pcpn",
                        lambda s, e, polygon=None, refresh=False, **kw: (seen.append("polygon" if polygon is not None else "buffer"), df)[1])
    for src in ("aorc", "prism_polygon", "prism_buffer"):
        out = basin.get_basin_pcpn("2020-01-01", "2020-12-31", source=src)
        assert list(out.columns) == ["date", "pcpn_in"]
    assert seen == ["aorc", "polygon", "buffer"]


def test_get_basin_pcpn_rejects_unknown_source():
    with pytest.raises(ValueError):
        basin.get_basin_pcpn("2020-01-01", "2020-12-31", source="daymet")


def test_basin_label_names_geometry_and_product():
    assert "AORC" in basin.basin_label("aorc") and "MoDNR" in basin.basin_label("aorc")
    assert "PRISM" in basin.basin_label("prism_polygon") and "MoDNR" in basin.basin_label("prism_polygon")
    assert "30 km" in basin.basin_label("prism_buffer")
