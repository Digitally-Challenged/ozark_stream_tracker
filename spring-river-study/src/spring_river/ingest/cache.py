"""Raw-data cache: every API pull lands in data/raw with request metadata."""
import json
from datetime import datetime, timezone
from typing import Callable

import pandas as pd

from spring_river.config import RAW_DIR


def fetch_cached(
    name: str,
    fetch_fn: Callable[[], pd.DataFrame],
    meta: dict,
    refresh: bool = False,
) -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    parquet_path = RAW_DIR / f"{name}.parquet"
    if parquet_path.exists() and not refresh:
        return pd.read_parquet(parquet_path)

    df = fetch_fn()
    df.to_parquet(parquet_path)
    record = dict(meta)
    record["fetched_at"] = datetime.now(timezone.utc).isoformat()
    record["rows"] = int(len(df))
    (RAW_DIR / f"{name}.meta.json").write_text(json.dumps(record, indent=2))
    return df
