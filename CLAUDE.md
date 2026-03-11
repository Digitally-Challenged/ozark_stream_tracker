# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ozark Stream Tracker is a React/TypeScript application for monitoring real-time water levels on Arkansas and Oklahoma whitewater streams. It displays USGS gauge data with paddling condition indicators and provides an interactive precipitation map to correlate rainfall with watershed locations.

## Commands

```bash
# Development
npm run dev          # Start Vite dev server (port 5174)
npm run build        # Production build (runs parse-streams + vite build)
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run format       # Format with Prettier

# Backend (Turner Bend scraper - separate process)
cd server && npm install && npm run start  # Express server on port 3001
cd server && npm run dev                   # With nodemon auto-reload
```

## Architecture

### Data Flow

1. **USGS Gauges**: Frontend fetches directly from `waterservices.usgs.gov/nwis/iv/` API
2. **Turner Bend**: Custom gauge scraped via Netlify Function (`netlify/functions/turner-bend.js`) to avoid CORS, cached 15 minutes in-memory (warm invocations only)
3. **Precipitation Data**: IEM MRMS tile overlays for radar/accumulated precipitation, WPC QPF forecast images, and NWS observed precipitation images — all fetched directly, no API keys required
4. **NWS River Forecasts**: Client-side fetch from `api.water.noaa.gov/nwps/v1/gauges/{id}/stageflow` — 5-day stage/flow forecasts + flood categories. ~30% gauge coverage (others return 404). Cached 1 hour in localStorage.
5. **NOAA QPE Rainfall**: Client-side identify requests to `mapservices.weather.noaa.gov/raster/rest/services/obs/rfc_qpe/MapServer/identify` — observed precipitation totals (24h, 48h, 72h, 7d) at gauge coordinates. Cached 30 minutes in localStorage.

### Component Architecture

**Styling & Theming:**

- Material-UI sx prop exclusively (no CSS modules or Tailwind)
- Dark/light modes with theme-aware colors from ThemeContext
- Gradients and animations from `src/theme/waterTheme.ts` — exports `glassmorphism` (light/dark/colored variants with backdrop-filter blur, alpha backgrounds), `waterGradients` (shallow, medium, deep, rapid, dawn, day, dusk, night, optimal, warning, danger), `animations` (float, wave, ripple, shimmer, liquidFill), and `shadows` (glass, glow, elevation)
- Responsive design via MUI Grid and breakpoints (xs, sm, md, lg, xl)
- Glassmorphism pattern: backdrop-filter blur + alpha backgrounds + subtle borders for overlay components (LayerControl, ForecastPanel, map popups)

**Component Structure:**

```
src/components/
├── badges/       # RatingBadge, SizeBadge
├── common/       # LiveTime, utilities
├── core/         # Header, Footer
│   └── Header.tsx   # App header with navigation tabs (Dashboard/Precipitation), logo, refresh/filter/theme buttons
├── dashboard/    # DashboardHeader (LiveTime + LiveIndicator), DashboardSidebar (rating/size filters)
├── effects/      # GlassCard visual effects
├── icons/        # StreamConditionIcon, TrendIcon
├── precipitation/ # Precipitation map components
│   ├── MapView.tsx         # Leaflet map with tile layers and watershed markers
│   ├── ForecastPanel.tsx   # QPF forecast + observed precipitation sidebar
│   ├── LayerControl.tsx    # Tile layer toggle (MUI ToggleButtonGroup)
│   ├── WatershedPopup.tsx  # Marker popup with rainfall/forecast rows and detail link
│   ├── WeatherSummaryBar.tsx # Aggregate rain/rising counts above map
│   └── StageChart.tsx      # Inline SVG stage forecast chart (no chart library)
├── stream-page/  # Stream detail page components
└── streams/      # StreamCard, StreamTable, StreamGroup, StreamGroupHeader (collapsible status sections)
```

**Pages:** `src/pages/DashboardPage.tsx`, `src/pages/StreamPage.tsx`, `src/pages/PrecipitationMap.tsx` (lazy-loaded via `PrecipitationMapLazy.tsx`), `src/pages/WatershedDetailPage.tsx` (lazy-loaded via `WatershedDetailLazy.tsx`, route: `/precipitation/watershed/:gaugeId`)

**State Pattern:**

- **Global**: ThemeContext (dark/light), GaugeDataContext (gauge readings)
- **Local**: Component-level state (filters, expanded sections)
- **Persistence**: localStorage for theme, view preferences, gauge history

