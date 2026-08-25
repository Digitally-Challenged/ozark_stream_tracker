"""Gap detection and approval-status accounting. Spec: flag gaps > 7 days."""
import pandas as pd


def find_gaps(df: pd.DataFrame, max_days: int = 7) -> pd.DataFrame:
    s = df.set_index("date")["value"].sort_index()
    full = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="D"))
    missing = full.isna()
    group = (missing != missing.shift()).cumsum()
    runs = (
        pd.DataFrame({"missing": missing, "group": group})
        .reset_index(names="date")
        .groupby("group")
        .agg(
            gap_start=("date", "min"),
            gap_end=("date", "max"),
            days=("date", "size"),
            missing=("missing", "first"),
        )
    )
    gaps = runs[runs["missing"] & (runs["days"] > max_days)]
    return gaps[["gap_start", "gap_end", "days"]].reset_index(drop=True)


def approval_summary(df: pd.DataFrame) -> dict:
    approved_frac = float(df["approved"].mean())
    provisional = df.loc[~df["approved"], "date"]
    return {
        "approved_frac": approved_frac,
        "provisional_from": provisional.min() if len(provisional) else None,
    }
