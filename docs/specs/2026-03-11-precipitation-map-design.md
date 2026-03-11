# Precipitation Map Feature — Design Spec

## Problem

Whitewater paddlers need to correlate precipitation data with watershed locations to predict which creeks will be runnable. The Arkansas Canoe Club community previously used a Google Maps precipitation overlay (deprecated June 2014) for this purpose. No modern equivalent exists in the Ozark Stream Tracker.

## Solution

Add an interactive precipitation map page (`/precipitation`) that overlays real-time and accumulated precipitation data on a map showing watershed gauge locations, alongside a forecast panel with NOAA QPF imagery.

## Architecture

### Layout

```
Desktop (>= md / 900px):
┌──────────────────────────────────────────────────┐
│  Header  [existing]  + precipitation nav button  │
├────────────────────────┬─────────────────────────┤
│                        │  Forecast Panel (350px)  │
│   Leaflet Map          │  ┌───────────────────┐  │
│   (fills left side)    │  │[Day1][Day2][Day3] │  │
│                        │  │  WPC QPF image    │  │
│   Precipitation tiles  │  └───────────────────┘  │
│   + watershed markers  │  Observed Panel         │
│                        │  ┌───────────────────┐  │
│   Layer toggle:        │  │ NWS observed img  │  │
│   [Radar][24h][48h]    │  └───────────────────┘  │
│   [72h]                │                         │
├────────────────────────┴─────────────────────────┤
│  Footer                                          │
└──────────────────────────────────────────────────┘

Mobile (< md / 900px):
┌──────────────────────┐
│  Header              │
├──────────────────────┤
│  Leaflet Map         │
│  (full width, 60vh)  │
│                      │
│  Layer toggle        │
│  [Radar][24h][48h]   │
├──────────────────────┤
│  Forecast tab bar    │
│  [QPF] [Observed]    │
│  Image panel         │
├──────────────────────┤
│  Footer              │
└──────────────────────┘
```

Desktop layout switches to mobile stacked layout at `md` breakpoint (900px) since the map needs meaningful width alongside the 350px panel.

### Dependencies

```
leaflet        (~40KB gzipped) — map rendering
react-leaflet  (~8KB gzipped)  — React bindings for Leaflet
@types/leaflet (devDependency) — TypeScript definitions
```

Leaflet CSS must be imported: `import 'leaflet/dist/leaflet.css'` in `PrecipitationMap.tsx`.

No API keys required for any data source.

### Bundle Strategy

The page is lazy-loaded following the existing `StreamPageLazy.tsx` pattern. A new `PrecipitationMapLazy.tsx` wrapper uses `React.lazy()` + `Suspense` with a `CircularProgress` fallback.

Vite `manualChunks` in `vite.config.ts` gets a new entry:

```typescript
'map-vendor': ['leaflet', 'react-leaflet']
```

This keeps the map library in its own chunk, only loaded when navigating to `/precipitation`.

### Data Sources

#### IEM MRMS Tile Overlays (Iowa Environmental Mesonet)

Free tile service, no API key. Standard Z/X/Y tiles compatible with Leaflet.

URL template: `https://mesonet.agron.iastate.edu/cache/tile.py/1.0.0/{layer}/{z}/{x}/{y}.png`

| Layer ID            | Description                            |
| ------------------- | -------------------------------------- |
| `nexrad-n0q-900913` | Current NEXRAD radar reflectivity      |
| `q2-p24h`           | MRMS 24-hour accumulated precipitation |
| `q2-p48h`           | MRMS 48-hour accumulated precipitation |
| `q2-p72h`           | MRMS 72-hour accumulated precipitation |

#### WPC QPF Forecast Images (Weather Prediction Center)

Static GIF images showing forecast precipitation amounts. These are national-scale maps — paddlers visually locate the Ozark region within the image.