### Key Patterns

**Stream Data Model** (`src/types/stream.ts`):

- `StreamData`: Core stream info with gauge reference and target levels
- `LevelStatus`: X (too low), L (low), O (optimal), H (high)
- `LevelTrend`: rise, fall, hold, none

**Hooks** (`src/hooks/`):
| Hook | Purpose |
|------|---------|
| `useStreamGauge` | Fetches gauge data with auto-refresh (15min) |
| `useGaugeReading` | Context-based gauge data consumer |
| `useGaugeHistory` | localStorage history (24hr retention) |
| `useStreamStatus` | Memoized status lookup |
| `useRelativeTime` | Dynamic "5 minutes ago" strings |
| `useViewPreference` | Table/card toggle with responsive defaults |
| `useWatershedIntelligence` | Fetches NWS forecast + NOAA QPE precip in parallel, used by WatershedPopup and WatershedDetailPage |

**Gauge Hook** (`src/hooks/useStreamGauge.ts`):

- Single source of truth for fetching gauge readings
- Special-cases `TURNER_BEND` gauge ID to use backend scraper
- Compares current vs previous reading for trend calculation
- Auto-refreshes every 15 minutes (`API_CONFIG.REFRESH_INTERVAL_MS`)

**Header Component** (`src/components/core/Header.tsx`):

- Sticky AppBar with animated wave overlay (gradient with SVG wave patterns)
- Three main sections: Logo (left), Navigation tabs (center), Action buttons (right)
- **Logo section**: Clickable `ButtonBase` with kayaking icon + waves animation (4s float keyframes), navigates to `/dashboard`. App name "OZARK CREEK FLOW ZONE" (hidden on mobile < sm)
- **Navigation tabs**: Glassmorphic container with Dashboard and Precipitation tabs. Uses react-router `useNavigate()` and `useLocation()`. Active tab detection: `location.pathname === '/precipitation'`. Styling: active tab has white text with elevated background + cyan glow, inactive tabs dimmed (50% opacity). Responsive: text labels hidden on mobile (< sm), icons remain visible
- **Action buttons**: LiveIndicator (desktop only, hidden < md), Refresh button (spinning animation when `isLoading`), Filter button (rotates 180deg when drawer open, shows badge count), Theme toggle (dark/light mode icons)
- Consumes `GaugeDataContext` for refresh state and `ThemeContext` for mode toggle

**Filtering System:**

- State managed in `DashboardPage.tsx` (local component state)
- Sidebar drawer (`DashboardSidebar`) controls rating/size filters (only visible on dashboard)
- Filter logic shared via `filterByRatingAndSize()` utility from `src/utils/filterStreams.ts`

**Routing:**

- `/` → redirects to `/dashboard`
- `/dashboard` → Main dashboard with stream list (Header shows Dashboard tab as active)
- `/stream/:streamId` → Individual stream detail page (lazy-loaded)
- `/precipitation` → Precipitation map (lazy-loaded via `PrecipitationMapLazy.tsx`, Header shows Precipitation tab as active)

### Precipitation Map

**Route:** `/precipitation` — Interactive map overlaying real-time and accumulated precipitation on watershed gauge locations. Implemented and fully functional.

**Data Sources:**

- **IEM MRMS tiles** (Iowa Environmental Mesonet): Z/X/Y tile service at `mesonet.agron.iastate.edu/cache/tile.py/1.0.0/{layer}/{z}/{x}/{y}.png`. Layer IDs: `nexrad-n0q-900913` (radar), `q2-p24h` (24h), `q2-p48h` (48h), `q2-p72h` (72h). Opacity: 0.6.
- **WPC QPF images** (Weather Prediction Center): Static GIF forecast images (Day 1-3) from `wpc.ncep.noaa.gov/qpf/fill_94qwbg.gif` (Day 1), `fill_98qwbg.gif` (Day 2), `fill_99qwbg.gif` (Day 3)
- **NWS observed images** (AHPS): Date-stamped PNG images at `water.weather.gov/precip/downloads/{yyyy}/{mm}/{dd}/nws_precip_{period}_observed.png` where period is `last24hrs`, `last48hrs`, or `last7days`

**Mapping Library:** Leaflet with react-leaflet bindings, lazy-loaded via `PrecipitationMapLazy.tsx` wrapper. Vite code-splits into a `map-vendor` chunk (`vite.config.ts` manual chunks).

