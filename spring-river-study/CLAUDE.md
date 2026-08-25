# Spring River Study

## Purpose
Quantify the hydrologic regime of Spring River at Hardy, AR (USGS 07069305) 1981–2026:
base-flow trend and attribution, flood frequency and stationarity, precipitation
regime over the Mammoth Spring recharge basin. Output is a reproducible report.

## Conventions
- Water year (Oct–Sep) for all annual hydrologic stats; calendar year for precip totals
  unless stated. Recharge season = Sep–Feb.
- Units: cfs, feet (NGVD/NAVD as reported by USGS — record datum), inches.
- Every figure: source, period, approval status in caption.
- Every trend claim: test name, effect size, CI, n. No bare p-values.
- Provisional data: analysis runs twice (all / approved-only); flag any conclusion
  that changes.
- Never interpolate across gaps > 7 days. Never edit data/raw.

## Data contract
See docs/data_inventory.md. Ingest modules must be idempotent and cached.

## Analysis order
Phases 0–8 in plan.md. Phases 0–6 complete (2026-08-25); Phase 7 (report assembly)
next. Outputs: docs/phase4_baseflow.md, docs/phase5_floods.md, docs/phase6_precip.md;
decisions and headline results in spring_river_research.md. `make analysis` rebuilds all.

## Style
Scientific, terse. Thesis → evidence → limitation. No hedging language in place
of numbers.
