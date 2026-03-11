# Watershed Intelligence Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add observed rainfall totals and NWS river forecasts to the precipitation map popups, a weather summary bar, and a new watershed detail subpage.

**Architecture:** Two new services fetch data on-demand from NOAA QPE (rainfall inches) and NWS NWPS (river forecasts). A shared hook manages both. Data surfaces in enhanced popups, a summary bar, and a drill-down subpage with an inline SVG stage chart. All client-side, no new backend.

**Tech Stack:** React 18, MUI 5, Leaflet/react-leaflet, NOAA QPE MapServer, NWS NWPS API, Vitest, inline SVG.

**Spec:** `docs/specs/2026-03-11-watershed-intelligence-design.md`

---

## Chunk 1: Data Services

### Task 1: NWS Forecast Service (TDD)

**Files:**

- Create: `src/services/nwsForecastService.ts`
- Create: `tests/unit/nwsForecastService.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tests/unit/nwsForecastService.test.ts`:

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchNwsForecast } from '../../src/services/nwsForecastService';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
  };
})();
Object.defineProperty(global, 'localStorage', { value: localStorageMock });

const MOCK_STAGEFLOW = {
  primaryName: 'Stage',
  primaryUnits: 'ft',
  secondaryName: 'Flow',
  secondaryUnits: 'kcfs',
  data: [
    { validTime: '2026-03-10T12:00:00Z', primary: 3.5, secondary: 1.2 },
    { validTime: '2026-03-10T18:00:00Z', primary: 3.8, secondary: 1.4 },
    { validTime: '2026-03-11T00:00:00Z', primary: 4.2, secondary: 1.7 },
    { validTime: '2026-03-11T12:00:00Z', primary: 5.1, secondary: 2.3 },
    { validTime: '2026-03-12T00:00:00Z', primary: 4.8, secondary: 2.1 },
  ],
};

const MOCK_GAUGE_INFO = {
  flood: {
    categories: [
      { category: 'action', stage: 10 },
      { category: 'minor', stage: 18 },
      { category: 'moderate', stage: 20 },
      { category: 'major', stage: 22 },
    ],
  },
};

