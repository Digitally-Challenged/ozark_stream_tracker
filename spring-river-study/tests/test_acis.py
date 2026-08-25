import pandas as pd

from spring_river.ingest.acis import _parse_stndata


PAYLOAD = {
    "meta": {"name": "WEST PLAINS"},
    "data": [
        ["2020-01-01", "0.35"],
        ["2020-01-02", "T"],
        ["2020-01-03", "M"],
        ["2020-01-04", "1.20"],
    ],
}


def test_parse_stndata_values():
    out = _parse_stndata(PAYLOAD)
    assert list(out.columns) == ["date", "pcpn_in"]
    assert out["pcpn_in"].iloc[0] == 0.35
    assert out["pcpn_in"].iloc[1] == 0.0  # trace -> 0.0
    assert pd.isna(out["pcpn_in"].iloc[2])  # missing -> NaN
    assert out["date"].dtype.kind == "M"
