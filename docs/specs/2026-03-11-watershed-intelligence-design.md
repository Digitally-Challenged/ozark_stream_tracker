# Watershed Intelligence — Design Spec

**Date:** 2026-03-11
**Status:** Approved
**Goal:** Add observed rainfall totals and NWS river forecasts to the precipitation map and a new watershed detail subpage, following a scan → preview → deep dive information hierarchy.

---

## Data Sources

### NWS River Forecasts (NWPS API)

**Base URL:** `https://api.water.noaa.gov/nwps/v1/gauges/{usgsId}`

| Endpoint              | Returns                                                             | Notes                              |
| --------------------- | ------------------------------------------------------------------- | ---------------------------------- |
| `/stageflow`          | Observed + forecast time-series (stage ft, flow kcfs)               | 5-day forecast at 6-12hr intervals |
| `/stageflow/forecast` | Forecast only                                                       | Same data, filtered                |
| (root)                | Gauge metadata, flood categories, current observed/forecast summary | Action/minor/moderate/major stages |

- **Coverage:** Partial — ~30% of our 36 gauges have NWS forecast data. Others return 404.
- **No API key required.** CORS allowed for client-side fetch.
- **Verified working:** Mulberry River (07252000) returns full forecast data.

### NOAA QPE (Quantitative Precipitation Estimates)

**Base URL:** `https://mapservices.weather.noaa.gov/raster/rest/services/obs/rfc_qpe/MapServer`

**Endpoint:** `/identify` — point query returning precipitation value at a lat/lng.

**Request parameters:**

- `geometry`: `{"x": <lng>, "y": <lat>, "spatialReference": {"wkid": 4326}}`
- `geometryType`: `esriGeometryPoint`
- `layers`: `visible:5,11,17,23` (1hr, 6hr, 24hr, 48hr layers)
- `mapExtent`: bounding box around point
- `imageDisplay`: `600,550,96`
- `returnGeometry`: `false`
- `f`: `json`

**Returns:** Pixel value at point = precipitation in inches for each queried layer.

**Resolution:** ~4km grid. No API key required.

**Layers used:**
| Layer ID | Period |
|----------|--------|
| 5 | Last 1 hour |
| 17 | Last 24 hours |
| 23 | Last 48 hours |
| 29 | Last 72 hours |
| 35 | Last 7 days |

---

## Architecture

### New Services

#### `src/services/nwsForecastService.ts`

```typescript
interface NwsForecastPoint {
  validTime: string;
  stage: number; // ft
  flow: number; // kcfs
}

interface NwsForecast {
  gaugeId: string;
  observed: NwsForecastPoint[];
  forecast: NwsForecastPoint[];
  peakForecast: { stage: number; time: string } | null;
  floodCategories: {
    action: number;
    minor: number;
    moderate: number;
    major: number;
  } | null;
}
```

- `fetchForecast(gaugeId: string): Promise<NwsForecast | null>`
- Fetches from `/stageflow` endpoint (contains both observed + forecast)
- Also fetches gauge root for flood categories
- Returns `null` on 404 (gauge has no NWS data)
- **Cache:** localStorage with 1-hour TTL, keyed by `nws-forecast-{gaugeId}`
- **Timeout:** 5s via `AbortSignal.timeout`

#### `src/services/precipQueryService.ts`

```typescript
interface PrecipTotals {
  gaugeId: string;
  lat: number;
  lng: number;
  last24h: number | null; // inches
  last48h: number | null;
  last72h: number | null;
  last7d: number | null;
}
```

- `fetchPrecipTotals(gaugeId: string, lat: number, lng: number): Promise<PrecipTotals>`
- Sends `identify` request to NOAA QPE MapServer with gauge coordinates
- Parses response to extract inch values from pixel data
- **Cache:** localStorage with 30-minute TTL, keyed by `precip-{gaugeId}`
- **Timeout:** 5s via `AbortSignal.timeout`
- Returns `null` values for any layer that fails or returns no-data

### New Hook

#### `src/hooks/useWatershedIntelligence.ts`

```typescript
interface WatershedIntelligence {
  forecast: NwsForecast | null;
  precip: PrecipTotals | null;
  loading: boolean;
  error: Error | null;
}
```

- `useWatershedIntelligence(gaugeId: string, lat: number, lng: number): WatershedIntelligence`
- Fetches both NWS forecast and precip data in parallel on mount
- Manages loading/error state
- Used by WatershedPopup (on popup open) and WatershedDetailPage (on page load)

---

## UI Changes

### Level 1: Precipitation Map Enhancements

#### Summary Bar (new component)

**File:** `src/components/precipitation/WeatherSummaryBar.tsx`

A glassmorphic strip above the map showing aggregate insights:

- "X watersheds got rain (24h)" — count of watersheds with >0.1 in rainfall
- "Y gauges forecast rising" — count of gauges with NWS forecast showing increase

Positioned as a fixed bar between the header and the map. Only renders once precip data is loaded. Shows a skeleton/loading state while fetching.

**Data flow:** The PrecipitationMap page fetches precip totals for all watersheds on mount (batched with short delays to avoid hammering the API), stores results in local state, passes aggregate counts to WeatherSummaryBar.

