"""Q4: do major floods reduce recharge? Post-flood base flow vs matched
non-flood years (spec §2.2).

Controls are non-flood years matched on two dimensions: precip over the
same-calendar post window AND antecedent state (mean base flow over the
`PRE_STATE_DAYS` before the event / its calendar equivalent). Distance is the
sum of standardized absolute differences, each term scaled by the candidate
pool's standard deviation; a term whose pool SD is zero or undefined (or whose
event-side value is NaN) contributes nothing, so matching degrades to the
remaining dimension rather than failing.
"""

from typing import NamedTuple

import numpy as np
import pandas as pd

from spring_river.hydro.baseflow import eckhardt_segmented

# Days skipped after the event date so the window starts past the flood
# recession (7 days was inside the recession limb and contaminated "base flow").
RECESSION_SKIP_DAYS = 30
# Antecedent-state window: mean base flow over this many days before the event.
PRE_STATE_DAYS = 90
# Minimum defined-baseflow days per window-month for a candidate year to count.
MIN_DAYS_PER_MONTH = 20
# Minimum defined-baseflow days in the antecedent window for a candidate.
MIN_PRE_DAYS = 60
# Minimum fraction of a precip window's calendar days that must carry a value.
# AORC has documented missing days; below this the window total is NaN and the
# precip term drops out of the match distance rather than reading as "dry".
MIN_PRECIP_COVERAGE = 0.9


class Candidate(NamedTuple):
    year: int
    bf_cfs: float
    precip_in: float
    pre_bf_cfs: float


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
    """Precip total over [start, end). NaN when fewer than `MIN_PRECIP_COVERAGE`
    of the window's calendar days carry a value."""
    w = basin[(basin["date"] >= start) & (basin["date"] < end)]["pcpn_in"]
    days = (end - start).days
    if days <= 0 or w.notna().sum() < MIN_PRECIP_COVERAGE * days:
        return float("nan")
    return float(w.sum())


def _pre_state(bf: pd.DataFrame, event: pd.Timestamp) -> tuple[float, int]:
    """Mean base flow over the `PRE_STATE_DAYS` ending the day before `event`."""
    return _window_mean(bf, event - pd.DateOffset(days=PRE_STATE_DAYS), event)


