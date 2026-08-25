import json

import pandas as pd

from spring_river.ingest.nwps import flood_categories


def test_flood_categories_extracts_stages():
    info = {
        "flood": {
            "categories": {
                "action": {"stage": 8.0},
                "minor": {"stage": 10.0},
                "moderate": {"stage": 14.0},
                "major": {"stage": 16.0},
            }
        }
    }
    assert flood_categories(info) == {
        "action": 8.0,
        "minor": 10.0,
        "moderate": 14.0,
        "major": 16.0,
    }


def test_flood_categories_missing_returns_empty():
    assert flood_categories({}) == {}


def test_historic_crests_dedups_and_sorts():
    from spring_river.ingest.nwps import historic_crests

    info = {
        "flood": {
            "crests": {
                "historic": [
                    {"occurredTime": "2008-03-19T12:30:00Z", "stage": 22.29, "flow": 80700},
                    {"occurredTime": "1982-12-03T00:00:00Z", "stage": 29, "flow": 0},
                    {"occurredTime": "1982-12-03T00:00:00Z", "stage": 29, "flow": 0},
                ]
            }
        }
    }
    out = historic_crests(info)
    assert list(out.columns) == ["date", "stage_ft", "flow_cfs"]
    assert len(out) == 2  # duplicate 1982 entry removed (NWPS returns it twice)
    assert out["date"].iloc[0].year == 1982
    assert pd.isna(out["flow_cfs"].iloc[0])  # flow 0 means "not reported"


def test_historic_crests_empty_returns_zero_row_frame_with_correct_dtypes():
    from spring_river.ingest.nwps import historic_crests

    out = historic_crests({})
    assert list(out.columns) == ["date", "stage_ft", "flow_cfs"]
    assert len(out) == 0
    assert out["date"].dtype == "datetime64[ns]"
    assert out["stage_ft"].dtype == "float64"
    assert out["flow_cfs"].dtype == "float64"


def test_get_gauge_info_writes_atomically_and_caches(monkeypatch, tmp_path):
    from spring_river.ingest import nwps

    monkeypatch.setattr(nwps, "RAW_DIR", tmp_path)

    fake_info = {"foo": "bar"}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return fake_info

    def fake_get(url, timeout):
        return FakeResponse()

    monkeypatch.setattr(nwps.requests, "get", fake_get)

    result = nwps.get_gauge_info()
    assert result == fake_info

    json_path = tmp_path / f"nwps_{nwps.NWS_GAUGE}.json"
    meta_path = tmp_path / f"nwps_{nwps.NWS_GAUGE}.meta.json"
    assert json_path.exists()
    assert meta_path.exists()
    assert list(tmp_path.glob("*.tmp")) == []

    meta = json.loads(meta_path.read_text())
    assert meta["source"]
    assert meta["url"]
    assert meta["fetched_at"]

    def fake_get_raises(url, timeout):
        raise AssertionError("should not hit network on cache hit")

    monkeypatch.setattr(nwps.requests, "get", fake_get_raises)

    result_cached = nwps.get_gauge_info()
    assert result_cached == fake_info
