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