describe('fetchNwsForecast', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorageMock.clear();
  });

  it('parses stageflow response into forecast structure', async () => {
    global.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(MOCK_STAGEFLOW),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(MOCK_GAUGE_INFO),
      });

    const result = await fetchNwsForecast('07252000');
    expect(result).not.toBeNull();
    expect(result!.gaugeId).toBe('07252000');
    expect(result!.data.length).toBe(5);
    expect(result!.data[0].stage).toBe(3.5);
    expect(result!.peakForecast!.stage).toBe(5.1);
    expect(result!.floodCategories).not.toBeNull();
    expect(result!.floodCategories!.action).toBe(10);
  });

  it('returns null when stageflow returns 404', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({ ok: false, status: 404 });

    const result = await fetchNwsForecast('99999999');
    expect(result).toBeNull();
  });

  it('uses cached data within TTL', async () => {
    const cached = {
      data: {
        gaugeId: '07252000',
        data: [],
        peakForecast: null,
        floodCategories: null,
      },
      timestamp: Date.now(),
    };
    localStorageMock.setItem('nws-forecast-07252000', JSON.stringify(cached));

    global.fetch = vi.fn();
    const result = await fetchNwsForecast('07252000');
    expect(result).toEqual(cached.data);
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('refetches when cache is expired', async () => {
    const cached = {
      data: {
        gaugeId: '07252000',
        data: [],
        peakForecast: null,
        floodCategories: null,
      },
      timestamp: Date.now() - 2 * 60 * 60 * 1000, // 2 hours ago
    };
    localStorageMock.setItem('nws-forecast-07252000', JSON.stringify(cached));

    global.fetch = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(MOCK_STAGEFLOW),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(MOCK_GAUGE_INFO),
      });

    const result = await fetchNwsForecast('07252000');
    expect(global.fetch).toHaveBeenCalled();
    expect(result!.data.length).toBe(5);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx vitest run tests/unit/nwsForecastService.test.ts
```

Expected: FAIL — module not found.

- [ ] **Step 3: Write the implementation**

Create `src/services/nwsForecastService.ts`:

```typescript
const NWS_BASE = 'https://api.water.noaa.gov/nwps/v1/gauges';
const CACHE_TTL_MS = 60 * 60 * 1000; // 1 hour
const FETCH_TIMEOUT_MS = 5000;

export interface NwsForecastPoint {
  validTime: string;
  stage: number;
  flow: number;
}

export interface NwsFloodCategories {
  action: number;
  minor: number;
  moderate: number;
  major: number;
}

export interface NwsForecast {
  gaugeId: string;
  data: NwsForecastPoint[];
  peakForecast: { stage: number; time: string } | null;
  floodCategories: NwsFloodCategories | null;
}

interface CacheEntry {
  data: NwsForecast;
  timestamp: number;
}

function getCached(gaugeId: string): NwsForecast | null {
  try {
    const raw = localStorage.getItem(`nws-forecast-${gaugeId}`);
    if (!raw) return null;
    const entry: CacheEntry = JSON.parse(raw);
    if (Date.now() - entry.timestamp > CACHE_TTL_MS) return null;
    return entry.data;
  } catch {
    return null;
  }
}

function setCache(gaugeId: string, data: NwsForecast): void {
  try {
    const entry: CacheEntry = { data, timestamp: Date.now() };
    localStorage.setItem(`nws-forecast-${gaugeId}`, JSON.stringify(entry));
  } catch {
    // localStorage full — ignore
  }
}

export async function fetchNwsForecast(
  gaugeId: string
): Promise<NwsForecast | null> {
  const cached = getCached(gaugeId);
  if (cached) return cached;

  try {
    const stageRes = await fetch(`${NWS_BASE}/${gaugeId}/stageflow`, {
      signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
    });
    if (!stageRes.ok) return null;

    const stageData = await stageRes.json();
    const points: NwsForecastPoint[] = (stageData.data ?? []).map(
      (d: { validTime: string; primary: number; secondary: number }) => ({
        validTime: d.validTime,
        stage: d.primary,
        flow: d.secondary,
      })
    );

    // Find peak forecast
    let peakForecast: { stage: number; time: string } | null = null;
    for (const p of points) {
      if (!peakForecast || p.stage > peakForecast.stage) {
        peakForecast = { stage: p.stage, time: p.validTime };
      }
    }

    // Fetch flood categories
    let floodCategories: NwsFloodCategories | null = null;
    try {
      const gaugeRes = await fetch(`${NWS_BASE}/${gaugeId}`, {
        signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
      });
      if (gaugeRes.ok) {
        const gaugeInfo = await gaugeRes.json();
        const cats = gaugeInfo.flood?.categories;
        if (Array.isArray(cats) && cats.length > 0) {
          const catMap: Record<string, number> = {};
          for (const c of cats) {
            catMap[c.category] = c.stage;
          }
          if (catMap.action) {
            floodCategories = {
              action: catMap.action,
              minor: catMap.minor ?? 0,
              moderate: catMap.moderate ?? 0,
              major: catMap.major ?? 0,
            };
          }
        }
      }
    } catch {
      // Flood categories are optional — ignore errors
    }

    const forecast: NwsForecast = {
      gaugeId,
      data: points,
      peakForecast,
      floodCategories,
    };

    setCache(gaugeId, forecast);
    return forecast;
  } catch {
    return null;
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx vitest run tests/unit/nwsForecastService.test.ts
```

Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/services/nwsForecastService.ts tests/unit/nwsForecastService.test.ts
git commit -m "feat: add NWS forecast service with caching and TDD tests"
```

---

### Task 2: Precipitation Query Service (TDD)

**Files:**

- Create: `src/services/precipQueryService.ts`
- Create: `tests/unit/precipQueryService.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tests/unit/precipQueryService.test.ts`:

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchPrecipTotals } from '../../src/services/precipQueryService';

const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
  };
})();
Object.defineProperty(global, 'localStorage', { value: localStorageMock });

const MOCK_IDENTIFY_RESPONSE = {
  results: [
    { layerId: 17, layerName: 'Last 24 Hours', value: 'Pixel Value: 1.23' },
    { layerId: 23, layerName: 'Last 48 Hours', value: 'Pixel Value: 2.85' },
    { layerId: 29, layerName: 'Last 72 Hours', value: 'Pixel Value: 3.12' },
    { layerId: 35, layerName: 'Last 7 Days', value: 'Pixel Value: 4.50' },
  ],
};

