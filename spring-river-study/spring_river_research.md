# Spring River research notes

## Phase 0 pre-check — verified 2026-08-24 (live API queries)

### USGS NWIS period of record (site service, `seriesCatalogOutput=true`)

| Site | Series | Begin | End | Count |
|---|---|---|---|---|
| 07069305 Hardy | DV discharge (00060) | 2001-10-01 | 2026-08-23 | 9,083 |
| 07069305 Hardy | DV stage (00065) | — | — | none |
| 07069305 Hardy | IV discharge | 2001-10-01 | present | |
| 07069305 Hardy | IV stage | 2007-10-01 | present | |
| 07069305 Hardy | Annual peaks | 2002-03-20 | 2025-04-05 | 24 |
| 07069500 Imboden | DV discharge | 1936-04-01 | 2026-08-23 | 30,261 |
| 07069500 Imboden | IV discharge | 1992-10-01 | present | |
| 07069500 Imboden | IV stage | 2007-10-01 | present | |
| 07069500 Imboden | Annual peaks | 1915-08 | 2025-04-05 | 90 |

**Spec risk #1 resolved:** the 1981 start does NOT hold for USGS data. Hardy is a
WY 2002+ discharge series with sub-daily stage from WY 2008. Imboden is the long
record for flood frequency (90 annual peaks, 1915–2025). There is no USGS daily
stage product at Hardy — daily stage statistics must be derived from IV.

### NWS NWPS HDYA4 (`api.water.noaa.gov/nwps/v1/gauges/HDYA4`)

- Flood categories (ft): action 8, minor 10, moderate 14, major 16 — matches spec.
- Historic crest list: 21 entries (one duplicate). Only entry before 2002 is the
  **record crest 29.0 ft on 1982-12-03** (flow not reported). Top crests:

| Date | Stage (ft) | Flow (cfs) |
|---|---|---|
| 1982-12-03 | 29.00 | n/a |
| 2025-04-05 | 22.82 | n/a |
| 2008-03-19 | 22.29 | 80,700 |
| 2008-04-11 | 20.81 | 70,081 |
| 2011-04-26 | 20.71 | 69,624 |
| 2009-10-30 | 17.41 | 48,273 |
| 2006-09-23 | 16.75 | n/a |
| 2017-04-30 | 16.65 | n/a |

**Implication for Q8 / spec risk #5:** the "22+ ft events: two in 18 years"
framing omits the 1982 29-ft crest. Any return-period statement for 22+ ft must
account for it (as a historical peak in B17C terms), and the 1981–2001 gap in
Hardy data means the 1982 crest is a censored-record observation, not part of a
systematic series. Imboden's 1915+ peaks are the defensible long series.

### Open items carried into the plan

- ACIS station sids for West Plains (KUNO vs COOP) — confirmed at Task 4/7 runtime.
- Mammoth Spring / Warm Fork gauge search — Task 7.
- Recharge-basin polygon: 30 km West Plains buffer approximation until a dye-trace
  delineation is obtained.
