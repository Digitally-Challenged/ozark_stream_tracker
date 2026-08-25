"""NWS NWPS gauge document for HDYA4: flood categories, ratings, crests."""
import json
import os
from datetime import datetime, timezone

import pandas as pd
import requests

from spring_river.config import NWS_GAUGE, RAW_DIR

NWPS_URL = f"https://api.water.noaa.gov/nwps/v1/gauges/{NWS_GAUGE}"


def get_gauge_info(refresh: bool = False) -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"nwps_{NWS_GAUGE}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    resp = requests.get(NWPS_URL, timeout=30)
    resp.raise_for_status()
    info = resp.json()

    # Atomic write: temp file → replace, so a truncated file never appears as cache
    tmp_path = path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(info, indent=2))
    os.replace(tmp_path, path)

    meta_path = RAW_DIR / f"nwps_{NWS_GAUGE}.meta.json"
    meta_tmp_path = meta_path.with_suffix(".json.tmp")
    meta_tmp_path.write_text(
        json.dumps(
            {
                "source": "NWS NWPS v1 gauge document",
                "url": NWPS_URL,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        )
    )
    os.replace(meta_tmp_path, meta_path)
    return info


def flood_categories(info: dict) -> dict[str, float]:
    cats = info.get("flood", {}).get("categories", {})
    return {
        name: float(body["stage"])
        for name, body in cats.items()
        if isinstance(body, dict) and body.get("stage") is not None
    }


def historic_crests(info: dict) -> pd.DataFrame:
    """NWS crest list — the only Hardy record before USGS DV starts in 2001.
    NWPS reports flow=0 when unknown; treat as missing. Duplicates dropped."""
    rows = info.get("flood", {}).get("crests", {}).get("historic", [])
    if not rows:
        return pd.DataFrame(
            {
                "date": pd.Series(dtype="datetime64[ns]"),
                "stage_ft": pd.Series(dtype="float64"),
                "flow_cfs": pd.Series(dtype="float64"),
            }
        )
    # Crests are all-day events; drop tz and keep the UTC wall date (not local-tz converted).
    df = pd.DataFrame(
        {
            "date": pd.to_datetime([r["occurredTime"] for r in rows]).tz_localize(None),
            "stage_ft": [float(r["stage"]) for r in rows],
            "flow_cfs": [float(r["flow"]) if r.get("flow") else float("nan") for r in rows],
        }
    )
    return (
        df.drop_duplicates(["date", "stage_ft"])
        .sort_values("date")
        .reset_index(drop=True)
    )
