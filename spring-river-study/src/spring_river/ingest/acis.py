"""RCC-ACIS daily precipitation (StnData) and station discovery (StnMeta).

ACIS/GHCN-Daily flag semantics for the `pcpn` element:
- "T" (trace): precipitation occurred but was too small to measure -> pcpn_in 0.0.
- "M" (missing): no observation for the day -> pcpn_in NaN.
- "S" (subsequent): the day's precipitation was accumulated into a SUBSEQUENT
  day's reported total (i.e. this day's true amount is unknown, folded forward)
  -> pcpn_in NaN. Per-day NaN is correct; it is not the same condition as "M".
- A numeric value with a trailing letter flag (most commonly "A", e.g. "0.42A")
  means that value is a multi-day ACCUMULATION ending on this day, not a
  single-day amount. The numeric value is preserved in pcpn_in (flags stripped)
  but the flag itself must stay identifiable — callers doing daily-resolution
  analysis need to be able to exclude or specially handle accumulated days.

`_parse_stndata` therefore returns an additive `flag` column: "" for a plain
numeric value, otherwise the flag string ("T", "M", "S", "A", ...).
"""
import pandas as pd
import requests

from spring_river.ingest.cache import fetch_cached

ACIS_BASE = "https://data.rcc-acis.org"


def _empty_stndata_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.Series([], dtype="datetime64[ns]"),
            "pcpn_in": pd.Series([], dtype="float64"),
            "flag": pd.Series([], dtype="str"),
        }
    )


def _parse_stndata(payload: dict) -> pd.DataFrame:
    rows = payload["data"]
    if not rows:
        return _empty_stndata_frame()
    df = pd.DataFrame(rows, columns=["date", "pcpn_in"])
    df["date"] = pd.to_datetime(df["date"])

    raw = df["pcpn_in"].astype(str).str.strip()

    # Flag-only sentinels ("T", "M", "S") have no numeric part of their own.
    is_flag_only = raw.isin(["T", "M", "S"])

    # Numeric values may carry a trailing alpha flag (e.g. "0.42A"); split it
    # off so the bare numeric string is left for coercion.
    split = raw.str.extract(r"^([\-0-9.]+)([A-Za-z]+)?$")
    numeric_part = split[0]
    trailing_flag = split[1].fillna("")

    flag = trailing_flag.where(~is_flag_only, raw)
    stripped = numeric_part.where(~is_flag_only, None)
    stripped = stripped.where(raw != "T", "0.0")  # trace -> 0.0

    df["pcpn_in"] = pd.to_numeric(stripped, errors="coerce").astype("float64")
    df["flag"] = flag.astype("str")
    return df[["date", "pcpn_in", "flag"]]


def _flag_counts(df: pd.DataFrame) -> dict[str, int]:
    if "flag" not in df.columns or not len(df):
        return {}
    counts = df.loc[df["flag"] != "", "flag"].value_counts().to_dict()
    return {str(k): int(v) for k, v in counts.items()}


def get_station_pcpn(
    sid: str, start: str, end: str, refresh: bool = False
) -> pd.DataFrame:
    name = f"acis_pcpn_{sid.replace(' ', '_')}"
    body = {"sid": sid, "sdate": start, "edate": end, "elems": [{"name": "pcpn"}]}
    meta = {"source": "RCC-ACIS StnData", "request": body}

    def fetch() -> pd.DataFrame:
        resp = requests.post(f"{ACIS_BASE}/StnData", json=body, timeout=60)
        resp.raise_for_status()
        payload = resp.json()
        if "error" in payload:
            raise RuntimeError(f"ACIS error for {sid}: {payload['error']}")
        df = _parse_stndata(payload)
        meta["flag_counts"] = _flag_counts(df)  # fetch_cached writes `meta` after this returns
        return df

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
