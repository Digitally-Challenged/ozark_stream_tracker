# Handoff — Spring River study: second edition on supplemental precipitation data

Status: implemented 2026-08-25 on `study/precip-edition` — see `docs/superpowers/plans/2026-08-25-spring-river-precip-edition.md`. Lay-reader artifact (new, 2026-08-25): https://claude.ai/code/artifact/461090a5-7702-4c8f-8fa2-0a498fde7390 — source reports/plain.html (hand-authored; numbers typed from reports/tables and the phase docs, plus the West Plains COOP 1948→ pull cached as data/raw/acis_pcpn_USC00238880_1948). Refresh by hand when headlines move.

Written 2026-08-25. Next session's job: rebuild the precipitation-dependent parts of the report on the MoDNR recharge polygon and NOAA AORC, then republish.

## Where things stand

- Repo: `~/Documents/GitHub/ozark_stream_tracker` (main at `7d0f09c`, pushed). Study lives in `spring-river-study/` (Python 3.12, `uv`). Work in an orca worktree, e.g. `~/orca/workspaces/ozark_stream_tracker/goatfish`; branch off `origin/main` (one branch, one effort — suggested name `study/precip-edition`).
- Phases 0–7 of `spring-river-study/plan.md` are complete: 141 tests, `make analysis` (ledger + phases 4–7) and `make report` (Quarto → `reports/report.html`) reproduce from the git-ignored `data/raw` cache. Quarto 1.10.18 is at `~/.local/bin/quarto` (Makefile finds it; brew cask needs sudo).
- Findings, decisions, and headline numbers: `spring-river-study/spring_river_research.md`. Review record: `docs/review_phase4-6.md`. Per-phase reports: `docs/phase4_baseflow.md` … `phase7_seasonality.md`.
- Published artifacts (republish to the SAME URLs by passing `url`): technical report https://claude.ai/code/artifact/a1dc172c-1984-4789-9ca4-cb3ba474b90c ; lay-reader brief https://claude.ai/code/artifact/7512d71e-8a5a-404d-a102-2a71e92a1f49 (source `reports/brief.html`, hand-authored — numbers typed from the tables; must be refreshed by hand when headlines move). The technical-report artifact is `reports/report.html` with `<head>` styles/scripts + body extracted into one fragment and a `<title>` added (see the extraction snippet pattern in this session: strip `<meta>`/`<title>`, wrap body in a `<div>`).

## The task

Replace the 30 km West Plains PRISM buffer with (a) the actual MoDNR Mammoth Spring recharge polygon and (b) NOAA AORC v1.1 as the primary basin precipitation series; add Alton COOP; re-run the precip-dependent analyses; publish a second edition that states what changed.

Everything you need is evaluated in **`spring-river-study/docs/precip_sources.md`** (sources, access snippets, verdicts) — read it first. The polygon is at `docs/gis/mammoth_spring_recharge_modnr.geojson` (~349–361 mi², bounds lon −91.954…−91.463, lat 36.496…36.823 — SE of West Plains; the old buffer was ~3× too big and offset NW).

### Sequence

1. `ingest/aorc.py`: S3 zarr `s3://noaa-nws-aorc-v1-1-1km/{year}.zarr` (anonymous), var `APCP_surface` mm/hr, subset to the polygon bbox, mask with the GeoJSON, area-mean, daily sum → `data/raw/aorc_basin_pcpn.parquet` (`date, pcpn_in`; note UTC days vs 7 AM COOP obs days) and an hourly parquet if cheap. Cache via `ingest/cache.fetch_cached`; one year per fetch; add deps `xarray zarr s3fs shapely rasterio` (or `regionmask`). Expect tens of minutes of network time — run in the background.
2. `ingest/prism.get_basin_pcpn`: accept a polygon; request the bbox from ACIS GridData and mask locally. Keep the old buffer callable for the comparison edition.
3. Add `USC00230127` (Alton, 1940→) to `PRECIP_SIDS` in `ingest/pull_all.py`; pull it.
4. Swap the basin series used by `hydro/ledger.py`, `analysis/phase4.py` (Q1 attribution, Q4 matching, antecedent), `analysis/phase6.py` (Q3 indices, coupling). Suggest a config switch `BASIN_PRECIP_SOURCE = "aorc" | "prism_polygon" | "prism_buffer"` so all three can be run and diffed.
5. `make analysis` for each source; write a comparison table (Q1 coefficients + residual trend, Q4 diff %, Q3 basin index trends, coupling lag/r) into `spring_river_research.md` and a new report section "What changed with the polygon and AORC".
6. Re-run the sensitivity rule (all vs approved-only) — unchanged code path.
7. Update `reports/report.qmd` (numbers from tables; parser asserts on phase-doc lines, so wording changes fail the render on purpose) and `reports/brief.html` (hand edit), `make report`, fresh-clone check, Codex adversarial pass (`codex-signoff` skill; whole-branch → `codex:codex-rescue`), merge with a merge commit, push, republish both artifacts, update memory.

### Known gotchas

- `acis.get_station_pcpn` caches by station id only — a different start date returns the cached range; use `refresh=True` deliberately (the COOP 1948 backfill is still pending for the same reason).
- `usgs.get_dv` likewise caches by site+param; the Imboden cache is 1981+ (study window). Do not refresh it casually — QA/ledger outputs would change.
- Peaks from the cache are tz-aware UTC; strip tz before comparing with DV/IV dates (see `_peaks_by_wy` in `analysis/phase5.py`).
- AORC pre-2002 has no radar input; its sub-daily advantage is really 2002→. The polygon excludes recharge shared with Bill Mac / Greer springs (separate MoDNR layers) — note, don't model.
- IEM is cutting MRMS retention to 30 days (announced 2026-08-06); mirror anything needed from `mtarchive.geol.iastate.edu` early if Stage IV/MRMS cross-checks are wanted.
- Repo has a husky/lint-staged pre-commit hook that reformats HTML (prettier) — edit `reports/brief.html` in the repo, not a scratch copy, and stage by explicit filename (never `git add -A`).
- Reviewer lessons from this round (see `docs/review_phase4-6.md`): keep predictors strictly antecedent (min7 window ends `end_date`, predictors end `end_date − 7`), coverage gates against calendar season length, every trend claim with effect size + CI + n, all/approved-only sensitivity with CHANGED flags.

## Open items not in this task's scope

USGS rating-shift/datum records for Hardy (Q5/Q8 provisional); real regional skew (`REGIONAL_SKEW=-0.2` is a B17B-map approximation); PeakFQ/EMA follow-up; fitted BFImax; linear-reservoir attribution; Phase 8 (`review.md`, adversarial review of conclusions).

## Suggested skills

- `superpowers:writing-plans` then `superpowers:subagent-driven-development` — plan file under `docs/superpowers/plans/2026-MM-DD-spring-river-precip-edition.md`, parallel agents for the independent modules (aorc ingest, prism recut, runner swaps).
- `superpowers:test-driven-development` — the project rule for new modules; `uv run pytest -q` is the gate.
- `codex-signoff` — mandatory independent review before merge (two passes caught real bugs last round).
- `dataviz` + `artifact-design` — only if the brief gets new charts.
- `superpowers:verification-before-completion` — fresh-clone `make report` before claiming done.
- `handoff` at the end.
