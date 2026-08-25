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

    monkeypatch.setattr(aorc, "get_basin_hourly", fake_year)
    out = aorc.get_basin_pcpn("2019-01-01", "2020-12-31")
    assert calls == [2019, 2020]
    assert out["date"].tolist() == [pd.Timestamp("2020-01-01"), pd.Timestamp("2021-01-01")]
    assert out["pcpn_in"].tolist() == pytest.approx([24.0, 24.0])
