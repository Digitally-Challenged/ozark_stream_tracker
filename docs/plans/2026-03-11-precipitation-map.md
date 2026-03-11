# Precipitation Map Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an interactive precipitation map page with IEM MRMS radar/precipitation tile overlays, watershed gauge markers, and NOAA forecast imagery.

**Architecture:** New `/precipitation` route lazy-loaded via React.lazy. Leaflet map with IEM tile layers and CircleMarker watershed markers colored by gauge status. Sidebar panel shows WPC QPF forecast and NWS observed precipitation images. Streams grouped by shared gauge ID (~35 watersheds).

**Tech Stack:** React 18, MUI 5, Leaflet + react-leaflet, IEM MRMS tiles, WPC QPF images, NWS AHPS images.

**Spec:** `docs/specs/2026-03-11-precipitation-map-design.md`

---

## Chunk 1: Dependencies, Data, and Build Config

### Task 1: Install dependencies

**Files:**

- Modify: `package.json`
- Modify: `vite.config.ts`

- [ ] **Step 1: Install leaflet, react-leaflet, and types**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm install leaflet react-leaflet && npm install -D @types/leaflet
```

- [ ] **Step 2: Add map-vendor chunk to vite config**

In `vite.config.ts`, add to the `manualChunks` object:

```typescript
'map-vendor': ['leaflet', 'react-leaflet'],
```

So the full `manualChunks` becomes:

```typescript
manualChunks: {
  'react-vendor': ['react', 'react-dom', 'react-router-dom'],
  'mui-vendor': [
    '@mui/material',
    '@mui/icons-material',
    '@emotion/react',
    '@emotion/styled',
  ],
  'date-vendor': ['date-fns'],
  'map-vendor': ['leaflet', 'react-leaflet'],
},
```

- [ ] **Step 3: Verify build still works**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm run build
```

Expected: Build succeeds. A `map-vendor-*.js` chunk appears in `dist/assets/`.

- [ ] **Step 4: Commit**

```bash
git add package.json package-lock.json vite.config.ts
git commit -m "chore: add leaflet and react-leaflet dependencies with map-vendor chunk"
```

---

### Task 2: Create gauge locations data

**Files:**

- Create: `src/data/gaugeLocations.ts`

- [ ] **Step 1: Create the gauge locations file**

Create `src/data/gaugeLocations.ts` with all 36 gauge coordinates (35 USGS + Turner Bend):