def _post_start(event: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(event) + pd.DateOffset(days=RECESSION_SKIP_DAYS)


def post_event_baseflow(
    dv_q: pd.DataFrame, event_dates: pd.Series, months: int = 6
) -> pd.DataFrame:
    """Mean Eckhardt base flow over the `months` following each event,
    starting `RECESSION_SKIP_DAYS` after it.

    Columns: event_date, post_baseflow_mean_cfs, post_days.
    """
    bf = eckhardt_segmented(dv_q)
    rows = []
    for d in pd.to_datetime(event_dates):
        s, e = _window(_post_start(d), months)
        m, n = _window_mean(bf, s, e)
        rows.append({"event_date": d, "post_baseflow_mean_cfs": m, "post_days": n})
    return pd.DataFrame(
        rows, columns=["event_date", "post_baseflow_mean_cfs", "post_days"]
    )


def _candidate_years(
    bf: pd.DataFrame,
    basin_precip: pd.DataFrame,
    event: pd.Timestamp,
    months: int,
    event_years: set[int],
) -> list[Candidate]:
    """Non-flood years (no event within ±1 yr) whose same-calendar post window
    and antecedent window both have enough defined-baseflow days."""
    out = []
    for y in sorted(set(bf["date"].dt.year)):
        if any(abs(y - ey) <= 1 for ey in event_years):
            continue
        ce_event = _same_day_in_year(event, y)
        cs = _same_day_in_year(_post_start(event), y)
        ce = cs + pd.DateOffset(months=months)
        m, n = _window_mean(bf, cs, ce)
        if n < months * MIN_DAYS_PER_MONTH:
            continue
        pre, n_pre = _pre_state(bf, ce_event)
        if n_pre < MIN_PRE_DAYS:
            continue
        out.append(Candidate(y, m, _window_precip(basin_precip, cs, ce), pre))
    return out


def _std_term(delta: float, sd: float) -> float:
    """|delta|/sd, or 0 when the term is undefined (NaN delta, or sd not > 0)."""
    if not (sd > 0) or np.isnan(delta):
        return 0.0
    return abs(delta) / sd


def _match(cands: list[Candidate], post_p: float, pre_bf: float, k: int) -> list[Candidate]:
    sd_p = float(np.std([c.precip_in for c in cands], ddof=1)) if len(cands) > 1 else 0.0
    sd_b = float(np.std([c.pre_bf_cfs for c in cands], ddof=1)) if len(cands) > 1 else 0.0

    def dist(c: Candidate) -> float:
        return _std_term(c.precip_in - post_p, sd_p) + _std_term(c.pre_bf_cfs - pre_bf, sd_b)

    return sorted(cands, key=dist)[:k]


def matched_comparison(
    dv_q: pd.DataFrame,
    basin_precip: pd.DataFrame,
    event_dates: pd.Series,
    months: int = 6,
    k: int = 3,
) -> pd.DataFrame:
    """Post-event base flow vs the mean of the `k` non-flood years closest in
    standardized (post-window precip, antecedent base flow) distance."""
    bf = eckhardt_segmented(dv_q)
    events = pd.DatetimeIndex(pd.to_datetime(event_dates))
    event_years = set(events.year)
    rows = []
    for d in events:
        s, e = _window(_post_start(d), months)
        post_bf, _ = _window_mean(bf, s, e)
        post_p = _window_precip(basin_precip, s, e)
        pre_bf, _ = _pre_state(bf, d)
        cands = _candidate_years(bf, basin_precip, d, months, event_years)
        top = _match(cands, post_p, pre_bf, k)
        matched_bf = float(np.mean([c.bf_cfs for c in top])) if top else float("nan")
        matched_p = float(np.mean([c.precip_in for c in top])) if top else float("nan")
        matched_pre = float(np.mean([c.pre_bf_cfs for c in top])) if top else float("nan")
        rows.append(
            {
                "event_date": d,
                "post_bf_cfs": post_bf,
                "post_p_in": post_p,
                "pre_bf_cfs": pre_bf,
                "matched_years": ",".join(str(c.year) for c in top),
                "matched_bf_cfs": matched_bf,
                "matched_p_in": matched_p,
                "matched_pre_bf_cfs": matched_pre,
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
            "pre_bf_cfs",
            "matched_years",
            "matched_bf_cfs",
            "matched_p_in",
            "matched_pre_bf_cfs",
            "diff_cfs",
            "diff_pct",
        ],
    )


def _unique_controls(cmp: pd.DataFrame) -> int:
    if "matched_years" not in cmp:
        return 0
    used = cmp.loc[cmp["diff_pct"].notna(), "matched_years"].fillna("")
    return len({y for cell in used for y in str(cell).split(",") if y})


def paired_summary(cmp: pd.DataFrame, n_boot: int = 5000, seed: int = 0) -> dict:
    """Bootstrap 95% CI on the mean of `diff_pct`.

    The CI reflects event-to-event variation ONLY: matching uncertainty (which
    control years were chosen) and reuse of the same control year across
    events are not propagated, so the band is narrower than the true
    uncertainty. `n_unique_controls` (distinct matched years across events with
    a defined diff) is reported so readers can judge the reuse.
    """
    d = cmp["diff_pct"].dropna().to_numpy()
    if len(d) == 0:
        nan = float("nan")
        return {"n": 0, "mean_diff_pct": nan, "lo": nan, "hi": nan, "n_unique_controls": 0}
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
        "n_unique_controls": _unique_controls(cmp),
    }