**Architecture:**

- **MapView.tsx**: Leaflet map container with CartoDB Positron base tiles (light: `light_all`, dark: `dark_all`), IEM MRMS precipitation overlay (dynamic URL: `mesonet.agron.iastate.edu/cache/tile.py/1.0.0/{layer}/{z}/{x}/{y}.png` with layer ID interpolation), and CircleMarker watershed markers (SVG-based, 12px radius, 2.5px white stroke). Uses `useGaugeDataContext()` to fetch real-time readings and `useMemo` to compute marker positions/colors on gauge data changes. Determines marker color via `getWatershedMarkerColor(statuses)` where statuses are computed per-stream using `determineLevel(reading.value, targetLevels)`. Glassmorphic popup styling with theme-aware backdrop-filter and alpha-blended backgrounds. Center: [35.5, -93.5] (Ozarks), default zoom: 8.
- **LayerControl.tsx**: MUI `ToggleButtonGroup` with glassmorphic background (`glassmorphism.dark` or `.light` from waterTheme). Positioned absolute (bottom-left, z-index 1000, 16px offset). Exclusive selection between radar, 24h, 48h, 72h layers. Selected button has gradient background (`linear-gradient(135deg, #30cfd0, #330867)`) with glow box-shadow. Radar button has `<Radar />` icon, 24h has `<WaterDrop />`, others text-only. All buttons have accessible aria-labels.
- **WatershedPopup.tsx**: Popup content for map markers. Displays gauge name (bold, 0.85rem), gradient divider line, current reading + trend label (colored via `TREND_COLORS` mapping: Rising=#4caf50, Falling=#f44336, Holding=#ff9800), and list of streams with individual status chips. Stream names are react-router `<Link>` components to `/stream/:streamId` using `getStreamIdFromName()` utility. Status chips use `STATUS_HEX_COLORS` for background with glow box-shadow. Shows "Awaiting data..." (italic, disabled color) when no gauge reading. Hover effect on stream rows (rgba(48, 207, 208, 0.08) background).
- **ForecastPanel.tsx**: Tabbed glassmorphic sidebar (QPF vs Observed) with full-width primary tabs (48px height, gradient indicator). Sub-tab selectors for forecast days (Day 1-3 WPC static GIF URLs: `fill_94qwbg.gif`, `fill_98qwbg.gif`, `fill_99qwbg.gif`) or observed periods (1/2/7-day NWS date-stamped PNGs generated via `getObservedUrl(period)` helper using current date). Uses internal `ImageWithFallback` component that catches `onError` events and displays fallback UI with `<CloudOff />` icon, message text, and gradient-styled external link ("View on source site"). Images have rounded corners, subtle border, and drop shadow.
- **PrecipitationMap.tsx**: Main page component with responsive layout. Desktop (>= md breakpoint): flex row with map + 350px forecast panel. Mobile (< md): stacked layout (map at 60vh height, panel below). Uses `groupStreamsByWatershed(allStreams)` to prepare watershed marker data, passes to MapView. State: `activeLayer` (PrecipLayer type) for tile control.

**Watershed Markers:** Streams grouped by shared `gauge.id` via `groupStreamsByWatershed()` utility. Each marker colored by highest-priority status among watershed streams (priority: High > Optimal > Low > TooLow). Coordinates sourced from `GAUGE_LOCATIONS` (exported from `src/data/gaugeLocations.ts` — hardcoded USGS Site Web Service data). Neutral gray (#9e9e9e) for missing gauge data.

**Navigation:** Header includes navigation icons (Dashboard and Precipitation) positioned in a glassmorphic container (right side, before action buttons). Each icon is an `IconButton` with react-router's `useNavigate()` for routing. Active icon determined via `useLocation().pathname` check (`!onPrecipMap` for Dashboard, `onPrecipMap` for Precipitation). Dashboard icon: `<Dashboard />`, Precipitation icon: `<Cloud />`. Active state: white color, elevated background (`rgba(255, 255, 255, 0.12)`), cyan glow box-shadow (`0 0 10px rgba(48, 207, 208, 0.2)`). Inactive state: 45% opacity, transparent background. Logo is also clickable, navigates to `/dashboard` on click.

**Known Edge Cases:** Tile loading failures handled gracefully by Leaflet (blank tiles). WPC/NWS image failures trigger fallback UI with "View on source site" link. Missing gauge data shows neutral gray markers with "Loading..." in popups.

**Implementation Status:** Fully implemented as of commit `a527c86` (2026-03-11). Includes complete component suite (MapView, LayerControl, ForecastPanel, WatershedPopup), routing integration, watershed grouping utilities, unit tests, and vite config for code-splitting map vendor chunk.

**Precipitation Query Service** (`src/services/precipQueryService.ts`):

- **Purpose**: Query point-specific precipitation totals from NOAA RFC QPE (Quantitative Precipitation Estimation) MapServer
- **API**: `mapservices.weather.noaa.gov/raster/rest/services/obs/rfc_qpe/MapServer/identify` (ArcGIS REST identify endpoint)
- **Layer IDs**: `{ last24h: 17, last48h: 23, last72h: 29, last7d: 35 }` (multi-day accumulated rainfall rasters)
- **Request Format**: Point geometry (lat/lng in EPSG:4326), queries all 4 layers in single HTTP call, includes mapExtent + imageDisplay params for identify service
- **Response Parsing**: Extracts "Pixel Value: X.XX" from layer results, handles "NoData"/"Null" gracefully (returns null)
- **Caching**: localStorage with 30-minute TTL (key: `precip-{gaugeId}`, stores `PrecipTotals` object with timestamp)
- **Error Handling**: Returns empty `PrecipTotals` (all nulls) on fetch failure or timeout (5s abort signal)
- **Interface**: `PrecipTotals { gaugeId, lat, lng, last24h, last48h, last72h, last7d }` (all values in inches or null)
- **Use Case**: Powers Watershed Intelligence — rainfall context in popups, summary bar, and detail page
- **Testing**: Unit tests in `tests/unit/precipQueryService.test.ts` — validates parsing, caching, NoData handling, error fallback

**NWS Forecast Service** (`src/services/nwsForecastService.ts`):

- **Purpose**: Fetch river stage forecasts and flood categories from NWS NWPS API
- **API**: `api.water.noaa.gov/nwps/v1/gauges/{gaugeId}/stageflow` (observed + 5-day forecast) and root gauge endpoint for flood categories
- **Coverage**: ~30% of gauges (others return 404, gracefully handled as null)
- **Caching**: localStorage with 1-hour TTL (key: `nws-forecast-{gaugeId}`)
- **Interface**: `NwsForecast { gaugeId, data: NwsForecastPoint[], peakForecast, floodCategories }`
- **Testing**: `tests/unit/nwsForecastService.test.ts` — parsing, 404 handling, cache TTL

**Watershed Intelligence** (scan → preview → deep dive):

- **WeatherSummaryBar**: Glassmorphic strip above the precipitation map showing aggregate counts: watersheds with rain (24h) and gauges forecast rising. Fetched via staggered batch (100ms delay per gauge) in PrecipitationMap page.
- **Enhanced WatershedPopup**: Shows rainfall row (24h/48h inches) and forecast row (peak stage by day) in addition to existing gauge reading/trend/stream list. Includes "View Watershed Forecast →" link.
- **WatershedDetailPage** (`/precipitation/watershed/:gaugeId`): Full subpage with stat cards (stage, trend, status), inline SVG stage forecast chart (StageChart.tsx), rainfall totals (24h/48h/72h/7d), stream list with optimal ranges, and flood stages bar. Lazy-loaded.

### Important Files

- `src/data/streamData.ts`: Static stream definitions (90+ streams with gauge mappings)
- `src/data/gaugeLocations.ts`: Lat/lng coordinates for each unique gauge ID (hardcoded from USGS Site Web Service)
- `src/data/streamContent.generated.ts`: Auto-generated from markdown (via parse-streams)
- `src/constants/index.ts`: API URLs, refresh intervals, level thresholds
- `src/utils/streamLevels.ts`: Level/trend calculation logic; exports `STATUS_HEX_COLORS` (canonical hex per status) and `STATUS_GRADIENT_COLORS` (primary/secondary gradient pairs) — single source of truth for status colors across all components
- `src/utils/trendUtils.ts`: Trend display helpers — `getTrendLabel()`, `getTrendMuiColor()`, `getTrendInfo()` (returns `{icon, label, muiColor}` or null for `LevelTrend.None`); used by `StreamDetail` and `StreamConditionIcon`
- `src/utils/filterStreams.ts`: `filterByRatingAndSize(streams, selectedRatings, selectedSizes)` — shared filter logic used by `DashboardPage` and `StreamTable`
- `src/utils/watershedGrouping.ts`: Watershed utilities — `groupStreamsByWatershed()` groups streams by shared gauge ID into `Map<string, Watershed>`, `getWatershedMarkerColor(statuses: LevelStatus[])` returns highest-priority status color (High > Optimal > Low > TooLow) for precipitation map markers, returns neutral gray (#9e9e9e) for empty array
- `src/utils/streamIds.ts`: Explicit stream name to content ID mapping
- `src/services/turnerBendScraper.ts`: Frontend `TurnerBendScraper` class — calls `/api/turner-bend/current`, 15-min localStorage cache, 5s fetch timeout via `AbortSignal.timeout`
- `src/components/common/LiveTime.tsx`: Real-time clock component — displays current time with 12h format + AM/PM, updates every second (configurable via `updateInterval` prop), shows full timestamp on hover via MUI Tooltip
- `src/services/precipQueryService.ts`: NOAA QPE point-query service — fetches rainfall totals (24h/48h/72h/7d) from RFC MapServer identify endpoint, 30min localStorage cache, returns `PrecipTotals` interface with null fallback for NoData
- `src/services/nwsForecastService.ts`: NWS NWPS forecast service — fetches river stage forecasts + flood categories, 1hr localStorage cache, returns `NwsForecast` or null (404 for uncovered gauges)
- `server/turnerBendScraper.js`: Local dev scraper for Turner Bend gauge (Express server)
- `netlify/functions/turner-bend.js`: Production Netlify Function scraper for Turner Bend gauge

### Storage Strategy

**localStorage Keys:**

- `ozark-stream-tracker-theme`: Dark/light mode preference
- `ozark-stream-tracker-view-mode`: Table vs cards preference
- `gauge-reading-history`: 24-hour rolling gauge history for trends
- `turner-bend-gauge-data`: 15-minute client-side cache for Turner Bend
- `nws-forecast-{gaugeId}`: 1-hour cache for NWS river forecasts
- `precip-{gaugeId}`: 30-minute cache for NOAA QPE precipitation totals

### Environment Variables

- `VITE_API_URL`: Turner Bend API endpoint — dev default: `http://localhost:3001/api/turner-bend/current`; production default: `/api/turner-bend/current` (relative URL routed to Netlify Function via redirect)

## Build & Configuration

**Build Pipeline:**

1. Netlify build command (`netlify.toml`): `npm run build && cd netlify/functions && npm install`
   - `npm run build` runs two steps: `npm run parse-streams` then `vite build`
   - `npm run parse-streams` (scripts/parse-streams.ts) → generates `src/data/streamContent.generated.ts`
   - `vite build` with code splitting (react-vendor, mui-vendor, date-vendor, map-vendor chunks)
   - `cd netlify/functions && npm install` → installs cheerio for the Netlify Function (runs after vite build)

**Netlify Configuration** (`netlify.toml` + `public/_redirects`):

- Node.js runtime: version 20 (`NODE_VERSION = "20"` in `[build.environment]`)
- API redirect `/api/turner-bend/*` uses `force = true` so it takes precedence over the SPA `/*` catch-all
- `public/_redirects` mirrors the same redirect rules as `netlify.toml` as a fallback (belt-and-suspenders)
- Function bundler: esbuild; cheerio declared as `external_node_modules` (installed separately, not bundled)
- Static assets served with 1-year immutable cache (`/assets/*`)
- Security headers applied globally: `X-Frame-Options`, `X-XSS-Protection`, `X-Content-Type-Options`, `Referrer-Policy`

**TypeScript:** Strict mode enabled with `noUnusedLocals` and `noUnusedParameters`

**Testing (Vitest):**

- Config lives in `vite.config.ts` (`test` key): globals enabled, `jsdom` environment, setup from `tests/setup.ts`
- Test files: `tests/**/*.{test,spec}.{ts,tsx}` — run with `npm run test` (or `npx vitest`)
- Unit tests in `tests/unit/`: `streamLevels.test.ts`, `trendUtils.test.ts`, `filterStreams.test.ts`, `watershedGrouping.test.ts` (tests grouping logic and marker color priority)
- New utilities follow TDD: write failing test in `tests/unit/`, implement, verify passing

**Key Constants** (`src/constants/index.ts`):

- USGS refresh: 15 minutes
- Level freshness: 1.5h (very fresh), 3h (fresh), 10h (recent)
- Change threshold: 0.1ft for trend detection

## Backend / Netlify Functions

Turner Bend scraping runs as a **Netlify Function** in production (`netlify/functions/turner-bend.js`):

- Scrapes `https://www.turnerbend.com/WaterLevel.html` using built-in Node.js `https` + cheerio
- In-memory cache: 15 minutes (not persistent across cold starts)
- Bundled via esbuild; only cheerio declared as `external_node_modules` (built-in `https` needs no bundling)
- Dependencies managed in `netlify/functions/package.json` (installed during Netlify build)

**API Endpoints (via Netlify redirect):**

- `GET /api/turner-bend/current` → `/.netlify/functions/turner-bend` - Get latest water level (cached)
- `POST /api/turner-bend/scrape` → `/.netlify/functions/turner-bend` - Force immediate re-scrape

**Local Development (Express server):**

The `server/` directory contains a standalone Express server for local dev:

- `GET /api/turner-bend/current` - Get latest water level (cached)
- `POST /api/turner-bend/scrape` - Force immediate scrape
- `GET /health` - Health check
- Caches data in `server/turner-bend-data.json` with 30-day rolling history; refreshes every 4 hours via cron

**Known Limitations:**

- Scraping relies on regex patterns - breaks if Turner Bend website HTML changes
- Netlify Function cache is in-memory only - cold starts re-fetch immediately

## Frontend/Backend Split

The frontend is a Vite SPA deployed to Netlify. In production, the Turner Bend scraper runs as a **Netlify Function** co-deployed with the frontend - no separate server process needed. The `server/` Express server is used for local development only. The frontend can run without the backend (Turner Bend will show errors).

<!-- AUTO-MANAGED: git-insights -->

## Git Insights

**Recent Feature: Precipitation Map (commits bc97f77, a527c86, 45dd1c1, 68d458b)**

- **Glassmorphism UI Pattern**: Applied to precipitation map components (LayerControl, ForecastPanel, map popups) using `glassmorphism.dark`/`.light` from waterTheme with backdrop-filter blur and alpha-blended backgrounds
- **Component Responsibilities**: MapView (Leaflet + tile layers + markers), LayerControl (toggle button group), ForecastPanel (tabbed forecast images), WatershedPopup (marker popup content with gauge + stream list)
- **Data Integration**: Real-time gauge readings from GaugeDataContext, watershed grouping via `groupStreamsByWatershed()`, marker colors via `getWatershedMarkerColor()` with priority-based status selection
- **Styling Patterns**: MUI sx prop with theme-aware colors, gradient backgrounds for active states (`linear-gradient(135deg, #30cfd0, #330867)`), glow box-shadows on selected elements, hover effects with subtle alpha backgrounds
- **Error Handling**: Image loading fallbacks with `<CloudOff />` icon and external links to source sites (WPC, NWS) for precipitation images

**Recent Refactoring: App/Header Component Cleanup (commits 6a65f0a, b4fbd72)**

- **State Management**: Moved filter state (selectedRatings, selectedSizes) from App.tsx to DashboardPage.tsx — filters are page-specific, not global
- **Header Navigation**: Refactored from tabs to icon buttons — Dashboard and Precipitation icons in glassmorphic container, active state with glow effect
- **Component Simplification**: App.tsx now only handles routing and global providers (Theme, GaugeData) — no UI state or filter props passing
- **Time Format**: LiveTime component changed from 24h (`HH:mm`) to 12h (`h:mm a`) format with AM/PM for better readability

**Recent Changes: UI Cleanup and Precipitation Service (commits 32d7a82, d49ad4a)**

- **DashboardHeader Simplification**: Removed "93 Runs" counter and swapped order to "Updated [LiveTime] [LiveIndicator]" — cleaner right-aligned layout
- **StreamGroupHeader Simplification**: Removed stream count chips from collapsible status section headers — reduces visual noise, keeps focus on status labels and emojis
- **Precipitation Query Service**: Implemented `precipQueryService.ts` with NOAA RFC QPE MapServer integration — fetches 24h/48h/72h/7d rainfall totals at point locations (lat/lng), localStorage caching (30min TTL), handles NoData gracefully
- **Testing**: Added comprehensive unit tests for precipQueryService — validates identify response parsing, cache behavior, NoData handling, error fallback
<!-- END AUTO-MANAGED -->
