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


def test_get_station_pcpn_cache_suffix_names_a_separate_file(tmp_path, monkeypatch):
    """A cache_suffix keys a distinct cache file, leaving the plain one alone."""
    import json

    from spring_river.ingest import acis, cache

    monkeypatch.setattr(cache, "RAW_DIR", tmp_path)

    class _Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return PAYLOAD

    monkeypatch.setattr(acis.requests, "post", lambda *a, **k: _Resp())

    out = acis.get_station_pcpn("USC00238880", "1948-01-01", "2020-01-06", cache_suffix="_1948")
    assert len(out) == 6
    assert (tmp_path / "acis_pcpn_USC00238880_1948.parquet").exists()
    assert not (tmp_path / "acis_pcpn_USC00238880.parquet").exists()
    meta = json.loads((tmp_path / "acis_pcpn_USC00238880_1948.meta.json").read_text())
    assert meta["cache_suffix"] == "_1948"
    assert meta["request"]["sdate"] == "1948-01-01"


def test_get_station_pcpn_without_suffix_keeps_the_plain_cache_name(tmp_path, monkeypatch):
    from spring_river.ingest import acis, cache

    monkeypatch.setattr(cache, "RAW_DIR", tmp_path)

    class _Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return PAYLOAD

    monkeypatch.setattr(acis.requests, "post", lambda *a, **k: _Resp())

    acis.get_station_pcpn("USC00238880", "1981-01-01", "2020-01-06")
    assert (tmp_path / "acis_pcpn_USC00238880.parquet").exists()
