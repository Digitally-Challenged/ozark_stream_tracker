"""USGS field and channel measurements via the OGC API (Water Data for the Nation).

Phase 8 (review.md items 5, 6). Q5's stage-at-fixed-discharge trend rests on
IV pairs whose discharge is itself rating-derived, so a drifting rating would
produce a drifting stage-at-flow with no channel change. Field measurements
answer that: a wading or ADCP measurement of discharge paired with the stage
read at the same visit is independent of the rating. If measured stage at a
measured discharge falls, the channel really degraded.

Endpoints (`api.waterdata.usgs.gov/ogcapi/v0`):

- `field-measurements`  one row per (visit, parameter). Discharge (00060) and
  gage height (00065) arrive as SEPARATE rows sharing a `field_visit_id`;
  `measured_pairs` joins them on that id, which is the only correct way to
  pair them (timestamps can differ within a visit).
- `channel-measurements`  the surveyed channel geometry per visit (width,
  area, velocity) — the physical corroboration for a change in the section.
- `monitoring-locations`  the CURRENT gauge datum (the Q1c limitation). It
  carries no revision history, and `time-series-revisions` is empty for this
  site, so the dated revisions are cited to the review and this pull confirms
  the value they end at.

Values arrive as strings and are coerced; `time` is UTC and is converted to
tz-naive so it aligns with the DV/IV frames the rest of the study uses.
"""
import pandas as pd
import requests

from spring_river.ingest.cache import fetch_cached

OGC_BASE = "https://api.waterdata.usgs.gov/ogcapi/v0"
PARAM_DISCHARGE = "00060"
PARAM_STAGE = "00065"
PAGE_LIMIT = 10_000
TIMEOUT_S = 60


def _location_id(site: str) -> str:
    return site if site.startswith("USGS-") else f"USGS-{site}"


def _get_features(collection: str, params: dict) -> list[dict]:
    r = requests.get(f"{OGC_BASE}/collections/{collection}/items",
                     params={"f": "json", "limit": PAGE_LIMIT, **params}, timeout=TIMEOUT_S)
    r.raise_for_status()
    return [f.get("properties", {}) for f in (r.json().get("features") or [])]


def _frame(props: list[dict], columns: list[str]) -> pd.DataFrame:
    if not props:
        return pd.DataFrame({c: pd.Series([], dtype="object") for c in columns})
    return pd.DataFrame(props)


def _naive_utc(s: pd.Series) -> pd.Series:
    t = pd.to_datetime(s, utc=True, errors="coerce")
    return t.dt.tz_localize(None)