describe('fetchPrecipTotals', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorageMock.clear();
  });

  it('parses identify response into precipitation totals', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(MOCK_IDENTIFY_RESPONSE),
    });

    const result = await fetchPrecipTotals('07252000', 35.5769, -94.0153);
    expect(result.gaugeId).toBe('07252000');
    expect(result.last24h).toBeCloseTo(1.23);
    expect(result.last48h).toBeCloseTo(2.85);
    expect(result.last72h).toBeCloseTo(3.12);
    expect(result.last7d).toBeCloseTo(4.5);
  });

  it('returns null values for missing layers', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ results: [] }),
    });

    const result = await fetchPrecipTotals('07252000', 35.5769, -94.0153);
    expect(result.last24h).toBeNull();
    expect(result.last48h).toBeNull();
  });

  it('handles NoData pixel values', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          results: [
            { layerId: 17, layerName: 'Last 24 Hours', value: 'NoData' },
          ],
        }),
    });

    const result = await fetchPrecipTotals('07252000', 35.5769, -94.0153);
    expect(result.last24h).toBeNull();
  });

  it('uses cached data within TTL', async () => {
    const cached = {
      data: {
        gaugeId: '07252000',
        lat: 35.5,
        lng: -94.0,
        last24h: 1.0,
        last48h: 2.0,
        last72h: null,
        last7d: null,
      },
      timestamp: Date.now(),
    };
    localStorageMock.setItem('precip-07252000', JSON.stringify(cached));

    global.fetch = vi.fn();
    const result = await fetchPrecipTotals('07252000', 35.5, -94.0);
    expect(result.last24h).toBe(1.0);
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('returns null values on fetch error', async () => {
    global.fetch = vi.fn().mockRejectedValueOnce(new Error('Network error'));

    const result = await fetchPrecipTotals('07252000', 35.5769, -94.0153);
    expect(result.last24h).toBeNull();
    expect(result.last48h).toBeNull();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx vitest run tests/unit/precipQueryService.test.ts
```

Expected: FAIL — module not found.

- [ ] **Step 3: Write the implementation**

Create `src/services/precipQueryService.ts`:

```typescript
const QPE_BASE =
  'https://mapservices.weather.noaa.gov/raster/rest/services/obs/rfc_qpe/MapServer/identify';
const CACHE_TTL_MS = 30 * 60 * 1000; // 30 minutes
const FETCH_TIMEOUT_MS = 5000;

// Layer IDs for precipitation periods
const LAYER_IDS = {
  last24h: 17,
  last48h: 23,
  last72h: 29,
  last7d: 35,
} as const;

export interface PrecipTotals {
  gaugeId: string;
  lat: number;
  lng: number;
  last24h: number | null;
  last48h: number | null;
  last72h: number | null;
  last7d: number | null;
}

interface CacheEntry {
  data: PrecipTotals;
  timestamp: number;
}

function getCached(gaugeId: string): PrecipTotals | null {
  try {
    const raw = localStorage.getItem(`precip-${gaugeId}`);
    if (!raw) return null;
    const entry: CacheEntry = JSON.parse(raw);
    if (Date.now() - entry.timestamp > CACHE_TTL_MS) return null;
    return entry.data;
  } catch {
    return null;
  }
}

function setCache(gaugeId: string, data: PrecipTotals): void {
  try {
    const entry: CacheEntry = { data, timestamp: Date.now() };
    localStorage.setItem(`precip-${gaugeId}`, JSON.stringify(entry));
  } catch {
    // localStorage full — ignore
  }
}

function parsePixelValue(value: string): number | null {
  if (!value || value === 'NoData' || value === 'Null') return null;
  const match = value.match(/Pixel Value:\s*([\d.]+)/);
  if (!match) return null;
  const num = parseFloat(match[1]);
  return isNaN(num) ? null : num;
}

export async function fetchPrecipTotals(
  gaugeId: string,
  lat: number,
  lng: number
): Promise<PrecipTotals> {
  const empty: PrecipTotals = {
    gaugeId,
    lat,
    lng,
    last24h: null,
    last48h: null,
    last72h: null,
    last7d: null,
  };

  const cached = getCached(gaugeId);
  if (cached) return cached;

  try {
    const layerList = Object.values(LAYER_IDS).join(',');
    const geometry = JSON.stringify({
      x: lng,
      y: lat,
      spatialReference: { wkid: 4326 },
    });
    const extent = `${lng - 0.5},${lat - 0.5},${lng + 0.5},${lat + 0.5}`;

    const params = new URLSearchParams({
      geometry,
      geometryType: 'esriGeometryPoint',
      layers: `visible:${layerList}`,
      mapExtent: extent,
      imageDisplay: '600,550,96',
      returnGeometry: 'false',
      f: 'json',
    });

    const res = await fetch(`${QPE_BASE}?${params}`, {
      signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
    });

    if (!res.ok) return empty;

    const data = await res.json();
    const results: Array<{ layerId: number; value: string }> =
      data.results ?? [];

    const byLayer = new Map<number, string>();
    for (const r of results) {
      byLayer.set(r.layerId, r.value);
    }

    const totals: PrecipTotals = {
      gaugeId,
      lat,
      lng,
      last24h: parsePixelValue(byLayer.get(LAYER_IDS.last24h) ?? ''),
      last48h: parsePixelValue(byLayer.get(LAYER_IDS.last48h) ?? ''),
      last72h: parsePixelValue(byLayer.get(LAYER_IDS.last72h) ?? ''),
      last7d: parsePixelValue(byLayer.get(LAYER_IDS.last7d) ?? ''),
    };

    setCache(gaugeId, totals);
    return totals;
  } catch {
    return empty;
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx vitest run tests/unit/precipQueryService.test.ts
```

Expected: All 5 tests PASS.

- [ ] **Step 5: Run all tests to ensure nothing broke**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx vitest run
```

Expected: All tests pass (existing 56 + 9 new = 65).

- [ ] **Step 6: Commit**

```bash
git add src/services/precipQueryService.ts tests/unit/precipQueryService.test.ts
git commit -m "feat: add precipitation query service with NOAA QPE point queries"
```

---

## Chunk 2: Hook and Popup Enhancement

### Task 3: useWatershedIntelligence hook

**Files:**

- Create: `src/hooks/useWatershedIntelligence.ts`

- [ ] **Step 1: Create the hook**

Create `src/hooks/useWatershedIntelligence.ts`:

```typescript
import { useState, useEffect } from 'react';
import { fetchNwsForecast, NwsForecast } from '../services/nwsForecastService';
import {
  fetchPrecipTotals,
  PrecipTotals,
} from '../services/precipQueryService';

export interface WatershedIntelligence {
  forecast: NwsForecast | null;
  precip: PrecipTotals | null;
  loading: boolean;
}

export function useWatershedIntelligence(
  gaugeId: string | null,
  lat: number | null,
  lng: number | null
): WatershedIntelligence {
  const [forecast, setForecast] = useState<NwsForecast | null>(null);
  const [precip, setPrecip] = useState<PrecipTotals | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!gaugeId || lat === null || lng === null) return;

    let cancelled = false;
    setLoading(true);

    Promise.all([
      fetchNwsForecast(gaugeId),
      fetchPrecipTotals(gaugeId, lat, lng),
    ]).then(([forecastResult, precipResult]) => {
      if (cancelled) return;
      setForecast(forecastResult);
      setPrecip(precipResult);
      setLoading(false);
    });

    return () => {
      cancelled = true;
    };
  }, [gaugeId, lat, lng]);

  return { forecast, precip, loading };
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx tsc --noEmit
```

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add src/hooks/useWatershedIntelligence.ts
git commit -m "feat: add useWatershedIntelligence hook for combined forecast + precip data"
```

---

### Task 4: Enhance WatershedPopup with rainfall + forecast

**Files:**

- Modify: `src/components/precipitation/WatershedPopup.tsx`

This task adds two new compact rows to the popup: observed rainfall and NWS forecast. Also adds a "View Forecast →" link to the watershed detail subpage.

- [ ] **Step 1: Read the current WatershedPopup.tsx**

Read `src/components/precipitation/WatershedPopup.tsx` to understand current structure.

- [ ] **Step 2: Add intelligence props and rainfall/forecast rows**

Add these changes to WatershedPopup.tsx:

**New imports at top:**

```typescript
import { Skeleton } from '@mui/material';
import { WaterDrop, TrendingUp } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { alpha } from '@mui/material/styles';
import { NwsForecast } from '../../services/nwsForecastService';
import { PrecipTotals } from '../../services/precipQueryService';
import { format } from 'date-fns';
```

**Add optional props to the interface:**

```typescript
interface WatershedPopupProps {
  watershed: Watershed;
  reading: GaugeReading | null;
  previousReading: GaugeReading | null;
  forecast?: NwsForecast | null;
  precip?: PrecipTotals | null;
  intelligenceLoading?: boolean;
}
```

**Between the reading/trend section and the stream list, add:**

```tsx
{
  /* Rainfall row */
}
{
  precip && (precip.last24h !== null || precip.last48h !== null) && (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 0.5,
        mb: 0.5,
        py: 0.5,
        px: 0.75,
        borderRadius: 1,
        background: 'rgba(48, 207, 208, 0.06)',
      }}
    >
      <WaterDrop sx={{ fontSize: 14, color: '#30cfd0' }} />
      <Typography
        variant="caption"
        sx={{ fontWeight: 600, fontSize: '0.7rem' }}
      >
        {precip.last24h !== null && `${precip.last24h.toFixed(1)} in (24h)`}
        {precip.last24h !== null && precip.last48h !== null && ' · '}
        {precip.last48h !== null && `${precip.last48h.toFixed(1)} in (48h)`}
      </Typography>
    </Box>
  );
}
{
  intelligenceLoading && !precip && (
    <Skeleton
      variant="rectangular"
      height={24}
      sx={{ borderRadius: 1, mb: 0.5 }}
    />
  );
}

{
  /* Forecast row */
}
{
  forecast?.peakForecast && (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 0.5,
        mb: 0.75,
        py: 0.5,
        px: 0.75,
        borderRadius: 1,
        background: alpha('#4caf50', 0.06),
      }}
    >
      <TrendingUp sx={{ fontSize: 14, color: '#4caf50' }} />
      <Typography
        variant="caption"
        sx={{ fontWeight: 600, fontSize: '0.7rem' }}
      >
        → {forecast.peakForecast.stage.toFixed(1)} ft by{' '}
        {format(new Date(forecast.peakForecast.time), 'EEE')}
      </Typography>
    </Box>
  );
}
```

**After the stream list, add a "View Forecast" link:**

```tsx
<Box
  onClick={() => navigate(`/precipitation/watershed/${watershed.gauge.id}`)}
  sx={{
    mt: 1,
    pt: 0.75,
    borderTop: '1px solid',
    borderColor: 'divider',
    cursor: 'pointer',
    textAlign: 'center',
    '&:hover': { color: '#30cfd0' },
    transition: 'color 0.2s',
  }}
>
  <Typography
    variant="caption"
    sx={{ fontWeight: 600, fontSize: '0.7rem', letterSpacing: '0.03em' }}
  >
    View Watershed Forecast →
  </Typography>
</Box>
```

- [ ] **Step 3: Update MapView to pass intelligence data to popup**

Read and modify `src/components/precipitation/MapView.tsx`:

Add imports:

```typescript
import { useWatershedIntelligence } from '../../hooks/useWatershedIntelligence';
import { GAUGE_LOCATIONS } from '../../data/gaugeLocations';
```

The challenge: `useWatershedIntelligence` is a hook and can't be called inside a `.map()`. Create a small wrapper component for each marker:

Create a `WatershedMarker` component inside MapView.tsx (or as a separate file):

```typescript
function WatershedMarker({
  marker,
  gaugeData,
}: {
  marker: { gaugeId: string; lat: number; lng: number; color: string; watershed: Watershed };
  gaugeData: { reading: GaugeReading | null; previousReading: GaugeReading | null } | undefined;
}) {
  const { forecast, precip, loading } = useWatershedIntelligence(
    marker.gaugeId,
    marker.lat,
    marker.lng
  );

  return (
    <CircleMarker
      center={[marker.lat, marker.lng]}
      radius={12}
      pathOptions={{
        fillColor: marker.color,
        color: '#fff',
        weight: 2.5,
        fillOpacity: 0.9,
      }}
    >
      <Popup>
        <WatershedPopup
          watershed={marker.watershed}
          reading={gaugeData?.reading ?? null}
          previousReading={gaugeData?.previousReading ?? null}
          forecast={forecast}
          precip={precip}
          intelligenceLoading={loading}
        />
      </Popup>
    </CircleMarker>
  );
}
```

Replace the markers `.map()` to use `WatershedMarker` instead of inline `CircleMarker`.

- [ ] **Step 4: Verify TypeScript compiles**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx tsc --noEmit
```

- [ ] **Step 5: Run all tests**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx vitest run
```

- [ ] **Step 6: Commit**

```bash
git add src/components/precipitation/WatershedPopup.tsx src/components/precipitation/MapView.tsx
git commit -m "feat: add rainfall and forecast data to watershed popup"
```

---

## Chunk 3: Summary Bar and Precipitation Page Update

### Task 5: WeatherSummaryBar component

**Files:**

- Create: `src/components/precipitation/WeatherSummaryBar.tsx`

- [ ] **Step 1: Create the summary bar component**

Create `src/components/precipitation/WeatherSummaryBar.tsx`:

```typescript
import { Box, Typography, Skeleton, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { WaterDrop, TrendingUp } from '@mui/icons-material';
import { glassmorphism } from '../../theme/waterTheme';
import { PrecipTotals } from '../../services/precipQueryService';
import { NwsForecast } from '../../services/nwsForecastService';

interface WeatherSummaryBarProps {
  precipData: Map<string, PrecipTotals>;
  forecastData: Map<string, NwsForecast>;
  loading: boolean;
}

export function WeatherSummaryBar({
  precipData,
  forecastData,
  loading,
}: WeatherSummaryBarProps) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const glass = isDark ? glassmorphism.dark : glassmorphism.light;

  const rainyCount = Array.from(precipData.values()).filter(
    (p) => p.last24h !== null && p.last24h > 0.1
  ).length;

  const risingCount = Array.from(forecastData.values()).filter((f) => {
    if (!f.data || f.data.length < 2) return false;
    const last = f.data[f.data.length - 1];
    const first = f.data[0];
    return last.stage > first.stage + 0.1;
  }).length;

  if (loading && precipData.size === 0) {
    return (
      <Box sx={{ px: 2, py: 1, ...glass, borderRadius: 0 }}>
        <Skeleton width={300} height={20} />
      </Box>
    );
  }

  if (rainyCount === 0 && risingCount === 0) return null;

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 3,
        px: 2,
        py: 1,
        ...glass,
        borderRadius: 0,
        borderBottom: `1px solid ${alpha(isDark ? '#30cfd0' : '#000', 0.1)}`,
      }}
    >
      {rainyCount > 0 && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
          <WaterDrop sx={{ fontSize: 16, color: '#30cfd0' }} />
          <Typography variant="caption" sx={{ fontWeight: 600, fontSize: '0.75rem' }}>
            {rainyCount} watershed{rainyCount !== 1 ? 's' : ''} got rain (24h)
          </Typography>
        </Box>
      )}
      {risingCount > 0 && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
          <TrendingUp sx={{ fontSize: 16, color: '#4caf50' }} />
          <Typography variant="caption" sx={{ fontWeight: 600, fontSize: '0.75rem' }}>
            {risingCount} gauge{risingCount !== 1 ? 's' : ''} forecast rising
          </Typography>
        </Box>
      )}
    </Box>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
