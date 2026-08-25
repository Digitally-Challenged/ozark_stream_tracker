"""Offline tests for the USGS OGC field/channel-measurement pull.

The network is never touched: `requests.get` is monkeypatched with a fake
whose payload has the real endpoint's shape (values as strings, UTC times,
discharge and stage on SEPARATE rows sharing a field_visit_id).
"""
import numpy as np
import pandas as pd
import pytest

from spring_river.ingest import field_measurements as fm


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def _feature(**props) -> dict:
    return {"type": "Feature", "properties": props}


FIELD_PAYLOAD = {"features": [
    _feature(field_visit_id="v1", parameter_code="00060", value="400",
             time="2004-07-01T15:00:00+00:00", unit_of_measure="ft^3/s",
             approval_status="Approved", measurement_rated="Good",
             observing_procedure="Wading", vertical_datum="None"),
    _feature(field_visit_id="v1", parameter_code="00065", value="3.44",
             time="2004-07-01T15:05:00+00:00", unit_of_measure="ft",
             approval_status="Approved", measurement_rated="Good",
             observing_procedure="Wading", vertical_datum="NGVD29"),
    _feature(field_visit_id="v2", parameter_code="00060", value="410",
             time="2011-11-02T16:00:00+00:00", unit_of_measure="ft^3/s",
             approval_status="Approved", measurement_rated="Fair",
             observing_procedure="ADCP", vertical_datum="None"),
    _feature(field_visit_id="v2", parameter_code="00065", value="3.04",
             time="2011-11-02T16:10:00+00:00", unit_of_measure="ft",
             approval_status="Approved", measurement_rated="Fair",
             observing_procedure="ADCP", vertical_datum="NGVD29"),
    # a discharge reading whose visit has no stage: must not produce a pair
    _feature(field_visit_id="v3", parameter_code="00060", value="900",
             time="2015-03-04T12:00:00+00:00", unit_of_measure="ft^3/s",
             approval_status="Approved", measurement_rated="Good",
             observing_procedure="ADCP", vertical_datum="None"),
]}

CHANNEL_PAYLOAD = {"features": [
    _feature(field_visit_id="v1", time="2004-07-01T15:00:00+00:00", channel_flow="400",
             channel_width="240", channel_area="2500", channel_velocity="0.16",
             channel_material="Unspecified", channel_stability="Unspecified",
             channel_measurement_type="wading"),
]}


@pytest.fixture
def offline(monkeypatch, tmp_path):
    """Patch the HTTP call and redirect the raw cache into tmp_path."""
    monkeypatch.setattr(fm, "RAW_DIR", tmp_path, raising=False)
    monkeypatch.setattr("spring_river.ingest.cache.RAW_DIR", tmp_path)

    def fake_get(url, params=None, timeout=None):
        return _FakeResponse(CHANNEL_PAYLOAD if "channel-measurements" in url else FIELD_PAYLOAD)

    monkeypatch.setattr(fm.requests, "get", fake_get)


def test_get_field_measurements_coerces_types(offline):
    df = fm.get_field_measurements("07069305")
    assert len(df) == 5
    assert df["value"].dtype.kind == "f"
    assert df["time"].dt.tz is None                      # tz-naive, aligns with DV/IV
    assert df["time"].is_monotonic_increasing


def test_location_id_accepts_bare_and_prefixed():
    assert fm._location_id("07069305") == "USGS-07069305"
    assert fm._location_id("USGS-07069305") == "USGS-07069305"


def test_measured_pairs_joins_on_visit_not_time(offline):
    pairs = fm.measured_pairs(fm.get_field_measurements("07069305"))
    # v3 has no stage reading, so exactly two pairs survive
    assert len(pairs) == 2
    assert set(pairs["field_visit_id"]) == {"v1", "v2"}
    row = pairs[pairs["field_visit_id"] == "v1"].iloc[0]
    assert row["q_cfs"] == 400.0 and row["stage_ft"] == 3.44
    # the measured stage fell between the two visits at essentially equal flow
    assert pairs.sort_values("time")["stage_ft"].iloc[-1] < row["stage_ft"]


def test_measured_pairs_assigns_water_year(offline):
    pairs = fm.measured_pairs(fm.get_field_measurements("07069305")).set_index("field_visit_id")
    assert pairs.loc["v1", "wy"] == 2004          # July -> same calendar year
    assert pairs.loc["v2", "wy"] == 2012          # November -> next water year


def test_get_channel_measurements_numeric(offline):
    ch = fm.get_channel_measurements("07069305")
    assert len(ch) == 1
    assert ch["channel_width"].iloc[0] == 240.0
    assert ch["channel_area"].dtype.kind in "fi"      # numeric, not the raw string
    assert ch["channel_velocity"].iloc[0] == 0.16


def test_empty_payload_yields_empty_frame(monkeypatch, tmp_path):
    monkeypatch.setattr("spring_river.ingest.cache.RAW_DIR", tmp_path)
    monkeypatch.setattr(fm.requests, "get", lambda *a, **k: _FakeResponse({"features": []}))
    df = fm.get_field_measurements("00000000")
    assert df.empty
    assert fm.measured_pairs(df).empty
