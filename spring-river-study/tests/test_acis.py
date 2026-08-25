import pandas as pd

from spring_river.ingest.acis import _parse_stndata


PAYLOAD = {
    "meta": {"name": "WEST PLAINS"},
    "data": [
        ["2020-01-01", "0.35"],
        ["2020-01-02", "T"],
        ["2020-01-03", "M"],
        ["2020-01-04", "1.20"],
        ["2020-01-05", "0.42A"],
        ["2020-01-06", "S"],
    ],
}


def test_parse_stndata_values():
    out = _parse_stndata(PAYLOAD)
    assert list(out.columns) == ["date", "pcpn_in", "flag"]
    assert out["pcpn_in"].iloc[0] == 0.35
    assert out["flag"].iloc[0] == ""
    assert out["pcpn_in"].iloc[1] == 0.0  # trace -> 0.0
    assert out["flag"].iloc[1] == "T"
    assert pd.isna(out["pcpn_in"].iloc[2])  # missing -> NaN
    assert out["flag"].iloc[2] == "M"
    assert out["date"].dtype.kind == "M"


def test_parse_stndata_accumulation_flag():
    out = _parse_stndata(PAYLOAD)
    row = out.iloc[4]
    assert row["pcpn_in"] == 0.42
    assert row["flag"] == "A"


def test_parse_stndata_subsequent_flag():
    out = _parse_stndata(PAYLOAD)
    row = out.iloc[5]
    assert pd.isna(row["pcpn_in"])
    assert row["flag"] == "S"


def test_parse_stndata_empty_returns_contract_frame():
    out = _parse_stndata({"meta": {}, "data": []})
    assert list(out.columns) == ["date", "pcpn_in", "flag"]
    assert len(out) == 0
    assert out["date"].dtype.kind == "M"
    assert out["pcpn_in"].dtype == "float64"