git add src/components/precipitation/WeatherSummaryBar.tsx
git commit -m "feat: add WeatherSummaryBar with rain and forecast counts"
```

---

### Task 6: Integrate summary bar into PrecipitationMap page

**Files:**

- Modify: `src/pages/PrecipitationMap.tsx`

- [ ] **Step 1: Read current PrecipitationMap.tsx**

Read `src/pages/PrecipitationMap.tsx` for current structure.

- [ ] **Step 2: Add batched intelligence fetching and summary bar**

Add imports and state for intelligence data. Fetch precip + forecast for all watersheds on mount, staggered to avoid hammering APIs. Pass results to WeatherSummaryBar.

Key additions:

- `useState` maps for `precipData` and `forecastData`
- `useEffect` that iterates through watersheds, fetching with 100ms stagger
- `WeatherSummaryBar` rendered above the map

Add to the page layout (both mobile and desktop), between the outer `Box` wrapper and the `MapView`:

```tsx
<WeatherSummaryBar
  precipData={precipData}
  forecastData={forecastData}
  loading={intelligenceLoading}
/>
```

The staggered fetch effect:

```typescript
useEffect(() => {
  let cancelled = false;
  setIntelligenceLoading(true);
  const entries = Array.from(watersheds.entries());

  (async () => {
    for (const [gaugeId, watershed] of entries) {
      if (cancelled) break;
      const loc = GAUGE_LOCATIONS[gaugeId];
      if (!loc) continue;

      const [forecast, precip] = await Promise.all([
        fetchNwsForecast(gaugeId),
        fetchPrecipTotals(gaugeId, loc.lat, loc.lng),
      ]);

      if (cancelled) break;
      if (forecast)
        setForecastData((prev) => new Map(prev).set(gaugeId, forecast));
      if (precip) setPrecipData((prev) => new Map(prev).set(gaugeId, precip));

      // Stagger requests
      await new Promise((r) => setTimeout(r, 100));
    }
    if (!cancelled) setIntelligenceLoading(false);
  })();

  return () => {
    cancelled = true;
  };
}, [watersheds]);
```

- [ ] **Step 3: Verify TypeScript compiles and all tests pass**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx tsc --noEmit && npx vitest run
```

