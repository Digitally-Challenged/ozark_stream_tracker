import numpy as np
import pandas as pd
import pytest
import xarray as xr

from spring_river.ingest import aorc, cache


@pytest.fixture
def raw_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "RAW_DIR", tmp_path)
    return tmp_path


def _hourly(start: str, hours: int, value: float = 1.0) -> pd.DataFrame:
    t = pd.date_range(start, periods=hours, freq="h")
    return pd.DataFrame({"time_utc": t, "pcpn_mm": np.full(hours, value)})


def test_daily_from_hourly_sums_24h_ending_12_utc():
    # 2020-01-01 13:00 .. 2020-01-02 12:00 is one complete day labelled 2020-01-02
    h = _hourly("2020-01-01 13:00", 24, value=25.4)
    out = aorc.daily_from_hourly(h)
    assert list(out.columns) == ["date", "pcpn_in"]
    assert out["date"].tolist() == [pd.Timestamp("2020-01-02")]
    assert out["pcpn_in"].iloc[0] == pytest.approx(24.0)


def test_daily_from_hourly_partial_day_is_nan_not_low():
    h = _hourly("2020-01-01 13:00", 30, value=1.0)  # one full day + 6 h of the next
    out = aorc.daily_from_hourly(h)
    assert out["date"].tolist() == [pd.Timestamp("2020-01-02"), pd.Timestamp("2020-01-03")]
    assert out["pcpn_in"].iloc[0] == pytest.approx(24 / 25.4)
    assert np.isnan(out["pcpn_in"].iloc[1])


def test_daily_from_hourly_boundary_hour_belongs_to_ending_day():
    h = pd.DataFrame({"time_utc": [pd.Timestamp("2020-01-02 12:00"), pd.Timestamp("2020-01-02 13:00")],
                      "pcpn_mm": [1.0, 2.0]})
    out = aorc.daily_from_hourly(h)
    # both days incomplete → NaN, but the labels must be 01-02 and 01-03
    assert out["date"].tolist() == [pd.Timestamp("2020-01-02"), pd.Timestamp("2020-01-03")]


def test_basin_hourly_mean_applies_mask():
    t = pd.date_range("2020-01-01", periods=2, freq="h")
    lats = np.array([36.5, 36.6])
    lons = np.array([-91.8, -91.7])
    data = np.array([[[1.0, 2.0], [3.0, 4.0]], [[10.0, 20.0], [30.0, 40.0]]])
    da = xr.DataArray(data, dims=("time", "latitude", "longitude"),
                      coords={"time": t, "latitude": lats, "longitude": lons})
    mask = np.array([[True, False], [False, True]])
    out = aorc._basin_hourly_mean(da, mask)
    assert list(out.columns) == ["time_utc", "pcpn_mm"]
    assert out["pcpn_mm"].tolist() == pytest.approx([2.5, 25.0])
    assert out["time_utc"].dt.tz is None


def test_get_basin_pcpn_concatenates_years_and_uses_cache(raw_dir, monkeypatch):
    calls = []

    def fake_year(year: int, refresh: bool = False) -> pd.DataFrame:
        calls.append(year)
        return _hourly(f"{year}-12-31 13:00", 24, value=25.4)  # one day labelled Jan 1 of year+1

    monkeypatch.setattr(aorc, "available_years", lambda: list(range(1979, 2026)))
    monkeypatch.setattr(aorc, "get_basin_hourly", fake_year)
    out = aorc.get_basin_pcpn("2019-01-01", "2020-12-31")
    assert calls == [2019, 2020]
    assert out["date"].tolist() == [pd.Timestamp("2020-01-01")]
    assert out["pcpn_in"].tolist() == pytest.approx([24.0])


def test_get_basin_pcpn_rejects_out_of_range_request(raw_dir, monkeypatch):
    def fail_if_called(year: int, refresh: bool = False) -> pd.DataFrame:
        raise AssertionError("get_basin_hourly should not be called for an out-of-range request")

    monkeypatch.setattr(aorc, "available_years", lambda: list(range(1979, 2026)))
    monkeypatch.setattr(aorc, "get_basin_hourly", fail_if_called)
    with pytest.raises(ValueError):
        aorc.get_basin_pcpn("1970-01-01", "1975-12-31")