def get_field_measurements(site: str, refresh: bool = False) -> pd.DataFrame:
    """All field measurements at `site`, both parameters, one row per reading.

    Columns: field_visit_id, parameter_code, time, value, unit_of_measure,
    approval_status, measurement_rated, observing_procedure, vertical_datum.
    """
    name = f"usgs_fieldmeas_{site}"

    def fetch() -> pd.DataFrame:
        props = _get_features("field-measurements",
                              {"monitoring_location_id": _location_id(site)})
        keep = ["field_visit_id", "parameter_code", "time", "value", "unit_of_measure",
                "approval_status", "measurement_rated", "observing_procedure", "vertical_datum"]
        df = _frame(props, keep)
        for c in keep:
            if c not in df.columns:
                df[c] = pd.NA
        df = df[keep].copy()
        df["time"] = _naive_utc(df["time"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        return df.sort_values("time").reset_index(drop=True)

    meta = {"source": "USGS OGC API field-measurements", "site": site,
            "endpoint": f"{OGC_BASE}/collections/field-measurements/items"}
    return fetch_cached(name, fetch, meta, refresh=refresh)


def get_channel_measurements(site: str, refresh: bool = False) -> pd.DataFrame:
    """Surveyed channel geometry per field visit at `site`."""
    name = f"usgs_chanmeas_{site}"

    def fetch() -> pd.DataFrame:
        props = _get_features("channel-measurements",
                              {"monitoring_location_id": _location_id(site)})
        keep = ["field_visit_id", "time", "channel_flow", "channel_width",
                "channel_area", "channel_velocity", "channel_material",
                "channel_stability", "channel_measurement_type"]
        df = _frame(props, keep)
        for c in keep:
            if c not in df.columns:
                df[c] = pd.NA
        df = df[keep].copy()
        df["time"] = _naive_utc(df["time"])
        for c in ("channel_flow", "channel_width", "channel_area", "channel_velocity"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
        return df.sort_values("time").reset_index(drop=True)

    meta = {"source": "USGS OGC API channel-measurements", "site": site,
            "endpoint": f"{OGC_BASE}/collections/channel-measurements/items"}
    return fetch_cached(name, fetch, meta, refresh=refresh)


def measured_pairs(fm: pd.DataFrame) -> pd.DataFrame:
    """(discharge, stage) pairs joined on `field_visit_id`.

    Both readings come from the same visit, so the pair is independent of the
    rating: the discharge was measured, not computed from the stage.

    A visit typically records the gage height several times (wire-weight
    readings at the start and end of the measurement, plus the mean), and
    occasionally more than one discharge. Both sides are therefore reduced to
    one value per visit — the mean of that visit's readings, which is the
    stage the measured discharge corresponds to — so the join cannot multiply
    a single visit into several pairs.

    Columns: field_visit_id, time, q_cfs, stage_ft, n_stage_readings, wy.
    """
    def _per_visit(param: str, value_name: str) -> pd.DataFrame:
        d = fm[fm["parameter_code"] == param].dropna(subset=["value"])
        g = d.groupby("field_visit_id").agg(**{value_name: ("value", "mean"),
                                               "time": ("time", "min"),
                                               f"n_{value_name}": ("value", "size")})
        return g.reset_index()

    q = _per_visit(PARAM_DISCHARGE, "q_cfs")
    h = _per_visit(PARAM_STAGE, "stage_ft").drop(columns="time")
    j = (q.merge(h, on="field_visit_id", how="inner")
          .rename(columns={"n_stage_ft": "n_stage_readings"})
          .drop(columns=[c for c in ("n_q_cfs",) if c in q.columns], errors="ignore")
          .dropna(subset=["q_cfs", "stage_ft", "time"]))
    j = j[j["q_cfs"] > 0]
    wy = j["time"].dt.year + (j["time"].dt.month >= 10).astype(int)
    return j.assign(wy=wy).sort_values("time").reset_index(drop=True)


def get_monitoring_location(site: str, refresh: bool = False) -> pd.DataFrame:
    """Monitoring-location metadata, including the CURRENT gauge datum.

    Phase 8 (review.md item 5). The Q1c limitation claimed no datum records
    had been reviewed; they exist. This endpoint reports the datum in force
    now (`altitude` + `vertical_datum`). It does NOT carry the revision
    history — `time-series-revisions` returns nothing for this site — so the
    dated revisions in the phase report are cited to the review, with this
    pull confirming the current value they end at.
    """
    name = f"usgs_monloc_{site}"

    def fetch() -> pd.DataFrame:
        r = requests.get(f"{OGC_BASE}/collections/monitoring-locations/items",
                         params={"f": "json", "id": _location_id(site)}, timeout=TIMEOUT_S)
        r.raise_for_status()
        feats = r.json().get("features") or []
        keep = ["id", "monitoring_location_name", "altitude", "altitude_accuracy",
                "altitude_method_name", "vertical_datum", "vertical_datum_name",
                "drainage_area"]
        df = _frame([f.get("properties", {}) for f in feats], keep)
        for c in keep:
            if c not in df.columns:
                df[c] = pd.NA
        df = df[keep].copy()
        df["altitude"] = pd.to_numeric(df["altitude"], errors="coerce")
        return df

    meta = {"source": "USGS OGC API monitoring-locations", "site": site,
            "endpoint": f"{OGC_BASE}/collections/monitoring-locations/items"}
    return fetch_cached(name, fetch, meta, refresh=refresh)
