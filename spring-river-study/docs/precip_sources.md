# Precipitation sources for the Mammoth Spring recharge area — evaluated 2026-08-25

Question: what is the best daily (ideally sub-daily) precipitation series over the Mammoth Spring recharge area (Howell / Oregon Co., MO) for 1981–present? Current build uses ACIS station pulls (KUNO 1998→, West Plains COOP 1948→ with gaps) and the PRISM 4 km daily grid averaged over a 30 km circle around West Plains.

## Recommendation

1. **Adopt the MoDNR "Mammoth Spring Recharge Area" polygon** as the basin (resolves spec risk #3). Saved at `docs/gis/mammoth_spring_recharge_modnr.geojson`. Source: Missouri DNR / Missouri Geological Survey, *Revised Recharge Areas of Selected Springs in the Big Four Region of the Ozarks*, layer modified 2022-09-14; MoDNR states 361.08 mi², equal-area recompute ≈ 349 mi². Bounds lon −91.954…−91.463, lat 36.496…36.823 — the polygon sits **south-east of West Plains toward Alton/Thayer**, not centred on West Plains as the buffer assumed. Endpoint: `https://services8.arcgis.com/RPgcHScWtnrsNIP7/arcgis/rest/services/Mammoth_Spring_Recharge_Area/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson` (license "custom" — cite MoDNR/MGS). Related layers: `Recharge_Area_Shared_by_Mammoth_and_Bill_Mac_Spring`, `greer_mammoth_recharge`.
2. **Adopt NOAA AORC v1.1 as the primary basin precipitation series** — 1 km, hourly, 1979→ (~10-day latency), free, anonymous S3: `s3://noaa-nws-aorc-v1-1-1km/{year}.zarr`, variable `APCP_surface` (mm/hr). It is the forcing NOAA uses for National Water Model calibration and is the only candidate that covers the full window at sub-daily resolution. Caveat: it is a blended product (Stage IV/MRMS radar + gauges + reanalysis), so it is not independent of PRISM in method.
3. **Keep PRISM (ACIS grid 21)** as the daily second gridded opinion, re-cut to the polygon.
4. **Keep the station set as gauge truth**, adding **Alton COOP `USC00230127` (1940→, active, on the polygon's eastern edge)** — the single best addition — plus the longer CoCoRaHS observers (`US1MOFSA091`, `US1MOFSA149` 2006→; `US1MOHL0030` 2011→ inside the polygon; `US1MOHL0041` 2015→).
5. **Stage IV via IEM** (4 km hourly, 2002→) for event-timing checks; **MRMS at IEM MTArchive** (1 km hourly, 2015→) — mirror what is needed now: IEM announced (2026-08-06) retention will shrink to a rolling 30 days. NCAR RDA ds507.5 is the Stage IV fallback.

Not worth adopting: Daymet v4 (station-only interpolation), gridMET (PRISM anomalies on NLDAS), NLDAS-2 (12.5 km cells swallow a 349 mi² polygon), Missouri Mesonet (no stations in either county; nearest ~55 km), NCEI CDO (same stations ACIS already serves).

## Access snippet (AORC)

```python
import xarray as xr, s3fs
fs = s3fs.S3FileSystem(anon=True)
ds = xr.open_mfdataset(
    [fs.get_mapper(f"noaa-nws-aorc-v1-1-1km/{y}.zarr") for y in range(1981, 2026)],
    engine="zarr", consolidated=True, parallel=True,
)
p = ds["APCP_surface"].sel(latitude=slice(36.45, 36.85), longitude=slice(-91.96, -91.45))
# mask with docs/gis/mammoth_spring_recharge_modnr.geojson (regionmask / rioxarray), then
daily_mm = p.resample(time="1D").sum()   # UTC days; shift when comparing with 7 AM COOP obs days
```

Pull one year at a time and cache as parquet (`data/raw/aorc_basin_pcpn.parquet`); a 0.5° × 0.4° subset for 45 years is a few hundred MB. Re-check recent years periodically — the bucket showed `.zmetadata` updates dated 2026-02-26 for 2020→.

## Comparison

| # | Source | Res / step | Period | Access | Auth | Basin fit | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | AORC v1.1 | 1 km / hourly | 1979→ | S3 zarr | none | full | **Primary** |
| 2 | COOP + CoCoRaHS (ACIS) | point / daily | Alton 1940→, West Plains 1948→, CoCoRaHS 2006→ | ACIS StnData | none | inside polygon | **Gauge truth** |
| 3 | PRISM (ACIS grid 21) | 4 km / daily | 1981→ | ACIS GridData | none | full | Cross-check, recut |
| 4 | Stage IV (IEM) | 4 km / hourly | 2002→ | HTTP grib | none | full | Event timing |
| 5 | MRMS (IEM) | 1 km / hourly | 2015→ | HTTP grib | none | full | Mirror now |
| 6 | Daymet v4 | 1 km / daily | 1980→ | pydaymet | none | full | Optional |
| 7 | gridMET | 4 km / daily | 1979→ | THREDDS | CC0 | full | Redundant |
| 8 | NLDAS-2 | 12.5 km / hourly | 1979→ | GES DISC | Earthdata | too coarse | Skip |
| 9 | MO Mesonet | point / hourly | 1992→ | agebb.missouri.edu | none | none in county | Skip |
| 10 | MoDNR polygon | vector | rev. 2022 | ArcGIS FeatureServer | custom | 349–361 mi² | **Adopt** |

## Implications for the study

- The 30 km West Plains buffer (~2,800 km²) is roughly three times the true recharge area and is offset north-west of it. Phase 4 (Q1 attribution) and Phase 6 (Q3 indices, coupling) should be re-run on the polygon-masked series; expect the precip–base-flow coefficients to tighten and the coupling r to rise.
- AORC's hourly resolution enables the antecedent-conditions and post-flood analyses at event scale, and a proper recharge-season intensity analysis.
- Proposed sequence: (a) ingest module `ingest/aorc.py` (S3 zarr → polygon mean → daily parquet); (b) `prism.get_basin_pcpn(polygon=…)` recut; (c) add Alton to `PRECIP_SIDS`; (d) re-run `make analysis`, diff headline numbers, record in `spring_river_research.md`.

Links: [AORC registry](https://registry.opendata.aws/noaa-nws-aorc/) · [AORC methods](https://www.weather.gov/media/owp/operations/aorc_v1_1_methods.pdf) · [MoDNR recharge area](https://gis-modnr.opendata.arcgis.com/datasets/mammoth-spring-recharge-area/about) · [MDC Spring River plan](https://mdc.mo.gov/sites/default/files/2022-05/240_2022_springriver.pdf) · [IEM MRMS archive](https://mesonet.agron.iastate.edu/archive/mrms.php) · [ACIS web services](https://docs.rcc-acis.org/acisws/)