def test_get_basin_pcpn_clamps_to_latest_available_year(raw_dir, monkeypatch):
    calls = []

    def fake_year(year: int, refresh: bool = False) -> pd.DataFrame:
        calls.append(year)
        return _hourly(f"{year}-12-31 13:00", 24, value=25.4)

    monkeypatch.setattr(aorc, "available_years", lambda: [2019, 2020])
    monkeypatch.setattr(aorc, "get_basin_hourly", fake_year)
    aorc.get_basin_pcpn("2019-01-01", "2026-08-25")
    assert calls == [2019, 2020]


def _fake_year_writer(calls: list[int]):
    """get_basin_hourly stand-in that also lays down the cache parquet the clamp looks for."""

    def fake_year(year: int, refresh: bool = False) -> pd.DataFrame:
        calls.append(year)
        df = _hourly(f"{year}-12-31 13:00", 24, value=25.4)
        df.to_parquet(cache.RAW_DIR / f"aorc_basin_hourly_{year}.parquet")
        return df

    return fake_year


def test_get_basin_pcpn_skips_s3_listing_when_all_years_cached(raw_dir, monkeypatch):
    calls: list[int] = []
    fake_year = _fake_year_writer(calls)
    for y in (2019, 2020):
        fake_year(y)
    calls.clear()

    def refuse_listing() -> tuple[int, ...]:
        raise AssertionError("listed")

    monkeypatch.setattr(aorc, "available_years", refuse_listing)
    monkeypatch.setattr(aorc, "get_basin_hourly", fake_year)
    out = aorc.get_basin_pcpn("2019-01-01", "2020-12-31")
    assert calls == [2019, 2020]
    assert out["date"].tolist() == [pd.Timestamp("2020-01-01")]


def test_get_basin_pcpn_warns_and_clamps_to_newest_cached_when_listing_fails(raw_dir, monkeypatch):
    calls: list[int] = []
    fake_year = _fake_year_writer(calls)
    fake_year(2019)  # 2020 is deliberately absent, so the clamp must try the listing
    calls.clear()

    def offline_listing() -> tuple[int, ...]:
        raise OSError("no network")

    monkeypatch.setattr(aorc, "available_years", offline_listing)
    monkeypatch.setattr(aorc, "get_basin_hourly", fake_year)
    with pytest.warns(UserWarning, match="newest cached year 2019"):
        aorc.get_basin_pcpn("2019-01-01", "2020-12-31")
    assert calls == [2019]


def test_get_basin_pcpn_reraises_when_listing_fails_with_no_cache(raw_dir, monkeypatch):
    def offline_listing() -> tuple[int, ...]:
        raise OSError("no network")

    monkeypatch.setattr(aorc, "available_years", offline_listing)
    monkeypatch.setattr(aorc, "get_basin_hourly", _fake_year_writer([]))
    with pytest.raises(OSError, match="no network"):
        aorc.get_basin_pcpn("2019-01-01", "2020-12-31")


def test_fetch_year_raises_when_no_hours_in_bbox(monkeypatch):
    from spring_river.config import RECHARGE_POLYGON_PATH
    from spring_river.ingest.basin import load_recharge_polygon

    poly = load_recharge_polygon(RECHARGE_POLYGON_PATH)
    cx, cy = poly.centroid.x, poly.centroid.y
    lats = np.array([cy - 0.01, cy + 0.01])
    lons = np.array([cx - 0.01, cx + 0.01])
    empty = xr.DataArray(
        np.empty((0, 2, 2)),
        dims=("time", "latitude", "longitude"),
        coords={"time": np.array([], dtype="datetime64[ns]"), "latitude": lats, "longitude": lons},
    )

    monkeypatch.setattr(aorc, "_open_year_subset", lambda year, bbox: empty)
    with pytest.raises(RuntimeError, match="no hours"):
        aorc._fetch_year(2020)