```typescript
export const GAUGE_LOCATIONS: Record<
  string,
  { name: string; lat: number; lng: number }
> = {
  '07034000': {
    name: 'St. Francis River near Roselle, MO',
    lat: 37.5961,
    lng: -90.4986,
  },
  '07048550': {
    name: 'West Fork White River east of Fayetteville, AR',
    lat: 36.0539,
    lng: -94.0831,
  },
  '07048600': {
    name: 'White River near Fayetteville, AR',
    lat: 36.0731,
    lng: -94.0811,
  },
  '07050500': {
    name: 'Kings River near Berryville, AR',
    lat: 36.4272,
    lng: -93.6208,
  },
  '07055646': {
    name: 'Buffalo River near Boxley, AR',
    lat: 35.9389,
    lng: -93.405,
  },
  '07055660': {
    name: 'Buffalo River at Ponca, AR',
    lat: 36.0225,
    lng: -93.3547,
  },
  '07055875': {
    name: 'Richland Creek near Witts Spring, AR',
    lat: 35.7972,
    lng: -92.9289,
  },
  '07069305': {
    name: 'Spring River at Hardy, AR',
    lat: 36.3136,
    lng: -91.4827,
  },
  '07074000': {
    name: 'Strawberry River near Poughkeepsie, AR',
    lat: 36.1111,
    lng: -91.4494,
  },
  '07075000': {
    name: 'Middle Fork of Little Red River at Shirley, AR',
    lat: 35.6567,
    lng: -92.2928,
  },
  '07075300': {
    name: 'South Fork of Little Red River at Clinton, AR',
    lat: 35.5869,
    lng: -92.4513,
  },
  '07164500': {
    name: 'Arkansas River at Tulsa, OK',
    lat: 36.1406,
    lng: -96.0064,
  },
  '07188838': {
    name: 'Little Sugar Creek near Pineville, MO',
    lat: 36.5841,
    lng: -94.373,
  },
  '07191179': {
    name: 'Spavinaw Creek near Cherokee City, AR',
    lat: 36.342,
    lng: -94.5877,
  },
  '07195430': {
    name: 'Illinois River South of Siloam Springs, AR',
    lat: 36.1086,
    lng: -94.5333,
  },
  '07196900': {
    name: 'Baron Fork at Dutch Mills, AR',
    lat: 35.88,
    lng: -94.4864,
  },
  '07249413': {
    name: 'Poteau River near Panama, OK',
    lat: 35.1657,
    lng: -94.653,
  },
  '07249800': { name: 'Lee Creek at Short, OK', lat: 35.5658, lng: -94.5319 },
  '07250965': {
    name: 'Frog Bayou at Winfrey, AR',
    lat: 35.7222,
    lng: -94.1136,
  },
  '07250974': {
    name: 'Jack Creek near Winfrey, AR',
    lat: 35.7044,
    lng: -94.0917,
  },
  '07251500': {
    name: 'Frog Bayou at Rudy, AR',
    lat: 35.5258,
    lng: -94.2713,
  },
  '07252000': {
    name: 'Mulberry River near Mulberry, AR',
    lat: 35.5769,
    lng: -94.0153,
  },
  '07256500': {
    name: 'Spadra Creek at Clarksville, AR',
    lat: 35.4683,
    lng: -93.4631,
  },
  '07257006': {
    name: 'Big Piney Creek at Highway 164 near Dover, AR',
    lat: 35.5058,
    lng: -93.1813,
  },
  '07257500': {
    name: 'Illinois Bayou near Scottsville, AR',
    lat: 35.4664,
    lng: -93.0411,
  },
  '07260000': {
    name: 'Dutch Creek at Waltreak, AR',
    lat: 34.9869,
    lng: -93.6131,
  },
  '07261000': {
    name: 'Cadron Creek near Guy, AR',
    lat: 35.2986,
    lng: -92.4038,
  },
  '07263000': {
    name: 'South Fourche LaFave River near Hollis, AR',
    lat: 34.9119,
    lng: -93.0561,
  },
  '07335840': {
    name: 'Pine Creek at Eubanks, OK',
    lat: 34.4053,
    lng: -95.5933,
  },
  '07340300': {
    name: 'Cossatot River near Vandervoort, AR',
    lat: 34.38,
    lng: -94.2364,
  },
  '07341000': {
    name: 'Saline River near Dierks, AR',
    lat: 34.0961,
    lng: -94.085,
  },
  '07356000': {
    name: 'Ouachita River near Mount Ida, AR',
    lat: 34.61,
    lng: -93.6975,
  },
  '07359002': {
    name: 'Ouachita River at Remmel Dam, AR',
    lat: 34.4261,
    lng: -92.8909,
  },
  '07359610': {
    name: 'Caddo River near Caddo Gap, AR',
    lat: 34.3828,
    lng: -93.6062,
  },
  '07360200': {
    name: 'Little Missouri River near Langley, AR',
    lat: 34.3117,
    lng: -93.8998,
  },
  TURNER_BEND: {
    name: 'Turner Bend Landing',
    lat: 35.6539,
    lng: -93.9272,
  },
};
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx tsc --noEmit
```

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add src/data/gaugeLocations.ts
git commit -m "feat: add gauge location coordinates for precipitation map"
```

---

## Chunk 2: Watershed Grouping Utility

### Task 3: Create watershed grouping utility with tests

**Files:**

- Create: `src/utils/watershedGrouping.ts`
- Create: `tests/unit/watershedGrouping.test.ts`

- [ ] **Step 1: Write the failing test**

Create `tests/unit/watershedGrouping.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';
import { LevelStatus } from '../../src/types/stream';
import {
  groupStreamsByWatershed,
  getWatershedMarkerColor,
} from '../../src/utils/watershedGrouping';