**Important:** Batch the QPE requests — don't fire 36 simultaneous identify requests. Stagger with 100ms delays, and only fetch for visible/nearby watersheds first.

#### Enhanced Watershed Popup

**File:** Modify `src/components/precipitation/WatershedPopup.tsx`

Add two compact rows between the reading/trend line and the stream list:

1. **Rainfall row:** Rain icon + "1.2 in (24h) · 2.8 in (48h)" — from precipQueryService
2. **Forecast row:** Trend icon + "→ 5.1 ft by Thu" — from nwsForecastService, only when available

Add a "View Forecast →" link at the bottom that navigates to `/precipitation/watershed/{gaugeId}`.

Both rows show small loading skeletons while data fetches, and gracefully hide if data unavailable.

### Level 2: Watershed Detail Subpage

**Route:** `/precipitation/watershed/:gaugeId`

**File:** `src/pages/WatershedDetailPage.tsx` (lazy-loaded via `WatershedDetailLazy.tsx`)

**Layout:** Full-width page with back-navigation to precipitation map.

**Sections (top to bottom):**

1. **Header** — Gauge name, back button ("← Back to Map")

2. **Current Conditions** — Three GlassCard stat cards in a row:
   - Stage (current reading in ft)
   - Trend (Rising/Falling/Stable with colored icon)
   - Status (highest-priority status among streams)

3. **Stage Forecast Chart** — Only renders when NWS forecast data exists.
   - Inline SVG line chart (no chart library dependency)
   - X-axis: time (days), Y-axis: stage (ft)
   - Solid line for observed data, dashed line for forecast
   - Horizontal dashed lines for flood categories (if available)
   - Responsive width, fixed ~200px height

4. **Rainfall Totals** — Four GlassCard cells in a row:
   - 24h, 48h, 72h, 7-day precipitation in inches
   - Each card shows the value prominently with a subtle rain icon
   - Null values show "—"

5. **Streams on This Gauge** — List of all streams sharing this gauge:
   - Stream name (linked to `/stream/:streamId`)
   - Current status chip
   - Target levels context (e.g., "Optimal: 3-5 ft")

6. **Flood Stages** (when NWS data available) — Horizontal bar or table showing:
   - Action / Minor / Moderate / Major stage thresholds
   - Current level indicator on the scale

**Responsive:** On mobile (< md), stat cards stack 1-per-row. Chart maintains aspect ratio. Rainfall cards go 2x2 grid.

---

## Routing Changes

**File:** `src/App.tsx`

Add route:

```typescript
<Route path="/precipitation/watershed/:gaugeId" element={<WatershedDetailLazy />} />
```

The WatershedDetailPage reads `gaugeId` from URL params, looks up the gauge in `GAUGE_LOCATIONS` for coordinates, then uses `useWatershedIntelligence` to fetch data.

---

## Caching Strategy

| Key Pattern              | TTL    | Data                             |
| ------------------------ | ------ | -------------------------------- |
| `nws-forecast-{gaugeId}` | 1 hour | NWS stageflow + flood categories |
| `precip-{gaugeId}`       | 30 min | QPE point precipitation totals   |

Cache uses the same localStorage pattern as `turner-bend-gauge-data`: JSON with `{ data, timestamp }` wrapper, checked on read.

---

## Error Handling

- **NWS 404:** Gauge has no forecast. `forecast` is `null`. Forecast sections don't render. No error shown to user.
- **NOAA QPE timeout/error:** Precip totals show "—" for failed layers. No error banner.
- **Network failure:** Loading state shown briefly, then graceful fallback (sections don't render).
- **No errors bubble to the user** unless all data sources fail simultaneously.

---

## Testing

- `tests/unit/nwsForecastService.test.ts` — Mock API responses for forecast parsing, 404 handling, cache TTL
- `tests/unit/precipQueryService.test.ts` — Mock identify responses, inch value extraction, null handling
- Existing watershed grouping tests unchanged

---

## Files Created/Modified

| Action | File                                                 |
| ------ | ---------------------------------------------------- |
| Create | `src/services/nwsForecastService.ts`                 |
| Create | `src/services/precipQueryService.ts`                 |
| Create | `src/hooks/useWatershedIntelligence.ts`              |
| Create | `src/components/precipitation/WeatherSummaryBar.tsx` |
| Create | `src/components/precipitation/StageChart.tsx`        |
| Create | `src/pages/WatershedDetailPage.tsx`                  |
| Create | `src/pages/WatershedDetailLazy.tsx`                  |
| Create | `tests/unit/nwsForecastService.test.ts`              |
| Create | `tests/unit/precipQueryService.test.ts`              |
| Modify | `src/components/precipitation/WatershedPopup.tsx`    |
| Modify | `src/pages/PrecipitationMap.tsx`                     |
| Modify | `src/App.tsx`                                        |

---

## What's Deliberately Excluded (YAGNI)

- Forecast rainfall in inches (requires GRIB parsing — too heavy for frontend)
- Historical comparison charts
- Push notifications or alerts
- Chart library dependency (D3, Recharts, etc.) — inline SVG is sufficient