- [ ] **Step 4: Run lint and format**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm run format && npm run lint
```

- [ ] **Step 5: Commit**

```bash
git add src/pages/PrecipitationMap.tsx
git commit -m "feat: integrate batched intelligence fetching and summary bar into precipitation page"
```

---

## Chunk 4: Watershed Detail Subpage

### Task 7: StageChart SVG component

**Files:**

- Create: `src/components/precipitation/StageChart.tsx`

- [ ] **Step 1: Create the inline SVG chart component**

Create `src/components/precipitation/StageChart.tsx`:

A pure SVG line chart component. No chart library. Takes observed + forecast data points and renders:

- Solid line for all data
- Dashed portion for forecast (points after current time)
- Y-axis labels (stage in ft)
- X-axis labels (day names)
- Optional horizontal dashed lines for flood categories
- Responsive width via viewBox

```typescript
import { Box, Typography, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { format } from 'date-fns';
import { NwsForecastPoint, NwsFloodCategories } from '../../services/nwsForecastService';

interface StageChartProps {
  data: NwsForecastPoint[];
  floodCategories?: NwsFloodCategories | null;
  currentStage?: number;
}

const CHART_W = 600;
const CHART_H = 200;
const PAD = { top: 20, right: 20, bottom: 30, left: 45 };

export function StageChart({ data, floodCategories, currentStage }: StageChartProps) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  if (data.length < 2) return null;

  const stages = data.map((d) => d.stage);
  const times = data.map((d) => new Date(d.validTime).getTime());

  let minStage = Math.min(...stages);
  let maxStage = Math.max(...stages);

  // Include flood action stage if it's close
  if (floodCategories && floodCategories.action <= maxStage * 1.5) {
    maxStage = Math.max(maxStage, floodCategories.action);
  }

  // Add padding to range
  const range = maxStage - minStage || 1;
  minStage = Math.max(0, minStage - range * 0.1);
  maxStage = maxStage + range * 0.1;

  const minTime = Math.min(...times);
  const maxTime = Math.max(...times);

  const x = (t: number) => PAD.left + ((t - minTime) / (maxTime - minTime)) * (CHART_W - PAD.left - PAD.right);
  const y = (s: number) => PAD.top + (1 - (s - minStage) / (maxStage - minStage)) * (CHART_H - PAD.top - PAD.bottom);

  const now = Date.now();
  const pathPoints = data.map((d) => `${x(new Date(d.validTime).getTime())},${y(d.stage)}`);
  const observedIdx = data.findIndex((d) => new Date(d.validTime).getTime() > now);
  const splitIdx = observedIdx === -1 ? data.length : observedIdx;

  const observedPath = pathPoints.slice(0, splitIdx + 1).join(' L');
  const forecastPath = pathPoints.slice(Math.max(0, splitIdx - 1)).join(' L');

  // X-axis day labels
  const dayLabels: Array<{ time: number; label: string }> = [];
  const startDay = new Date(minTime);
  startDay.setHours(0, 0, 0, 0);
  for (let d = new Date(startDay); d.getTime() <= maxTime; d.setDate(d.getDate() + 1)) {
    if (d.getTime() >= minTime) {
      dayLabels.push({ time: d.getTime(), label: format(d, 'EEE') });
    }
  }

  // Y-axis labels
  const ySteps = 4;
  const yLabels = Array.from({ length: ySteps + 1 }, (_, i) => minStage + (range * 1.2 * i) / ySteps);

  const textColor = isDark ? alpha('#fff', 0.6) : alpha('#000', 0.5);
  const gridColor = isDark ? alpha('#fff', 0.08) : alpha('#000', 0.08);

  return (
    <Box sx={{ width: '100%' }}>
      <svg viewBox={`0 0 ${CHART_W} ${CHART_H}`} style={{ width: '100%', height: 'auto' }}>
        {/* Grid lines */}
        {yLabels.map((s, i) => (
          <line key={i} x1={PAD.left} x2={CHART_W - PAD.right} y1={y(s)} y2={y(s)} stroke={gridColor} strokeWidth={1} />
        ))}

        {/* Flood category line */}
        {floodCategories && floodCategories.action <= maxStage && (
          <line
            x1={PAD.left}
            x2={CHART_W - PAD.right}
            y1={y(floodCategories.action)}
            y2={y(floodCategories.action)}
            stroke="#f44336"
            strokeWidth={1}
            strokeDasharray="6,4"
            opacity={0.6}
          />
        )}

        {/* Observed line */}
        {splitIdx > 0 && (
          <path
            d={`M${observedPath}`}
            fill="none"
            stroke="#30cfd0"
            strokeWidth={2.5}
            strokeLinecap="round"
          />
        )}

        {/* Forecast line */}
        {splitIdx < data.length && (
          <path
            d={`M${forecastPath}`}
            fill="none"
            stroke="#30cfd0"
            strokeWidth={2}
            strokeDasharray="8,4"
            opacity={0.7}
            strokeLinecap="round"
          />
        )}

        {/* Current stage dot */}
        {currentStage !== undefined && (
          <circle
            cx={x(now > maxTime ? maxTime : now < minTime ? minTime : now)}
            cy={y(currentStage)}
            r={4}
            fill="#30cfd0"
            stroke="#fff"
            strokeWidth={2}
          />
        )}

        {/* Y-axis labels */}
        {yLabels.map((s, i) => (
          <text key={i} x={PAD.left - 8} y={y(s) + 4} textAnchor="end" fontSize={10} fill={textColor}>
            {s.toFixed(1)}
          </text>
        ))}

        {/* X-axis day labels */}
        {dayLabels.map((d, i) => (
          <text key={i} x={x(d.time)} y={CHART_H - 5} textAnchor="middle" fontSize={10} fill={textColor}>
            {d.label}
          </text>
        ))}
      </svg>
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 0.5 }}>
        <Typography variant="caption" sx={{ color: 'text.secondary', display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Box component="span" sx={{ width: 16, height: 2, bgcolor: '#30cfd0', display: 'inline-block' }} /> Observed
        </Typography>
        <Typography variant="caption" sx={{ color: 'text.secondary', display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Box component="span" sx={{ width: 16, height: 2, bgcolor: '#30cfd0', opacity: 0.7, display: 'inline-block', borderTop: '2px dashed #30cfd0', background: 'none' }} /> Forecast
        </Typography>
      </Box>
    </Box>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
git add src/components/precipitation/StageChart.tsx
git commit -m "feat: add inline SVG stage forecast chart component"
```

---

### Task 8: WatershedDetailPage + lazy wrapper

**Files:**

- Create: `src/pages/WatershedDetailPage.tsx`
- Create: `src/pages/WatershedDetailLazy.tsx`

- [ ] **Step 1: Create the watershed detail page**

Create `src/pages/WatershedDetailPage.tsx`:

A full page showing current conditions, stage forecast chart, rainfall totals, stream list, and flood stages. Uses `useParams` to get gaugeId, looks up gauge location, and uses `useWatershedIntelligence` for data.

Key sections:

- Back button → `/precipitation`
- Gauge name header
- Three stat cards (GlassCard): stage, trend, status
- StageChart (only when forecast data exists)
- Four rainfall cards (24h, 48h, 72h, 7d)
- Stream list with status chips and links
- Flood stages bar (only when NWS data exists)

Uses: `useParams`, `useNavigate`, `useGaugeDataContext`, `useWatershedIntelligence`, `GlassCard`, `StageChart`, `GAUGE_LOCATIONS`, `streams` from streamData, `groupStreamsByWatershed`.

- [ ] **Step 2: Create the lazy wrapper**

Create `src/pages/WatershedDetailLazy.tsx` following the same pattern as `PrecipitationMapLazy.tsx`:

```typescript
import { lazy, Suspense } from 'react';
import { Box, CircularProgress } from '@mui/material';

const WatershedDetailPage = lazy(() => import('./WatershedDetailPage'));

function LoadingFallback() {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flex: 1 }}>
      <CircularProgress />
    </Box>
  );
}

export function WatershedDetailLazy() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <WatershedDetailPage />
    </Suspense>
  );
}
```

- [ ] **Step 3: Verify TypeScript compiles**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx tsc --noEmit
```

