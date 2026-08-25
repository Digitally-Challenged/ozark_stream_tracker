"""CPC Oceanic Niño Index — ENSO covariate for Q1 attribution (spec §1.3)."""
import io

import pandas as pd
import requests

from spring_river.ingest.cache import fetch_cached

ONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
_CENTER_MONTH = {
    "DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6,
    "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12,
}


def parse_oni(text: str) -> pd.DataFrame:
    raw = pd.read_csv(io.StringIO(text), sep=r"\s+")
    month = raw["SEAS"].map(_CENTER_MONTH)
    date = pd.to_datetime({"year": raw["YR"], "month": month, "day": 1})
    return pd.DataFrame({"date": date, "anom": raw["ANOM"].astype("float64")}).sort_values("date").reset_index(drop=True)


def get_oni(refresh: bool = False) -> pd.DataFrame:
    def fetch() -> pd.DataFrame:
        resp = requests.get(ONI_URL, timeout=60)
        resp.raise_for_status()
        return parse_oni(resp.text)

    return fetch_cached("cpc_oni", fetch, {"source": "CPC ONI", "url": ONI_URL}, refresh=refresh)


def recharge_season_oni(oni: pd.DataFrame) -> pd.Series:
    d = oni["date"]
    wy = d.dt.year + (d.dt.month >= 9).astype(int)   # Sep..Dec belong to next WY's recharge season
    in_season = d.dt.month.isin([9, 10, 11, 12, 1, 2])
    return oni.loc[in_season].groupby(wy[in_season])["anom"].mean().rename("oni_recharge")