describe('groupStreamsByWatershed', () => {
  it('groups streams sharing the same gauge ID', () => {
    const streams = [
      {
        name: 'Stream A',
        rating: 'III',
        size: 'S' as const,
        gauge: { name: 'Gauge 1', id: '001', url: '' },
        quality: 'A' as const,
        targetLevels: { tooLow: 1, optimal: 2, high: 3 },
      },
      {
        name: 'Stream B',
        rating: 'II',
        size: 'M' as const,
        gauge: { name: 'Gauge 1', id: '001', url: '' },
        quality: 'B' as const,
        targetLevels: { tooLow: 2, optimal: 3, high: 4 },
      },
      {
        name: 'Stream C',
        rating: 'IV',
        size: 'L' as const,
        gauge: { name: 'Gauge 2', id: '002', url: '' },
        quality: 'A' as const,
        targetLevels: { tooLow: 1, optimal: 2, high: 3 },
      },
    ];

    const result = groupStreamsByWatershed(streams);
    expect(result.size).toBe(2);
    expect(result.get('001')!.streams).toHaveLength(2);
    expect(result.get('002')!.streams).toHaveLength(1);
    expect(result.get('001')!.gauge.name).toBe('Gauge 1');
  });
});

describe('getWatershedMarkerColor', () => {
  it('returns High color when any stream is High', () => {
    const statuses = [LevelStatus.Optimal, LevelStatus.High, LevelStatus.Low];
    expect(getWatershedMarkerColor(statuses)).toBe('#0288d1');
  });

  it('returns Optimal color when best is Optimal (no High)', () => {
    const statuses = [LevelStatus.Optimal, LevelStatus.Low, LevelStatus.TooLow];
    expect(getWatershedMarkerColor(statuses)).toBe('#2e7d32');
  });

  it('returns Low color when best is Low', () => {
    const statuses = [LevelStatus.Low, LevelStatus.TooLow];
    expect(getWatershedMarkerColor(statuses)).toBe('#ed6c02');
  });

  it('returns TooLow color when all Too Low', () => {
    const statuses = [LevelStatus.TooLow, LevelStatus.TooLow];
    expect(getWatershedMarkerColor(statuses)).toBe('#d32f2f');
  });

  it('returns neutral gray for empty array', () => {
    expect(getWatershedMarkerColor([])).toBe('#9e9e9e');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx vitest run tests/unit/watershedGrouping.test.ts
```

Expected: FAIL — module not found.

- [ ] **Step 3: Write the implementation**

Create `src/utils/watershedGrouping.ts`:

```typescript
import { StreamData, StreamGauge, LevelStatus } from '../types/stream';
import { STATUS_HEX_COLORS } from './streamLevels';

export interface Watershed {
  gauge: StreamGauge;
  streams: StreamData[];
}

const NEUTRAL_GRAY = '#9e9e9e';

// Priority: High (safety) > Optimal (runnable) > Low > TooLow
const STATUS_PRIORITY: Record<LevelStatus, number> = {
  [LevelStatus.High]: 4,
  [LevelStatus.Optimal]: 3,
  [LevelStatus.Low]: 2,
  [LevelStatus.TooLow]: 1,
};

export function groupStreamsByWatershed(
  streams: StreamData[]
): Map<string, Watershed> {
  const watersheds = new Map<string, Watershed>();
  for (const stream of streams) {
    const existing = watersheds.get(stream.gauge.id);
    if (existing) {
      existing.streams.push(stream);
    } else {
      watersheds.set(stream.gauge.id, {
        gauge: stream.gauge,
        streams: [stream],
      });
    }
  }
  return watersheds;
}

export function getWatershedMarkerColor(statuses: LevelStatus[]): string {
  if (statuses.length === 0) return NEUTRAL_GRAY;

  let highestPriority = 0;
  let highestStatus: LevelStatus = LevelStatus.TooLow;

  for (const status of statuses) {
    const priority = STATUS_PRIORITY[status];
    if (priority > highestPriority) {
      highestPriority = priority;
      highestStatus = status;
    }
  }

  return STATUS_HEX_COLORS[highestStatus];
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx vitest run tests/unit/watershedGrouping.test.ts
```

Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/utils/watershedGrouping.ts tests/unit/watershedGrouping.test.ts
git commit -m "feat: add watershed grouping utility with marker color priority"
```

---

## Chunk 3: Precipitation Map Components

### Task 4: Create WatershedPopup component

**Files:**

- Create: `src/components/precipitation/WatershedPopup.tsx`

- [ ] **Step 1: Create the popup component**

Create `src/components/precipitation/WatershedPopup.tsx`:

```typescript
import { Box, Typography, Chip } from '@mui/material';
import { Link } from 'react-router-dom';
import { Watershed } from '../../utils/watershedGrouping';
import { GaugeReading, LevelStatus, LevelTrend } from '../../types/stream';
import { determineLevel, determineTrend } from '../../utils/streamLevels';
import { STATUS_HEX_COLORS } from '../../utils/streamLevels';
import { getStreamIdFromName } from '../../utils/streamIds';
import { getTrendLabel } from '../../utils/trendUtils';

interface WatershedPopupProps {
  watershed: Watershed;
  reading: GaugeReading | null;
  previousReading: GaugeReading | null;
}

const STATUS_LABELS: Record<LevelStatus, string> = {
  [LevelStatus.TooLow]: 'Too Low',
  [LevelStatus.Low]: 'Low',
  [LevelStatus.Optimal]: 'Optimal',
  [LevelStatus.High]: 'High',
};

export function WatershedPopup({
  watershed,
  reading,
  previousReading,
}: WatershedPopupProps) {
  const trend = reading && previousReading
    ? determineTrend(reading, previousReading)
    : LevelTrend.None;
  const trendLabel = getTrendLabel(trend);

  return (
    <Box sx={{ minWidth: 200, maxWidth: 280 }}>
      <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 0.5 }}>
        {watershed.gauge.name}
      </Typography>

      {reading ? (
        <Typography variant="body2" sx={{ mb: 1, color: 'text.secondary' }}>
          {reading.value} ft{trendLabel ? ` (${trendLabel})` : ''}
        </Typography>
      ) : (
        <Typography variant="body2" sx={{ mb: 1, color: 'text.disabled' }}>
          Loading...
        </Typography>
      )}

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {watershed.streams.map((stream) => {
          const status = reading
            ? determineLevel(reading.value, stream.targetLevels)
            : null;
          const streamId = getStreamIdFromName(stream.name);

          return (
            <Box
              key={stream.name}
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              {streamId ? (
                <Link
                  to={`/stream/${streamId}`}
                  style={{
                    color: 'inherit',
                    textDecoration: 'none',
                    fontSize: '0.8rem',
                  }}
                >
                  {stream.name}
                </Link>
              ) : (
                <Typography variant="caption">{stream.name}</Typography>
              )}
              {status && (
                <Chip
                  label={STATUS_LABELS[status]}
                  size="small"
                  sx={{
                    height: 20,
                    fontSize: '0.65rem',
                    bgcolor: STATUS_HEX_COLORS[status],
                    color: '#fff',
                  }}
                />
              )}
            </Box>
          );
        })}
      </Box>
    </Box>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx tsc --noEmit
```

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add src/components/precipitation/WatershedPopup.tsx
git commit -m "feat: add WatershedPopup component for map marker popups"
```

---

### Task 5: Create LayerControl component

**Files:**

- Create: `src/components/precipitation/LayerControl.tsx`

- [ ] **Step 1: Create the layer control component**

Create `src/components/precipitation/LayerControl.tsx`:

```typescript
import { ToggleButtonGroup, ToggleButton, Paper } from '@mui/material';
import { Radar, WaterDrop } from '@mui/icons-material';

export type PrecipLayer = 'radar' | '24h' | '48h' | '72h';

interface LayerControlProps {
  activeLayer: PrecipLayer;
  onChange: (layer: PrecipLayer) => void;
}

export function LayerControl({ activeLayer, onChange }: LayerControlProps) {
  return (
    <Paper
      elevation={3}
      sx={{
        position: 'absolute',
        bottom: 16,
        left: 16,
        zIndex: 1000,
        borderRadius: 2,
      }}
    >
      <ToggleButtonGroup
        value={activeLayer}
        exclusive
        onChange={(_, value) => {
          if (value !== null) onChange(value as PrecipLayer);
        }}
        size="small"
        aria-label="precipitation layer"
      >
        <ToggleButton value="radar" aria-label="live radar">
          <Radar sx={{ mr: 0.5, fontSize: 18 }} />
          Radar
        </ToggleButton>
        <ToggleButton value="24h" aria-label="24 hour precipitation">
          <WaterDrop sx={{ mr: 0.5, fontSize: 18 }} />
          24h
        </ToggleButton>
        <ToggleButton value="48h" aria-label="48 hour precipitation">
          48h
        </ToggleButton>
        <ToggleButton value="72h" aria-label="72 hour precipitation">
          72h
        </ToggleButton>
      </ToggleButtonGroup>
    </Paper>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
git add src/components/precipitation/LayerControl.tsx
git commit -m "feat: add LayerControl toggle for precipitation tile layers"
```

---

### Task 6: Create ForecastPanel component

**Files:**

- Create: `src/components/precipitation/ForecastPanel.tsx`

- [ ] **Step 1: Create the forecast panel component**

Create `src/components/precipitation/ForecastPanel.tsx`:

```typescript
import { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Typography,
  Link as MuiLink,
  Paper,
} from '@mui/material';

type ForecastTab = 'qpf' | 'observed';

const QPF_IMAGES = [
  {
    label: 'Day 1',
    url: 'https://www.wpc.ncep.noaa.gov/qpf/fill_94qwbg.gif',
  },
  {
    label: 'Day 2',
    url: 'https://www.wpc.ncep.noaa.gov/qpf/fill_98qwbg.gif',
  },
  {
    label: 'Day 3',
    url: 'https://www.wpc.ncep.noaa.gov/qpf/fill_99qwbg.gif',
  },
];

function getObservedUrl(period: string): string {
  const now = new Date();
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, '0');
  const dd = String(now.getDate()).padStart(2, '0');
  return `https://water.weather.gov/precip/downloads/${yyyy}/${mm}/${dd}/nws_precip_${period}_observed.png`;
}

const OBSERVED_IMAGES = [
  { label: '1 Day', period: 'last24hrs' },
  { label: '2 Day', period: 'last48hrs' },
  { label: '7 Day', period: 'last7days' },
];

function ImageWithFallback({
  src,
  alt,
  fallbackUrl,
  fallbackLabel,
}: {
  src: string;
  alt: string;
  fallbackUrl: string;
  fallbackLabel: string;
}) {
  const [error, setError] = useState(false);

  if (error) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          py: 4,
          color: 'text.secondary',
        }}
      >
        <Typography variant="body2" sx={{ mb: 1 }}>
          {fallbackLabel}
        </Typography>
        <MuiLink href={fallbackUrl} target="_blank" rel="noopener noreferrer">
          View on source site
        </MuiLink>
      </Box>
    );
  }

  return (
    <Box
      component="img"
      src={src}
      alt={alt}
      onError={() => setError(true)}
      sx={{ width: '100%', height: 'auto', borderRadius: 1 }}
    />
  );
}

export function ForecastPanel() {
  const [tab, setTab] = useState<ForecastTab>('qpf');
  const [qpfDay, setQpfDay] = useState(0);
  const [observedPeriod, setObservedPeriod] = useState(0);

  return (
    <Paper
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      <Tabs
        value={tab}
        onChange={(_, v) => setTab(v)}
        variant="fullWidth"
        sx={{ borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab label="Forecast (QPF)" value="qpf" />
        <Tab label="Observed" value="observed" />
      </Tabs>

      <Box sx={{ flex: 1, overflow: 'auto', p: 1.5 }}>
        {tab === 'qpf' && (
          <>
            <Tabs
              value={qpfDay}
              onChange={(_, v) => setQpfDay(v)}
              variant="fullWidth"
              sx={{ mb: 1 }}
            >
              {QPF_IMAGES.map((img, i) => (
                <Tab key={img.label} label={img.label} value={i} />
              ))}
            </Tabs>
            <ImageWithFallback
              src={QPF_IMAGES[qpfDay].url}
              alt={`QPF Forecast ${QPF_IMAGES[qpfDay].label}`}
              fallbackUrl="https://www.wpc.ncep.noaa.gov/qpf/qpf2.shtml"
              fallbackLabel="Forecast image unavailable"
            />
            <Typography
              variant="caption"
              sx={{ display: 'block', mt: 1, color: 'text.secondary' }}
            >
              Source: NOAA Weather Prediction Center
            </Typography>
          </>
        )}

        {tab === 'observed' && (
          <>
            <Tabs
              value={observedPeriod}
              onChange={(_, v) => setObservedPeriod(v)}
              variant="fullWidth"
              sx={{ mb: 1 }}
            >
              {OBSERVED_IMAGES.map((img, i) => (
                <Tab key={img.label} label={img.label} value={i} />
              ))}
            </Tabs>
            <ImageWithFallback
              src={getObservedUrl(OBSERVED_IMAGES[observedPeriod].period)}
              alt={`Observed precipitation ${OBSERVED_IMAGES[observedPeriod].label}`}
              fallbackUrl="https://water.weather.gov/precip/"
              fallbackLabel="Observed precipitation image unavailable"
            />
            <Typography
              variant="caption"
              sx={{ display: 'block', mt: 1, color: 'text.secondary' }}
            >
              Source: NWS Advanced Hydrologic Prediction Service
            </Typography>
          </>
        )}
      </Box>
    </Paper>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
git add src/components/precipitation/ForecastPanel.tsx
git commit -m "feat: add ForecastPanel with QPF forecast and observed precipitation images"
```

---

### Task 7: Create MapView component

**Files:**

- Create: `src/components/precipitation/MapView.tsx`

This is the core component — Leaflet map with tile overlays and watershed markers.

- [ ] **Step 1: Create the MapView component**

Create `src/components/precipitation/MapView.tsx`:

```typescript
import { useMemo } from 'react';
import { Box } from '@mui/material';
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
} from 'react-leaflet';
import type { PrecipLayer } from './LayerControl';
import { LayerControl } from './LayerControl';
import { WatershedPopup } from './WatershedPopup';
import { Watershed } from '../../utils/watershedGrouping';
import { getWatershedMarkerColor } from '../../utils/watershedGrouping';
import { GAUGE_LOCATIONS } from '../../data/gaugeLocations';
import { useGaugeDataContext } from '../../context/GaugeDataContext';
import { determineLevel } from '../../utils/streamLevels';
import { LevelStatus } from '../../types/stream';

const IEM_TILE_URL =
  'https://mesonet.agron.iastate.edu/cache/tile.py/1.0.0/{layer}/{z}/{x}/{y}.png';

const LAYER_IDS: Record<PrecipLayer, string> = {
  radar: 'nexrad-n0q-900913',
  '24h': 'q2-p24h',
  '48h': 'q2-p48h',
  '72h': 'q2-p72h',
};

const LAYER_ATTR =
  'Weather data &copy; <a href="https://mesonet.agron.iastate.edu/">Iowa Environmental Mesonet</a>';

const OZARK_CENTER: [number, number] = [35.5, -93.5];
const DEFAULT_ZOOM = 8;

interface MapViewProps {
  watersheds: Map<string, Watershed>;
  activeLayer: PrecipLayer;
  onLayerChange: (layer: PrecipLayer) => void;
}

export function MapView({
  watersheds,
  activeLayer,
  onLayerChange,
}: MapViewProps) {
  const { gauges } = useGaugeDataContext();

  const markers = useMemo(() => {
    const result: Array<{
      gaugeId: string;
      lat: number;
      lng: number;
      color: string;
      watershed: Watershed;
    }> = [];

    for (const [gaugeId, watershed] of watersheds) {
      const location = GAUGE_LOCATIONS[gaugeId];
      if (!location) continue;

      const gaugeData = gauges.get(gaugeId);
      const reading = gaugeData?.reading ?? null;

      const statuses: LevelStatus[] = reading
        ? watershed.streams.map((s) =>
            determineLevel(reading.value, s.targetLevels)
          )
        : [];

      result.push({
        gaugeId,
        lat: location.lat,
        lng: location.lng,
        color: getWatershedMarkerColor(statuses),
        watershed,
      });
    }

    return result;
  }, [watersheds, gauges]);

  const tileUrl = IEM_TILE_URL.replace('{layer}', LAYER_IDS[activeLayer]);

  return (
    <Box sx={{ position: 'relative', width: '100%', height: '100%' }}>
      <MapContainer
        center={OZARK_CENTER}
        zoom={DEFAULT_ZOOM}
        style={{ width: '100%', height: '100%' }}
        zoomControl={true}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>'
        />

        <TileLayer
          key={activeLayer}
          url={tileUrl}
          attribution={LAYER_ATTR}
          opacity={0.6}
        />

        {markers.map((marker) => {
          const gaugeData = gauges.get(marker.gaugeId);
          return (
            <CircleMarker
              key={marker.gaugeId}
              center={[marker.lat, marker.lng]}
              radius={10}
              pathOptions={{
                fillColor: marker.color,
                color: '#fff',
                weight: 2,
                fillOpacity: 0.85,
              }}
            >
              <Popup>
                <WatershedPopup
                  watershed={marker.watershed}
                  reading={gaugeData?.reading ?? null}
                  previousReading={gaugeData?.previousReading ?? null}
                />
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>

      <LayerControl activeLayer={activeLayer} onChange={onLayerChange} />
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
git add src/components/precipitation/MapView.tsx
git commit -m "feat: add MapView with Leaflet, IEM tiles, and watershed markers"
```

---

## Chunk 4: Page, Routing, and Navigation

### Task 8: Create PrecipitationMap page and lazy wrapper

**Files:**

- Create: `src/pages/PrecipitationMap.tsx`
- Create: `src/pages/PrecipitationMapLazy.tsx`

- [ ] **Step 1: Create the page component**

Create `src/pages/PrecipitationMap.tsx`:

```typescript
import { useState, useMemo } from 'react';
import { Box, useMediaQuery, useTheme } from '@mui/material';
import 'leaflet/dist/leaflet.css';
import { MapView } from '../components/precipitation/MapView';
import { ForecastPanel } from '../components/precipitation/ForecastPanel';
import { groupStreamsByWatershed } from '../utils/watershedGrouping';
import { streams } from '../data/streamData';
import type { PrecipLayer } from '../components/precipitation/LayerControl';

export default function PrecipitationMap() {
  const [activeLayer, setActiveLayer] = useState<PrecipLayer>('24h');
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const watersheds = useMemo(() => groupStreamsByWatershed(streams), []);

  if (isMobile) {
    return (
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ height: '60vh' }}>
          <MapView
            watersheds={watersheds}
            activeLayer={activeLayer}
            onLayerChange={setActiveLayer}
          />
        </Box>
        <Box sx={{ flex: 1, minHeight: 300 }}>
          <ForecastPanel />
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ flex: 1, display: 'flex' }}>
      <Box sx={{ flex: 1 }}>
        <MapView
          watersheds={watersheds}
          activeLayer={activeLayer}
          onLayerChange={setActiveLayer}
        />
      </Box>
      <Box sx={{ width: 350, flexShrink: 0 }}>
        <ForecastPanel />
      </Box>
    </Box>
  );
}
```

- [ ] **Step 2: Create the lazy wrapper**

Create `src/pages/PrecipitationMapLazy.tsx` (following `StreamPageLazy.tsx` pattern):

```typescript
import { lazy, Suspense } from 'react';
import { Box, CircularProgress } from '@mui/material';

const PrecipitationMap = lazy(() => import('./PrecipitationMap'));

function LoadingFallback() {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        flex: 1,
      }}
    >
      <CircularProgress />
    </Box>
  );
}

export function PrecipitationMapLazy() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <PrecipitationMap />
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
git add src/pages/PrecipitationMap.tsx src/pages/PrecipitationMapLazy.tsx
git commit -m "feat: add PrecipitationMap page with lazy loading"
```

---

### Task 9: Add route and header navigation

**Files:**

- Modify: `src/App.tsx`
- Modify: `src/components/core/Header.tsx`

- [ ] **Step 1: Add the precipitation route to App.tsx**

In `src/App.tsx`, add the import at the top:

```typescript
import { PrecipitationMapLazy } from './pages/PrecipitationMapLazy';
```

Add the new route inside `<Routes>`, after the `/stream/:streamId` route:

```typescript
<Route
  path="/precipitation"
  element={<PrecipitationMapLazy />}
/>
```

- [ ] **Step 2: Add precipitation nav button to Header.tsx**

In `src/components/core/Header.tsx`:

Add imports:

```typescript
import { Cloud } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
```

Inside the `Header` function, add navigation hooks:

```typescript
const navigate = useNavigate();
const location = useLocation();
const onPrecipMap = location.pathname === '/precipitation';
```

Add the Cloud icon button in the right-side `Box`, before the refresh `IconButton`:

```typescript
<IconButton
  onClick={() =>
    navigate(onPrecipMap ? '/dashboard' : '/precipitation')
  }
  aria-label="precipitation map"
  sx={{
    color: onPrecipMap ? theme.palette.primary.light : 'white',
    minWidth: 48,
    minHeight: 48,
    '&:hover': {
      backgroundColor: 'rgba(255, 255, 255, 0.1)',
    },
  }}
>
  <Cloud />
</IconButton>
```

- [ ] **Step 3: Verify TypeScript compiles and app starts**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx tsc --noEmit
```

Expected: No TS errors.

Then manually start the dev server (`npm run dev`) and navigate to `http://localhost:5174/precipitation` to visually verify: map renders with precipitation tiles and watershed markers, Cloud button in header toggles between dashboard and map.

- [ ] **Step 4: Run all existing tests to ensure nothing broke**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx vitest run
```

Expected: All existing tests pass.

- [ ] **Step 5: Run lint and format**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm run format && npm run lint
```

Expected: No errors.

- [ ] **Step 6: Verify production build**

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm run build
```

Expected: Build succeeds. `map-vendor` chunk in output.

- [ ] **Step 7: Commit**

```bash
git add src/App.tsx src/components/core/Header.tsx
git commit -m "feat: add /precipitation route and header navigation button"
```

---

## Summary

| Task | What                             | Files                                                                    |
| ---- | -------------------------------- | ------------------------------------------------------------------------ |
| 1    | Install deps + build config      | `package.json`, `vite.config.ts`                                         |
| 2    | Gauge location coordinates       | `src/data/gaugeLocations.ts`                                             |
| 3    | Watershed grouping utility (TDD) | `src/utils/watershedGrouping.ts`, `tests/unit/watershedGrouping.test.ts` |
| 4    | WatershedPopup component         | `src/components/precipitation/WatershedPopup.tsx`                        |
| 5    | LayerControl component           | `src/components/precipitation/LayerControl.tsx`                          |
| 6    | ForecastPanel component          | `src/components/precipitation/ForecastPanel.tsx`                         |
| 7    | MapView component                | `src/components/precipitation/MapView.tsx`                               |
| 8    | Page + lazy wrapper              | `src/pages/PrecipitationMap.tsx`, `src/pages/PrecipitationMapLazy.tsx`   |
| 9    | Route + header nav               | `src/App.tsx`, `src/components/core/Header.tsx`                          |
