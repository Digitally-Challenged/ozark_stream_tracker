"""Water-year (Oct-Sep) conventions per spec: WY labeled by ending year."""
import pandas as pd


def water_year(dates: pd.Series) -> pd.Series:
    d = pd.to_datetime(dates)
    return d.dt.year + (d.dt.month >= 10).astype(int)


def min7(df: pd.DataFrame) -> pd.Series:
    """Annual minimum 7-day mean discharge per water year.

    Uses complete 7-day windows only (min_periods=7): windows touching a data
    gap are excluded rather than interpolated (spec: never interpolate).
    """
    s = df.set_index("date")["value"].sort_index()
    full = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="D"))
    roll = full.rolling(7, min_periods=7).mean()
    wy = water_year(pd.Series(roll.index))
    return roll.groupby(wy.values).min().rename("min7")


def daily_max_stage(iv: pd.DataFrame) -> pd.DataFrame:
    """Daily max of instantaneous stage; a day is 'approved' only if all its
    readings are. Hardy has no USGS daily-stage product, so this stands in."""
    day = iv["datetime"].dt.normalize()
    out = (
        iv.groupby(day)
        .agg(value=("value", "max"), approved=("approved", "all"))
        .reset_index(names="date")
    )
    return out[["date", "value", "approved"]]
