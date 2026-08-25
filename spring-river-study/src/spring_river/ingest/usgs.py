"""USGS NWIS ingestion via the dataretrieval package, cached to data/raw."""
import pandas as pd
from dataretrieval import nwis

from spring_river.ingest.cache import fetch_cached


def _tidy_dv(raw: pd.DataFrame, param: str) -> pd.DataFrame:
    value_col = f"{param}_Mean"
    cd_col = f"{param}_Mean_cd"
    out = pd.DataFrame(
        {
            "date": raw.index.tz_localize(None)
            if raw.index.tz is not None
            else raw.index,
            "value": pd.to_numeric(raw[value_col], errors="coerce"),
            "approved": raw[cd_col].astype(str).str.startswith("A"),
        }
    ).reset_index(drop=True)
    out.loc[out["value"] <= -999990, "value"] = pd.NA
    out["value"] = out["value"].astype("float64")
    return out


def get_dv(
    site: str, param: str, start: str, end: str, refresh: bool = False
) -> pd.DataFrame:
    name = f"usgs_dv_{site}_{param}"

    def fetch() -> pd.DataFrame:
        raw, _ = nwis.get_dv(sites=site, parameterCd=param, start=start, end=end)
        return _tidy_dv(raw, param)

    meta = {
        "source": "USGS NWIS daily values via dataretrieval",
        "site": site,
        "parameterCd": param,
        "start": start,
        "end": end,
    }
    return fetch_cached(name, fetch, meta, refresh=refresh)


def get_iv(
    site: str, param: str, start: str, end: str, refresh: bool = False
) -> pd.DataFrame:
    name = f"usgs_iv_{site}_{param}_{start[:4]}_{end[:4]}"

    def fetch() -> pd.DataFrame:
        raw, _ = nwis.get_iv(sites=site, parameterCd=param, start=start, end=end)
        cd_cols = [c for c in raw.columns if c.endswith("_cd")]
        value_cols = [
            c for c in raw.columns if c.startswith(param) and not c.endswith("_cd")
        ]
        out = pd.DataFrame(
            {
                "datetime": raw.index.tz_convert("US/Central").tz_localize(None),
                "value": pd.to_numeric(raw[value_cols[0]], errors="coerce"),
                "approved": raw[cd_cols[0]].astype(str).str.startswith("A"),
            }
        ).reset_index(drop=True)
        out.loc[out["value"] <= -999990, "value"] = pd.NA
        return out

    meta = {
        "source": "USGS NWIS instantaneous values via dataretrieval",
        "site": site,
        "parameterCd": param,
        "start": start,
        "end": end,
    }
    return fetch_cached(name, fetch, meta, refresh=refresh)


def get_peaks(site: str, refresh: bool = False) -> pd.DataFrame:
    name = f"usgs_peaks_{site}"

    def fetch() -> pd.DataFrame:
        raw, _ = nwis.get_discharge_peaks(sites=site)
        out = pd.DataFrame(
            {
                "date": pd.to_datetime(raw.index)
                if isinstance(raw.index, pd.DatetimeIndex)
                else pd.to_datetime(raw["datetime"]),
                "peak_cfs": pd.to_numeric(raw["peak_va"], errors="coerce"),
                "gage_ht_ft": pd.to_numeric(raw["gage_ht"], errors="coerce"),
            }
        ).reset_index(drop=True)
        return out

    meta = {"source": "USGS NWIS annual peaks via dataretrieval", "site": site}
    return fetch_cached(name, fetch, meta, refresh=refresh)
