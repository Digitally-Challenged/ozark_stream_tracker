import numpy as np
import pytest
from shapely.geometry import Polygon

from spring_river.config import RECHARGE_POLYGON_PATH
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
