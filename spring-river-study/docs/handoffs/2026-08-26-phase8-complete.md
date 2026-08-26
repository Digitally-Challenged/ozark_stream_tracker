# Handoff — Spring River study: phases 0–8 complete; what a future session can pick up

Written 2026-08-26 (session of 2026-08-25). Everything is merged and pushed; there is no half-finished work. This doc exists so the next session knows what is settled, what is open, and where the traps are.

## Where things stand

- Repo `~/Documents/GitHub/ozark_stream_tracker`, `main` at **b8f834f** (= origin/main). Study in `spring-river-study/` (Python 3.12, `uv`). 214 tests; `make report` reproduces every phase document byte-for-byte from the git-ignored `data/raw` cache (verified from a fresh clone at efabce9). Work in an orca worktree and branch off `origin/main` (one branch, one effort).
- Two merges on 2026-08-25: `53297cd` second edition (MoDNR recharge polygon, NOAA AORC v1.1 basin precipitation, `West Plains 1948–` gauge record, source comparison, lay final report) and `b8f834f` Phase 8 adversarial review with corrections.
- Corrected conclusions live in **`spring-river-study/review.md`** (24 claims, verdict / attack / falsifier / checks / what would settle it) with the reviewer reports in `docs/review_phase8/`. Decisions and headline table: `spring_river_research.md`. Technical report: `reports/report.qmd` → `report.html`. Lay report source: `reports/plain.html` (hand-typed numbers; refresh by hand when headlines move).
- Published artifacts — republish to the SAME URLs by passing `url`: lay final report https://claude.ai/code/artifact/461090a5-7702-4c8f-8fa2-0a498fde7390 ; technical report https://claude.ai/code/artifact/a1dc172c-1984-4789-9ca4-cb3ba474b90c (fragment = `report.html` head styles/scripts + body in `<div class="quarto-light">`, `<title>Spring River at Hardy</title>`). Nick's standing instruction for the lay page: a standalone final report — no edition language, no references to prior studies.
- Session ledger (rulings, incidents): `/private/tmp/claude-501/…/scratchpad/sdd-ledger-final.md` may be gone; the substance is in memory (`spring-river-study-status.md`) and `docs/handoffs/2026-08-25-precip-edition.md` (closing section).

## What the next session could take up (Nick has not chosen; all are in review.md "Data that would resolve…")

1. **Close the AORC product-step question** — re-pull ONE AORC cell at the West Plains gauge coordinate (−91.874, 36.727) from `s3://noaa-nws-aorc-v1-1-1km` (the cache keeps only the polygon mean; `ingest/aorc._open_year_subset` + `.sel(latitude=…, longitude=…, method="nearest")`), compare its ten indices with the gauge, split at 2002. Cheap (46 stores × seconds). Also an independent grid with no 2002 input change (nClimGrid-Daily or Livneh) over the polygon.
2. **Where the extra Hardy low-flow water enters** — South Fork at Saddle (07069295, DV 2010→) carries ~34 of the ~90 cfs unexplained; 07069220 (Spring R nr Mammoth Spring, 1988–95/2010–16) shows no gain just below the vent; South Fork nr Hardy (07069300) has no daily record. A synoptic seepage run is the field answer; on the desk, check whether 07069300/07069270/07069265 have peaks or partial records via the OGC `time-series-metadata`.
3. **COOP/KUNO homogenisation** — replace the constant 1.068 catch ratio (`climate/westplains.py`) with quantile matching over the 282 overlap months; the days≥1in result depends on the ratio (nothing significant at 1.00), and a residual 1998 step hides SDII/recharge trends.
4. **Flood frequency** — PeakFQ/EMA with the 1982 crest (≈156,000 cfs; 29.0 ft) as a historical peak over a stated perceptibility threshold; the Arkansas/Missouri regional-skew study value (REGIONAL_SKEW=−0.2 is a B17B map approximation; `hydro/freq_lp3.fit_lp3_historical` is a B17B weighting without the skew bias correction).
5. Housekeeping nits: `climate/seasonal.py` Timedelta deprecation (11 warnings); `hydro/postflood.skip_day_sensitivity` and `phase4._mammoth_cross_source_section` mutate module globals — thread parameters instead; the Codex generalist review (`codex:codex-rescue`) never delivered a report — its scope was covered by the domain reviews.

## Gotchas learned (the ones not already in CLAUDE.md / handoff of 2026-08-25)

- **Subagents and git.** One implementer detached HEAD, three commits were made on it, and a later agent's `git checkout <branch>` stranded them (recovered from reflog). Every dispatch now says: never checkout/switch/reset/stash; verify `git branch --show-current && git log -1` after every implementer. Do the same.
- **Fresh-clone check:** `cp -R data/raw dest/data/raw` nests into `raw/raw`; use `cp -R data/raw/. dest/data/raw/`, and print the clone's HEAD before trusting a result.
- **Artifacts:** publishing to an existing URL from a fresh session is refused until you `read` the live version; the tool saves it and tells you the path. Keep the `<title>` stable ("Spring River at Hardy" for the technical report).
- **USGS legacy `waterdata.usgs.gov/nwis/measurements` returns HTML now**; use `api.waterdata.usgs.gov/ogcapi/v0/collections/{field-measurements,channel-measurements,monitoring-locations,time-series-revisions}/items?monitoring_location_id=USGS-07069305` (paginate via `links[rel=next]`). Field measurements have up to 5 stage readings per visit — reduce to one per `field_visit_id` before joining (a bug that multiplied 134 visits to 350 pairs was fixed in `ingest/field_measurements.py`).
- AORC bucket carries whole calendar years and lags by months (2025.zarr was the latest on 2026-08-25); `aorc.get_basin_pcpn` clamps to what is cached/listed and warns offline.
- West Plains gauges are **10.7 mi** apart (town COOP 36.727 N; airport KUNO 36.879 N, 120 ft higher); COOP catches 6.8 % more; both are inside the MoDNR recharge polygon's NW edge. 2026: the two gauges agree (37.5 vs 38.4 in over the last year).
- Regex-anchored phase-doc lines (see `reports/report.qmd` helpers `section`, `doc_re`, `doc_trend`) fail the render on wording drift — by design. Add new content under new headers; never retype numbers in prose.

## Suggested skills

- `superpowers:brainstorming` first if Nick picks one of the items above — the scope of each is a judgment call (e.g. one-cell AORC check vs a full independent-grid ingest).
- `superpowers:writing-plans` → `superpowers:subagent-driven-development` for anything touching the runners; `superpowers:test-driven-development` (project rule for new modules; `uv run pytest -q` is the gate).
- `codex-signoff` before merging anything that changes a conclusion (whole branch → `codex:codex-rescue`; note it stalled once today — check the report file exists before relying on it).
- `artifact-design` + `dataviz` if the lay page gets new charts; re-render with Playwright (`npx -y playwright screenshot --full-page`) and inspect crops before publishing — the artifact viewer would not scroll under browser automation.
- `superpowers:verification-before-completion` — fresh-clone `make report` with the cache copied correctly.
- `handoff` at the end.
