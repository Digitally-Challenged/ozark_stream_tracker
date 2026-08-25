import pandas as pd

from spring_river.ingest.usgs import _tidy_dv, _tidy_iv


def _fake_nwis_dv() -> pd.DataFrame:
    idx = pd.DatetimeIndex(
        ["2020-01-01", "2020-01-02", "2020-01-03"], tz="UTC", name="datetime"
    )
    return pd.DataFrame(
        {
            "site_no": ["07069305"] * 3,
            "00060_Mean": [850.0, 900.0, -999999.0],
            "00060_Mean_cd": ["A", "P", "A, e"],
        },
        index=idx,
    )


def _fake_nwis_iv() -> pd.DataFrame:
    idx = pd.DatetimeIndex(
        [
            "2020-01-01T06:00:00Z",
            "2020-01-01T06:15:00Z",
            "2020-01-01T06:30:00Z",
        ],
        tz="UTC",
        name="datetime",
    )
    return pd.DataFrame(
        {
            "site_no": ["07069305"] * 3,
            "00060": [850.0, 900.0, -999999.0],
            "00060_cd": ["A", "P", "A, e"],
        },
        index=idx,
    )


def test_tidy_dv_columns_and_approval():
    out = _tidy_dv(_fake_nwis_dv(), param="00060")
    assert list(out.columns) == ["date", "value", "approved"]
    assert out["approved"].tolist() == [True, False, True]
    assert out["date"].dt.tz is None  # naive local dates


def test_tidy_dv_masks_nwis_sentinel():
    out = _tidy_dv(_fake_nwis_dv(), param="00060")
    assert pd.isna(out["value"].iloc[2])  # -999999 => NaN


def test_tidy_dv_empty_input_returns_contract_frame():
    empty_raw = _fake_nwis_dv().iloc[0:0]
    out = _tidy_dv(empty_raw, param="00060")
    assert list(out.columns) == ["date", "value", "approved"]
    assert len(out) == 0
    assert out["date"].dtype == "datetime64[ns]"
    assert out["value"].dtype == "float64"
    assert out["approved"].dtype == "bool"


def test_tidy_dv_missing_columns_returns_contract_frame():
    raw = pd.DataFrame({"site_no": ["07069305"]})
    out = _tidy_dv(raw, param="00060")
    assert list(out.columns) == ["date", "value", "approved"]
    assert len(out) == 0


def test_tidy_iv_columns_approval_and_central_conversion():
    out = _tidy_iv(_fake_nwis_iv(), param="00060")
    assert list(out.columns) == ["datetime", "value", "approved"]
    assert out["approved"].tolist() == [True, False, True]
    assert out["datetime"].dt.tz is None
    # 2020-01-01T06:00:00Z => 2020-01-01 00:00:00 US/Central (CST, UTC-6)
    assert out["datetime"].iloc[0] == pd.Timestamp("2020-01-01 00:00:00")


def test_tidy_iv_masks_nwis_sentinel():
    out = _tidy_iv(_fake_nwis_iv(), param="00060")
    assert pd.isna(out["value"].iloc[2])


def test_tidy_iv_empty_input_returns_contract_frame():
    empty_raw = _fake_nwis_iv().iloc[0:0]
    out = _tidy_iv(empty_raw, param="00060")
    assert list(out.columns) == ["datetime", "value", "approved"]
    assert len(out) == 0
    assert out["datetime"].dtype == "datetime64[ns]"
    assert out["value"].dtype == "float64"
    assert out["approved"].dtype == "bool"


def test_tidy_iv_missing_columns_returns_contract_frame():
    raw = pd.DataFrame({"site_no": ["07069305"]})
    out = _tidy_iv(raw, param="00060")
    assert list(out.columns) == ["datetime", "value", "approved"]
    assert len(out) == 0