| Image | URL                                                 |
| ----- | --------------------------------------------------- |
| Day 1 | `https://www.wpc.ncep.noaa.gov/qpf/fill_94qwbg.gif` |
| Day 2 | `https://www.wpc.ncep.noaa.gov/qpf/fill_98qwbg.gif` |
| Day 3 | `https://www.wpc.ncep.noaa.gov/qpf/fill_99qwbg.gif` |

#### NWS Observed Precipitation

Direct image URLs from the NWS Advanced Hydrologic Prediction Service:

| Period | URL                                                                                       |
| ------ | ----------------------------------------------------------------------------------------- |
| 1-day  | `https://water.weather.gov/precip/downloads/2026/03/11/nws_precip_last24hrs_observed.png` |
| 2-day  | `https://water.weather.gov/precip/downloads/2026/03/11/nws_precip_last48hrs_observed.png` |
| 7-day  | `https://water.weather.gov/precip/downloads/2026/03/11/nws_precip_last7days_observed.png` |

These URLs use the current date. The component constructs the URL dynamically using today's date: `https://water.weather.gov/precip/downloads/{YYYY}/{MM}/{DD}/nws_precip_last{period}_observed.png`

If the image fails to load (404 or network error), show a fallback message: "Observed precipitation image unavailable" with a link to `https://water.weather.gov/precip/`.

### Watershed Markers

Streams are grouped by their shared `gauge.id` from `streamData.ts`. Each unique gauge ID represents one watershed, producing ~35 markers.

#### Gauge Coordinates

Coordinates for each USGS gauge are available from the USGS Site Web Service:
`https://waterservices.usgs.gov/nwis/site/?format=rdb&sites={siteId}&siteOutput=expanded`

These will be hardcoded in `src/data/gaugeLocations.ts` since they are static geographic data. The TURNER_BEND gauge gets a manually set coordinate (Mulberry River area: ~35.65, -93.93).

#### Marker Type

Use Leaflet `CircleMarker` (SVG-based) to avoid the well-known broken-icon issue with Leaflet's default PNG markers in Vite/webpack bundlers. CircleMarkers render as colored circles directly in SVG — no icon images to resolve.

```typescript
<CircleMarker
  center={[lat, lng]}
  radius={10}
  pathOptions={{ fillColor: statusColor, color: '#fff', weight: 2, fillOpacity: 0.8 }}
/>
```

#### Marker Color Priority

Color reflects the **highest-priority** status among all streams in that watershed. Priority reflects paddling interest — High (dangerous) outranks everything, then Optimal (runnable), then the rest:

| Priority    | Status  | Color                 | Reasoning                                  |
| ----------- | ------- | --------------------- | ------------------------------------------ |
| 1 (highest) | High    | `STATUS_HEX_COLORS.H` | Safety concern — paddlers need to see this |
| 2           | Optimal | `STATUS_HEX_COLORS.O` | Runnable — the main thing paddlers want    |
| 3           | Low     | `STATUS_HEX_COLORS.L` | Marginal — worth knowing                   |
| 4 (lowest)  | Too Low | `STATUS_HEX_COLORS.X` | Not runnable                               |

If gauge data hasn't loaded yet, use a neutral gray (`#9e9e9e`).

#### Popup on Click

Shows watershed name, current gauge reading, trend, and a list of all streams in the watershed with their individual statuses. Each stream name links to `/stream/:streamId`.

#### Grouping Logic

```typescript
// Group streams by gauge ID
const watersheds = Map<string, { gauge: StreamGauge; streams: StreamData[] }>;
streams.forEach((s) => {
  if (!watersheds.has(s.gauge.id)) {
    watersheds.set(s.gauge.id, { gauge: s.gauge, streams: [] });
  }
  watersheds.get(s.gauge.id).streams.push(s);
});
```

### Map Configuration

- **Center**: `[35.5, -93.5]` (central Ozarks)
- **Default zoom**: 8 (covers AR/OK region)
- **Base tiles**: CartoDB Positron (`https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png`) — clean, minimal style that lets precipitation colors stand out. Free, no API key.
- **Default overlay**: 24h accumulated precipitation

### Layer Control

