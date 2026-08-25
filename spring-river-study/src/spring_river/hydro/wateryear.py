"""Water-year (Oct-Sep) conventions per spec: WY labeled by ending year."""
import pandas as pd


def water_year(dates: pd.Series) -> pd.Series:
    d = pd.to_datetime(dates)
    return d.dt.year + (d.dt.month >= 10).astype(int)


def min7_dated(df: pd.DataFrame) -> pd.DataFrame:
    """Annual minimum 7-day mean discharge per water year, with the date on
    which the minimum window ENDS.

    Columns: wy, min7, end_date. One row per water year present in the daily
    span; min7/end_date are NaN/NaT for a WY with no complete 7-day window.

    Uses complete 7-day windows only (min_periods=7): windows touching a data
    gap are excluded rather than interpolated (spec: never interpolate).

    Must be called on the WHOLE series (not a per-water-year slice): a
    rolling window is free to span a water-year boundary (e.g. start in late
    September and end in early October) and is assigned to the water year of
    its ENDING day. Reindexing to a single water year's own extent before
    rolling silently makes those boundary-spanning windows impossible to
    form. NaN windows (touching a gap) are skipped intentionally — a WY with
    at least one complete window returns that window's minimum; a WY with NO
    complete windows correctly reduces to NaN.

    Ties resolve to the earliest ending date.
    """
    s = df.set_index("date")["value"].sort_index()
    full = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="D"))
    roll = full.rolling(7, min_periods=7).mean()
    wy = water_year(pd.Series(roll.index)).to_numpy()
    frame = pd.DataFrame({"wy": wy, "min7": roll.to_numpy(), "end_date": roll.index})
    ok = frame.dropna(subset=["min7"])
    rows = ok.loc[ok.groupby("wy")["min7"].idxmin()]
    all_wy = pd.DataFrame({"wy": sorted(frame["wy"].unique())})
    return all_wy.merge(rows, on="wy", how="left")[["wy", "min7", "end_date"]]


def min7(df: pd.DataFrame) -> pd.Series:
    """Annual minimum 7-day mean discharge per water year (Series indexed by
    wy). Thin wrapper over `min7_dated`; see it for the window conventions."""
    return min7_dated(df).set_index("wy")["min7"]


def daily_max_stage(iv: pd.DataFrame) -> pd.DataFrame:
    """Daily max of instantaneous stage; a day is 'approved' only if all its
    readings are. Hardy has no USGS daily-stage product, so this stands in.

    Input datetime must be tz-naive local time (US/Central, as produced by usgs.get_iv).
    Raises ValueError if datetime is tz-aware.
    """
    if iv["datetime"].dt.tz is not None:
        raise ValueError("datetime must be tz-naive local time")
    day = iv["datetime"].dt.normalize()
    out = (
        iv.groupby(day)
        .agg(value=("value", "max"), approved=("approved", "all"))
        .reset_index(names="date")
    )
    return out[["date", "value", "approved"]]
