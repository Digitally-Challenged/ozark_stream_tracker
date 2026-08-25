"""Split daily series at gaps > 7 days (project rule: never interpolate
across them). Gaps of <= max_gap_days are linearly interpolated."""
import pandas as pd


def segment_gapfree(df: pd.DataFrame, max_gap_days: int = 7) -> list[pd.DataFrame]:
    """Return gap-free daily segments with columns `date, value`.

    Reindexes to a daily calendar (missing rows count as gaps), linearly
    interpolates runs of <= `max_gap_days` missing days, and splits at longer
    runs. Each returned frame is sorted, contiguous, and NaN-free.
    """
    s = df.set_index("date")["value"].sort_index().astype("float64")
    if s.empty:
        return []
    full = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="D"))
    missing = full.isna()
    run_id = (missing != missing.shift()).cumsum()
    run_len = missing.groupby(run_id).transform("size")
    long_gap = missing & (run_len > max_gap_days)
    filled = full.interpolate(limit_area="inside")
    filled[long_gap] = float("nan")
    seg_id = (long_gap != long_gap.shift()).cumsum()
    out = []
    for _, chunk in filled.groupby(seg_id):
        chunk = chunk.dropna()
        if len(chunk):
            out.append(chunk.rename("value").rename_axis("date").reset_index())
    return out
