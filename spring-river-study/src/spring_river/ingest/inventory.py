"""Phase 0: data inventory. Writes docs/data_inventory.md from live metadata."""
from datetime import date

import pandas as pd
from dataretrieval import nwis

from spring_river.config import DOCS_DIR, SITE_HARDY, SITE_IMBODEN
from spring_river.ingest.acis import find_stations
from spring_river.ingest.nwps import flood_categories, get_gauge_info, historic_crests
from spring_river.ingest.prism import _bbox_around
from spring_river.config import WEST_PLAINS_LATLON


def _period_of_record(site: str) -> pd.DataFrame:
    """Per-parameter/service date ranges from the NWIS site service."""
    raw, _ = nwis.get_info(sites=site, seriesCatalogOutput=True)
    cols = ["parm_cd", "data_type_cd", "begin_date", "end_date", "count_nu"]
    have = [c for c in cols if c in raw.columns]
    df = raw[have].copy()
    return df[df["parm_cd"].isin(["00060", "00065"]) | df["data_type_cd"].eq("pk")]


def _mammoth_spring_search() -> tuple[pd.DataFrame, list[str]]:
    """Search NWIS for gauges near Mammoth Spring / Warm Fork (spec §1.1).

    Returns (frame, warnings) — exceptions are recorded as warning strings, never
    folded into the result frame as fake rows.
    """
    frames = []
    warnings: list[str] = []
    for state, name_like in [("ar", "mammoth"), ("mo", "warm fork")]:
        try:
            raw, _ = nwis.what_sites(stateCd=state, hasDataTypeCd="dv")
            hit = raw[raw["station_nm"].str.lower().str.contains(name_like, na=False)]
            frames.append(hit[["site_no", "station_nm", "site_tp_cd"]])
        except Exception as exc:  # noqa: BLE001 - inventory records failures as warnings
            warnings.append(f"{state}/{name_like}: {exc}")
    frame = (
        pd.concat(frames, ignore_index=True)
        if frames
        else pd.DataFrame(columns=["site_no", "station_nm", "site_tp_cd"])
    )
    return frame, warnings


def main() -> None:
    lines = [f"# Data inventory — generated {date.today().isoformat()}", ""]

    for site, label in [(SITE_HARDY, "Hardy 07069305"), (SITE_IMBODEN, "Imboden 07069500")]:
        lines += [f"## USGS {label} — period of record", ""]
        lines.append(_period_of_record(site).to_markdown(index=False))
        lines.append("")

    lines += ["## Mammoth Spring / Warm Fork gauge search", ""]
    search_frame, search_warnings = _mammoth_spring_search()
    lines.append(search_frame.to_markdown(index=False))
    lines.append("")

    lines += ["## Warnings", ""]
    if search_warnings:
        lines += [f"- {w}" for w in search_warnings]
    else:
        lines.append("(none)")
    lines.append("")

    lines += ["## USGS Mammoth Spring gauges — period of record", ""]
    for site, label in [("07069220", "Spring River near Mammoth Spring, AR"), ("07069190", "Mammoth Spring at Mammoth Spring")]:
        lines += [f"### {site} — {label}", ""]
        lines.append(_period_of_record(site).to_markdown(index=False))
        lines.append("")

    lines += ["## ACIS precip stations within ~40 km of West Plains", ""]
    bbox = _bbox_around(*WEST_PLAINS_LATLON, 40)
    lines.append(find_stations(bbox).to_markdown(index=False))
    lines.append("")

    lines += ["## NWPS HDYA4 flood categories (ft)", ""]
    lines.append(str(flood_categories(get_gauge_info())))
    lines.append("")

    lines += ["## NWPS HDYA4 historic crests", ""]
    lines.append(historic_crests(get_gauge_info()).to_markdown(index=False))
    lines += [
        "",
        "## Decisions (fill in after review)",
        "",
        "- [ ] Long flood-frequency series: Hardy alone or Imboden-extended?",
        "- [ ] Primary precip station (ASOS vs COOP) and its working ACIS sid",
        "- [ ] Mammoth Spring discharge series available: yes/no",
        "- [ ] IV data availability from 2007+ for rating-drift analysis: yes/no",
        "- [ ] Legacy NWIS endpoint status note",
    ]

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    out = DOCS_DIR / "data_inventory.md"
    out.write_text("\n".join(lines))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
