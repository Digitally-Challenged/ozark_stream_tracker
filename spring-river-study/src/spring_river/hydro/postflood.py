"""Q4: do major floods reduce recharge? Post-flood base flow vs precip-matched
non-flood years (spec §2.2)."""

import numpy as np
import pandas as pd

from spring_river.hydro.baseflow import eckhardt_segmented

# Days skipped after the event date so the window starts past the storm recession.
RECESSION_SKIP_DAYS = 7
# Minimum defined-baseflow days per window-month for a candidate year to count.
MIN_DAYS_PER_MONTH = 20


def _window(start: pd.Timestamp, months: int) -> tuple[pd.Timestamp, pd.Timestamp]:
    return start, start + pd.DateOffset(months=months)


def _same_day_in_year(ts: pd.Timestamp, year: int) -> pd.Timestamp:
    """`ts` moved to `year`; Feb 29 falls back to Feb 28 in non-leap years."""
    try:
        return ts.replace(year=year)
    except ValueError:
        return ts.replace(year=year, day=28)


def _window_mean(
    bf: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp
) -> tuple[float, int]:
    w = bf[(bf["date"] >= start) & (bf["date"] < end)]["baseflow"].dropna()
    return (float(w.mean()) if len(w) else float("nan")), int(len(w))


def _window_precip(
    basin: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp
) -> float:
    return float(
        basin[(basin["date"] >= start) & (basin["date"] < end)]["pcpn_in"].sum()
    )


def post_event_baseflow(
    dv_q: pd.DataFrame, event_dates: pd.Series, months: int = 6
) -> pd.DataFrame:
    """Mean Eckhardt base flow over the `months` following each event.

    Columns: event_date, post_baseflow_mean_cfs, post_days.
    """
    bf = eckhardt_segmented(dv_q)
    rows = []
    for d in pd.to_datetime(event_dates):
        s, e = _window(
            pd.Timestamp(d) + pd.DateOffset(days=RECESSION_SKIP_DAYS), months
        )
        m, n = _window_mean(bf, s, e)
        rows.append({"event_date": d, "post_baseflow_mean_cfs": m, "post_days": n})
    return pd.DataFrame(
        rows, columns=["event_date", "post_baseflow_mean_cfs", "post_days"]
    )


def _candidate_years(
    bf: pd.DataFrame,
    basin_precip: pd.DataFrame,
    start: pd.Timestamp,
    months: int,
    event_years: set[int],
) -> list[tuple[int, float, float]]:
    """Non-flood years (no event within ±1 yr) whose same-calendar window has
    enough defined-baseflow days, as (year, mean_bf_cfs, precip_in)."""
    out = []
    for y in sorted(set(bf["date"].dt.year)):
        if any(abs(y - ey) <= 1 for ey in event_years):
            continue
        cs = _same_day_in_year(start, y)
        ce = cs + pd.DateOffset(months=months)
        m, n = _window_mean(bf, cs, ce)
        if n < months * MIN_DAYS_PER_MONTH:
            continue
        out.append((y, m, _window_precip(basin_precip, cs, ce)))
    return out


def matched_comparison(
    dv_q: pd.DataFrame,
    basin_precip: pd.DataFrame,
    event_dates: pd.Series,
    months: int = 6,
    k: int = 3,
) -> pd.DataFrame:
    """Post-event base flow vs the mean of the `k` non-flood years whose same
    calendar window had the closest precip total."""
    bf = eckhardt_segmented(dv_q)
    events = pd.DatetimeIndex(pd.to_datetime(event_dates))
    event_years = set(events.year)
    rows = []
    for d in events:
        s, e = _window(
            pd.Timestamp(d) + pd.DateOffset(days=RECESSION_SKIP_DAYS), months
        )
        post_bf, _ = _window_mean(bf, s, e)
        post_p = _window_precip(basin_precip, s, e)
        cands = _candidate_years(bf, basin_precip, s, months, event_years)
        top = sorted(cands, key=lambda c: abs(c[2] - post_p))[:k]
        matched_bf = float(np.mean([c[1] for c in top])) if top else float("nan")
        matched_p = float(np.mean([c[2] for c in top])) if top else float("nan")
        rows.append(
            {
                "event_date": d,
                "post_bf_cfs": post_bf,
                "post_p_in": post_p,
                "matched_years": ",".join(str(c[0]) for c in top),
                "matched_bf_cfs": matched_bf,
                "matched_p_in": matched_p,
                "diff_cfs": post_bf - matched_bf,
                "diff_pct": 100.0 * (post_bf - matched_bf) / matched_bf
                if matched_bf
                else float("nan"),
            }
        )
    return pd.DataFrame(
        rows,
        columns=[
            "event_date",
            "post_bf_cfs",
            "post_p_in",
            "matched_years",
            "matched_bf_cfs",
            "matched_p_in",
            "diff_cfs",
            "diff_pct",
        ],
    )


def paired_summary(cmp: pd.DataFrame, n_boot: int = 5000, seed: int = 0) -> dict:
    """Bootstrap 95% CI on the mean of `diff_pct`."""
    d = cmp["diff_pct"].dropna().to_numpy()
    if len(d) == 0:
        nan = float("nan")
        return {"n": 0, "mean_diff_pct": nan, "lo": nan, "hi": nan}
    rng = np.random.default_rng(seed)
    boots = np.array(
        [rng.choice(d, len(d), replace=True).mean() for _ in range(n_boot)]
    )
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {
        "n": int(len(d)),
        "mean_diff_pct": float(d.mean()),
        "lo": float(lo),
        "hi": float(hi),
    }
