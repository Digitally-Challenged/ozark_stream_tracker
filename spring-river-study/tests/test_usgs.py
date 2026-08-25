import pandas as pd

from spring_river.ingest.usgs import _tidy_dv


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


def test_tidy_dv_columns_and_approval():
    out = _tidy_dv(_fake_nwis_dv(), param="00060")
    assert list(out.columns) == ["date", "value", "approved"]
    assert out["approved"].tolist() == [True, False, True]
    assert out["date"].dt.tz is None  # naive local dates


def test_tidy_dv_masks_nwis_sentinel():
    out = _tidy_dv(_fake_nwis_dv(), param="00060")
    assert pd.isna(out["value"].iloc[2])  # -999999 => NaN
