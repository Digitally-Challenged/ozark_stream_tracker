"""RCC-ACIS daily precipitation (StnData) and station discovery (StnMeta)."""
import pandas as pd
import requests

from spring_river.ingest.cache import fetch_cached

ACIS_BASE = "https://data.rcc-acis.org"


def _empty_stndata_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.Series([], dtype="datetime64[ns]"),
            "pcpn_in": pd.Series([], dtype="float64"),
        }
    )


def _parse_stndata(payload: dict) -> pd.DataFrame:
    rows = payload["data"]
    if not rows:
        return _empty_stndata_frame()
    df = pd.DataFrame(rows, columns=["date", "pcpn_in"])
    df["date"] = pd.to_datetime(df["date"])
    # ACIS values can carry a trailing single-letter flag appended to the numeric
    # string (e.g. "0.42A" = accumulated); "T" (trace) and "M" (missing) are
    # flag-only sentinels with no numeric part, and "S" (subsequent, i.e. value
    # revised/withheld) can also appear alone. Handle the flag-only sentinels
    # first, then strip any trailing alpha flag from the rest before coercion.
    raw = df["pcpn_in"].astype(str).str.strip()
    special = raw.replace({"T": "0.0", "M": None, "S": None})
    stripped = special.where(
        special.isna(), special.str.replace(r"[A-Za-z]+$", "", regex=True).str.strip()
    )
    df["pcpn_in"] = pd.to_numeric(stripped, errors="coerce").astype("float64")
    return df


def get_station_pcpn(
    sid: str, start: str, end: str, refresh: bool = False
) -> pd.DataFrame:
    name = f"acis_pcpn_{sid.replace(' ', '_')}"
    body = {"sid": sid, "sdate": start, "edate": end, "elems": [{"name": "pcpn"}]}

    def fetch() -> pd.DataFrame:
        resp = requests.post(f"{ACIS_BASE}/StnData", json=body, timeout=60)
        resp.raise_for_status()
        payload = resp.json()
        if "error" in payload:
            raise RuntimeError(f"ACIS error for {sid}: {payload['error']}")
        return _parse_stndata(payload)

    meta = {"source": "RCC-ACIS StnData", "request": body}
    return fetch_cached(name, fetch, meta, refresh=refresh)


def find_stations(bbox: tuple[float, float, float, float]) -> pd.DataFrame:
    body = {
        "bbox": ",".join(str(v) for v in bbox),  # west,south,east,north
        "elems": "pcpn",
        "meta": "name,sids,ll,valid_daterange",
    }
    resp = requests.post(f"{ACIS_BASE}/StnMeta", json=body, timeout=60)
    resp.raise_for_status()
    payload = resp.json()
    if "error" in payload:
        raise RuntimeError(f"ACIS StnMeta error: {payload['error']}")
    stations = payload.get("meta", [])
    return pd.DataFrame(
        {
            "name": [s.get("name") for s in stations],
            "sids": [s.get("sids") for s in stations],
            "ll": [s.get("ll") for s in stations],
            "valid_daterange": [s.get("valid_daterange") for s in stations],
        }
    )