- [ ] **Step 4: Commit**

```bash
git add src/pages/WatershedDetailPage.tsx src/pages/WatershedDetailLazy.tsx
git commit -m "feat: add WatershedDetailPage with forecast chart, rainfall, and stream list"
```

---

### Task 9: Add route and verify end-to-end

**Files:**

- Modify: `src/App.tsx`

- [ ] **Step 1: Add the watershed detail route**

In `src/App.tsx`, add import:

```typescript
import { WatershedDetailLazy } from './pages/WatershedDetailLazy';
```

Add route after the `/precipitation` route:

```typescript
<Route path="/precipitation/watershed/:gaugeId" element={<WatershedDetailLazy />} />
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx tsc --noEmit
```

- [ ] **Step 3: Run all tests**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx vitest run
```

Expected: All tests pass.

- [ ] **Step 4: Run lint and format**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm run format && npm run lint
```

- [ ] **Step 5: Verify production build**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm run build
```

Expected: Build succeeds with proper chunking.

- [ ] **Step 6: Commit**

```bash
git add src/App.tsx
git commit -m "feat: add /precipitation/watershed/:gaugeId route for watershed detail"
```

---

## Summary

| Task | What                                    | Files                                                                         |
| ---- | --------------------------------------- | ----------------------------------------------------------------------------- |
| 1    | NWS Forecast Service (TDD)              | `src/services/nwsForecastService.ts`, `tests/unit/nwsForecastService.test.ts` |
| 2    | Precip Query Service (TDD)              | `src/services/precipQueryService.ts`, `tests/unit/precipQueryService.test.ts` |
| 3    | useWatershedIntelligence hook           | `src/hooks/useWatershedIntelligence.ts`                                       |
| 4    | Enhanced popup with rainfall + forecast | `src/components/precipitation/WatershedPopup.tsx`, `MapView.tsx`              |
| 5    | WeatherSummaryBar component             | `src/components/precipitation/WeatherSummaryBar.tsx`                          |
| 6    | Precipitation page integration          | `src/pages/PrecipitationMap.tsx`                                              |
| 7    | StageChart SVG component                | `src/components/precipitation/StageChart.tsx`                                 |
| 8    | WatershedDetailPage + lazy wrapper      | `src/pages/WatershedDetailPage.tsx`, `WatershedDetailLazy.tsx`                |
| 9    | Route + end-to-end verification         | `src/App.tsx`                                                                 |
