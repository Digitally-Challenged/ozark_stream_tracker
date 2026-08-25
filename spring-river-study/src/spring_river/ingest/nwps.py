"""NWS NWPS gauge document for HDYA4: flood categories, ratings, crests."""
import json
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
    path.write_text(json.dumps(info, indent=2))
    (RAW_DIR / f"nwps_{NWS_GAUGE}.meta.json").write_text(
        json.dumps(
            {
                "source": "NWS NWPS v1 gauge document",
                "url": NWPS_URL,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        )
    )
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