MUI `ToggleButtonGroup` (exclusive selection) overlaid on the map via absolute positioning (bottom-left, with z-index above map tiles):

- Radar (live)
- 24h Precip
- 48h Precip
- 72h Precip

Only one precipitation layer active at a time to avoid visual clutter.

## Files

### New Files

| File                                              | Purpose                                                  |
| ------------------------------------------------- | -------------------------------------------------------- |
| `src/pages/PrecipitationMap.tsx`                  | Page component, layout, Leaflet CSS import               |
| `src/pages/PrecipitationMapLazy.tsx`              | Lazy-load wrapper (React.lazy + Suspense)                |
| `src/components/precipitation/MapView.tsx`        | Leaflet map with tile layers and watershed CircleMarkers |
| `src/components/precipitation/ForecastPanel.tsx`  | QPF forecast + observed precipitation sidebar/panel      |
| `src/components/precipitation/LayerControl.tsx`   | Tile layer toggle (MUI ToggleButtonGroup)                |
| `src/components/precipitation/WatershedPopup.tsx` | Marker popup content                                     |
| `src/data/gaugeLocations.ts`                      | Static lat/lng for each unique gauge ID                  |

### Modified Files

| File                             | Change                                                                                                                                                                                                                                         |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/App.tsx`                    | Add `/precipitation` route using `PrecipitationMapLazy`                                                                                                                                                                                        |
| `src/components/core/Header.tsx` | Add precipitation map nav button (Cloud icon) using `useNavigate` from react-router-dom. Placed before the refresh button. Uses `aria-label="precipitation map"`. Active state highlighted when on `/precipitation` route (via `useLocation`). |
| `vite.config.ts`                 | Add `'map-vendor': ['leaflet', 'react-leaflet']` to `manualChunks`                                                                                                                                                                             |

### Header Navigation Detail

The Header currently has no route navigation. The new precipitation button is an `IconButton` wrapping the MUI `Cloud` icon, using `useNavigate()` for routing:

```typescript
const navigate = useNavigate();
const location = useLocation();
const onPrecipMap = location.pathname === '/precipitation';

<IconButton
  onClick={() => navigate(onPrecipMap ? '/dashboard' : '/precipitation')}
  aria-label="precipitation map"
  sx={{
    color: onPrecipMap ? theme.palette.primary.light : 'white',
    // ... standard hover styles
  }}
>
  <Cloud />
</IconButton>
```

This toggles between the dashboard and precipitation map. The filter button remains visible on all pages (acceptable for prototype — it simply has no effect on the precipitation page).

## Styling

- All MUI sx prop, consistent with existing codebase
- Dark/light mode support via ThemeContext
- Map container height: use `flex: 1` within the existing flex layout from `App.tsx`, not hardcoded pixel math. On mobile, constrain to `60vh` with the forecast panel scrolling below.
- Forecast panel: 350px fixed width on desktop (>= md), full-width stacked section on mobile (< md)

## Edge Cases

- **Leaflet JS loading**: The lazy-load wrapper shows `CircularProgress` while the chunk loads, matching the existing `StreamPageLazy` pattern.
- **Tile loading failures**: IEM tiles may occasionally be slow or unreachable. Leaflet handles this gracefully with blank tiles. No special error UI needed.
- **QPF image failures**: If WPC images fail to load, the `<img>` `onError` handler shows "Forecast image unavailable — check wpc.ncep.noaa.gov" with a direct link.
- **NWS observed image failures**: Same pattern — fallback message with link to `water.weather.gov/precip/`.
- **Stale QPF images**: WPC images update every 6-12 hours. Browser cache is sufficient.
- **No gauge data**: If GaugeDataContext hasn't loaded yet, markers render with neutral gray and "Loading..." in popups.

## Out of Scope

- Custom watershed boundary polygons (would require GIS shapefiles)
- Precipitation amount calculations per watershed
- Historical precipitation queries
- Animated radar playback
- Hiding the filter button on the precipitation page (acceptable prototype tech debt)
