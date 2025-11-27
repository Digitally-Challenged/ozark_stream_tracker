# Architecture & UX Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the Ozark Stream Tracker from per-row API fetching to batched fetching, add visual grouping by stream condition, and support card/table view switching.

**Architecture:** Centralized `GaugeDataContext` fetches all ~20 unique USGS gauges in one API call, stores in a Map. Components consume via `useGaugeReading(gaugeId)` hook. Streams grouped by condition (Optimal/Low/High/TooLow) with collapsible sections. Dual card/table views with responsive defaults.

**Tech Stack:** React 18, TypeScript, Material-UI 5, Vite, USGS Water Services API

**Design Doc:** `docs/plans/2025-11-27-architecture-ux-redesign.md`

---

## Phase 1: Data Architecture (Batched API)

### Task 1: Create GaugeDataContext Types

**Files:**
- Create: `src/context/GaugeDataContext.tsx`

**Step 1: Create the context file with types**

```typescript
// src/context/GaugeDataContext.tsx
import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { GaugeReading } from '../types/stream';
import { API_CONFIG } from '../constants';
import { streams } from '../data/streamData';
import { TurnerBendScraper } from '../services/turnerBendScraper';

interface GaugeData {
  reading: GaugeReading | null;
  loading: boolean;
  error: Error | null;
}

interface GaugeDataContextValue {
  gauges: Map<string, GaugeData>;
  lastUpdated: Date | null;
  isLoading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
}

const GaugeDataContext = createContext<GaugeDataContextValue | null>(null);

// Extract unique gauge IDs from stream data
function getUniqueGaugeIds(): string[] {
  const ids = new Set<string>();
  streams.forEach(stream => {
    if (stream.gauge.id && stream.gauge.id !== 'TURNER_BEND') {
      ids.add(stream.gauge.id);
    }
  });
  return Array.from(ids);
}

interface GaugeDataProviderProps {
  children: ReactNode;
}

export function GaugeDataProvider({ children }: GaugeDataProviderProps) {
  const [gauges, setGauges] = useState<Map<string, GaugeData>>(new Map());
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchAllGauges = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    const newGauges = new Map<string, GaugeData>();
    const gaugeIds = getUniqueGaugeIds();

    try {
      // Batch fetch USGS gauges
      const response = await fetch(
        `${API_CONFIG.USGS_BASE_URL}?format=json&sites=${gaugeIds.join(',')}&parameterCd=${API_CONFIG.GAUGE_HEIGHT_PARAMETER}`,
        {
          headers: { Accept: 'application/json' },
          signal: AbortSignal.timeout(API_CONFIG.REQUEST_TIMEOUT_MS),
        }
      );

      if (!response.ok) {
        throw new Error(`USGS API error: ${response.status}`);
      }

      const data = await response.json();

      // Process each time series
      if (data.value?.timeSeries) {
        data.value.timeSeries.forEach((series: any) => {
          const siteCode = series.sourceInfo?.siteCode?.[0]?.value;
          if (siteCode && series.values?.[0]?.value?.[0]) {
            const latestValue = series.values[0].value[0];
            newGauges.set(siteCode, {
              reading: {
                value: parseFloat(latestValue.value),
                timestamp: latestValue.dateTime,
                dateTime: latestValue.dateTime,
              },
              loading: false,
              error: null,
            });
          }
        });
      }

      // Mark missing gauges as unavailable
      gaugeIds.forEach(id => {
        if (!newGauges.has(id)) {
          newGauges.set(id, {
            reading: null,
            loading: false,
            error: new Error('No data available'),
          });
        }
      });

    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch gauge data'));
      // Mark all as errored
      gaugeIds.forEach(id => {
        newGauges.set(id, {
          reading: null,
          loading: false,
          error: err instanceof Error ? err : new Error('Failed to fetch'),
        });
      });
    }

    // Fetch Turner Bend separately
    try {
      const turnerBendReading = await TurnerBendScraper.fetchGaugeData();
      newGauges.set('TURNER_BEND', {
        reading: turnerBendReading,
        loading: false,
        error: turnerBendReading ? null : new Error('Turner Bend unavailable'),
      });
    } catch (err) {
      newGauges.set('TURNER_BEND', {
        reading: null,
        loading: false,
        error: err instanceof Error ? err : new Error('Turner Bend fetch failed'),
      });
    }

    setGauges(newGauges);
    setLastUpdated(new Date());
    setIsLoading(false);
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchAllGauges();
  }, [fetchAllGauges]);

  // Auto-refresh interval
  useEffect(() => {
    const interval = setInterval(fetchAllGauges, API_CONFIG.REFRESH_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchAllGauges]);

  return (
    <GaugeDataContext.Provider
      value={{
        gauges,
        lastUpdated,
        isLoading,
        error,
        refresh: fetchAllGauges,
      }}
    >
      {children}
    </GaugeDataContext.Provider>
  );
}

export function useGaugeDataContext() {
  const context = useContext(GaugeDataContext);
  if (!context) {
    throw new Error('useGaugeDataContext must be used within GaugeDataProvider');
  }
  return context;
}
```

**Step 2: Verify no TypeScript errors**

Run: `npx tsc --noEmit`
Expected: No errors related to GaugeDataContext

**Step 3: Commit**

```bash
git add src/context/GaugeDataContext.tsx
git commit -m "feat: add GaugeDataContext for batched gauge fetching"
```

---

### Task 2: Create useGaugeReading Hook

**Files:**
- Create: `src/hooks/useGaugeReading.ts`

**Step 1: Create the hook**

```typescript
// src/hooks/useGaugeReading.ts
import { useMemo } from 'react';
import { useGaugeDataContext } from '../context/GaugeDataContext';
import { GaugeReading, LevelStatus, LevelTrend, TargetLevels } from '../types/stream';
import { determineLevel, determineTrend } from '../utils/streamLevels';
import { useGaugeHistory } from './useGaugeHistory';

interface UseGaugeReadingResult {
  reading: GaugeReading | null;
  currentLevel: {
    status: LevelStatus;
    trend: LevelTrend;
  } | undefined;
  loading: boolean;
  error: Error | null;
}

export function useGaugeReading(
  gaugeId: string,
  targetLevels: TargetLevels
): UseGaugeReadingResult {
  const { gauges, isLoading } = useGaugeDataContext();
  const { addReading, getPreviousReading } = useGaugeHistory(gaugeId);

  const gaugeData = gauges.get(gaugeId);

  const result = useMemo(() => {
    if (!gaugeData) {
      return {
        reading: null,
        currentLevel: undefined,
        loading: isLoading,
        error: null,
      };
    }

    const { reading, loading, error } = gaugeData;

    if (!reading) {
      return {
        reading: null,
        currentLevel: undefined,
        loading: loading || isLoading,
        error,
      };
    }

    // Calculate level status
    const status = determineLevel(reading.value, targetLevels);

    // Get previous reading for trend calculation
    const previousReading = getPreviousReading();
    const trend = previousReading
      ? determineTrend(reading, previousReading)
      : LevelTrend.None;

    // Store current reading for future trend calculation
    addReading(reading);

    return {
      reading,
      currentLevel: { status, trend },
      loading: false,
      error: null,
    };
  }, [gaugeData, isLoading, targetLevels, addReading, getPreviousReading]);

  return result;
}
```

**Step 2: Verify no TypeScript errors**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add src/hooks/useGaugeReading.ts
git commit -m "feat: add useGaugeReading hook consuming context"
```

---

### Task 3: Wrap App with GaugeDataProvider

**Files:**
- Modify: `src/App.tsx`

**Step 1: Import and wrap with provider**

Add import at top of `src/App.tsx`:
```typescript
import { GaugeDataProvider } from './context/GaugeDataContext';
```

Wrap the return JSX - change from:
```typescript
return (
  <ThemeProvider>
    <CssBaseline />
    <BrowserRouter>
```

To:
```typescript
return (
  <GaugeDataProvider>
    <ThemeProvider>
      <CssBaseline />
      <BrowserRouter>
```

And add closing tag before final `</ThemeProvider>`:
```typescript
      </BrowserRouter>
    </ThemeProvider>
  </GaugeDataProvider>
);
```

**Step 2: Verify app compiles**

Run: `npm run build`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add src/App.tsx
git commit -m "feat: wrap App with GaugeDataProvider"
```

---

### Task 4: Update StreamTableRow to Use New Hook

**Files:**
- Modify: `src/components/streams/StreamTableRow.tsx`

**Step 1: Replace useStreamGauge with useGaugeReading**

Change import from:
```typescript
import { useStreamGauge } from '../../hooks/useStreamGauge';
```

To:
```typescript
import { useGaugeReading } from '../../hooks/useGaugeReading';
```

Change hook usage from:
```typescript
const { currentLevel, reading, loading, error } = useStreamGauge(stream);
```

To:
```typescript
const { currentLevel, reading, loading, error } = useGaugeReading(
  stream.gauge.id,
  stream.targetLevels
);
```

**Step 2: Verify app works**

Run: `npm run dev`
Open browser, verify streams load and display data

**Step 3: Commit**

```bash
git add src/components/streams/StreamTableRow.tsx
git commit -m "refactor: StreamTableRow uses useGaugeReading hook"
```

---

## Phase 2: Visual Grouping

### Task 5: Create StreamGroupHeader Component

**Files:**
- Create: `src/components/streams/StreamGroupHeader.tsx`

**Step 1: Create the component**

```typescript
// src/components/streams/StreamGroupHeader.tsx
import { Box, Typography, IconButton, Chip, useTheme } from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';
import { LevelStatus } from '../../types/stream';

interface StreamGroupHeaderProps {
  status: LevelStatus;
  count: number;
  expanded: boolean;
  onToggle: () => void;
}

const STATUS_CONFIG: Record<LevelStatus, { label: string; emoji: string; color: string }> = {
  [LevelStatus.Optimal]: { label: 'Optimal - Running Good', emoji: '🟢', color: '#2e7d32' },
  [LevelStatus.Low]: { label: 'Low - Runnable but Scraping', emoji: '🟡', color: '#ed6c02' },
  [LevelStatus.High]: { label: 'High - Running Fast', emoji: '🔵', color: '#0288d1' },
  [LevelStatus.TooLow]: { label: 'Too Low - Not Runnable', emoji: '🔴', color: '#d32f2f' },
};

export function StreamGroupHeader({
  status,
  count,
  expanded,
  onToggle,
}: StreamGroupHeaderProps) {
  const theme = useTheme();
  const config = STATUS_CONFIG[status];

  return (
    <Box
      onClick={onToggle}
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        p: 2,
        cursor: 'pointer',
        borderRadius: 1,
        bgcolor: theme.palette.mode === 'dark'
          ? 'rgba(255,255,255,0.05)'
          : 'rgba(0,0,0,0.02)',
        '&:hover': {
          bgcolor: theme.palette.mode === 'dark'
            ? 'rgba(255,255,255,0.08)'
            : 'rgba(0,0,0,0.04)',
        },
        borderLeft: `4px solid ${config.color}`,
        mb: 1,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography variant="h6" component="span">
          {config.emoji}
        </Typography>
        <Typography variant="subtitle1" fontWeight="medium">
          {config.label}
        </Typography>
        <Chip
          label={count}
          size="small"
          sx={{
            bgcolor: config.color,
            color: 'white',
            fontWeight: 'bold',
          }}
        />
      </Box>
      <IconButton size="small">
        {expanded ? <ExpandLess /> : <ExpandMore />}
      </IconButton>
    </Box>
  );
}
```

**Step 2: Verify no TypeScript errors**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add src/components/streams/StreamGroupHeader.tsx
git commit -m "feat: add StreamGroupHeader component"
```

---

### Task 6: Create StreamGroup Component

**Files:**
- Create: `src/components/streams/StreamGroup.tsx`

**Step 1: Create the component**

```typescript
// src/components/streams/StreamGroup.tsx
import { useState } from 'react';
import { Box, Collapse } from '@mui/material';
import { StreamData, LevelStatus } from '../../types/stream';
import { StreamGroupHeader } from './StreamGroupHeader';
import { StreamTable } from './StreamTable';

interface StreamGroupProps {
  status: LevelStatus;
  streams: StreamData[];
  defaultExpanded?: boolean;
  onStreamClick: (stream: StreamData) => void;
  selectedRatings: string[];
  selectedSizes: string[];
}

export function StreamGroup({
  status,
  streams,
  defaultExpanded = true,
  onStreamClick,
  selectedRatings,
  selectedSizes,
}: StreamGroupProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  if (streams.length === 0) {
    return null;
  }

  return (
    <Box sx={{ mb: 3 }}>
      <StreamGroupHeader
        status={status}
        count={streams.length}
        expanded={expanded}
        onToggle={() => setExpanded(!expanded)}
      />
      <Collapse in={expanded}>
        <StreamTable
          streams={streams}
          onStreamClick={onStreamClick}
          selectedRatings={selectedRatings}
          selectedSizes={selectedSizes}
        />
      </Collapse>
    </Box>
  );
}
```

**Step 2: Verify no TypeScript errors**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add src/components/streams/StreamGroup.tsx
git commit -m "feat: add StreamGroup component with collapsible sections"
```

---

### Task 7: Create Stream Grouping Utility

**Files:**
- Create: `src/utils/streamGrouping.ts`

**Step 1: Create the utility**

```typescript
// src/utils/streamGrouping.ts
import { StreamData, LevelStatus } from '../types/stream';

export interface GroupedStreams {
  [LevelStatus.Optimal]: StreamData[];
  [LevelStatus.Low]: StreamData[];
  [LevelStatus.High]: StreamData[];
  [LevelStatus.TooLow]: StreamData[];
}

export function groupStreamsByStatus(
  streams: StreamData[],
  getStatus: (stream: StreamData) => LevelStatus | undefined
): GroupedStreams {
  const groups: GroupedStreams = {
    [LevelStatus.Optimal]: [],
    [LevelStatus.Low]: [],
    [LevelStatus.High]: [],
    [LevelStatus.TooLow]: [],
  };

  streams.forEach(stream => {
    const status = getStatus(stream);
    if (status && groups[status]) {
      groups[status].push(stream);
    } else {
      // Default to TooLow if no reading available
      groups[LevelStatus.TooLow].push(stream);
    }
  });

  return groups;
}

// Order for display (most useful first)
export const GROUP_ORDER: LevelStatus[] = [
  LevelStatus.Optimal,
  LevelStatus.Low,
  LevelStatus.High,
  LevelStatus.TooLow,
];
```

**Step 2: Verify no TypeScript errors**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add src/utils/streamGrouping.ts
git commit -m "feat: add stream grouping utility"
```

---

### Task 8: Create useStreamStatus Hook

**Files:**
- Create: `src/hooks/useStreamStatus.ts`

**Step 1: Create the hook**

```typescript
// src/hooks/useStreamStatus.ts
import { useMemo } from 'react';
import { useGaugeDataContext } from '../context/GaugeDataContext';
import { StreamData, LevelStatus } from '../types/stream';
import { determineLevel } from '../utils/streamLevels';

export function useStreamStatus(stream: StreamData): LevelStatus | undefined {
  const { gauges } = useGaugeDataContext();

  return useMemo(() => {
    const gaugeData = gauges.get(stream.gauge.id);
    if (!gaugeData?.reading) {
      return undefined;
    }
    return determineLevel(gaugeData.reading.value, stream.targetLevels);
  }, [gauges, stream.gauge.id, stream.targetLevels]);
}

export function useAllStreamStatuses(
  streams: StreamData[]
): Map<string, LevelStatus | undefined> {
  const { gauges } = useGaugeDataContext();

  return useMemo(() => {
    const statuses = new Map<string, LevelStatus | undefined>();

    streams.forEach(stream => {
      const gaugeData = gauges.get(stream.gauge.id);
      if (gaugeData?.reading) {
        statuses.set(stream.name, determineLevel(gaugeData.reading.value, stream.targetLevels));
      } else {
        statuses.set(stream.name, undefined);
      }
    });

    return statuses;
  }, [gauges, streams]);
}
```

**Step 2: Verify no TypeScript errors**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add src/hooks/useStreamStatus.ts
git commit -m "feat: add useStreamStatus hook for getting stream conditions"
```

---

### Task 9: Update DashboardPage with Grouped Streams

**Files:**
- Modify: `src/pages/DashboardPage.tsx`

**Step 1: Update imports**

Add to imports:
```typescript
import { useAllStreamStatuses } from '../hooks/useStreamStatus';
import { StreamGroup } from '../components/streams/StreamGroup';
import { groupStreamsByStatus, GROUP_ORDER } from '../utils/streamGrouping';
import { LevelStatus } from '../types/stream';
```

**Step 2: Add grouping logic and update render**

Replace the component body with:

```typescript
export function DashboardPage({
  selectedRatings,
  selectedSizes,
}: DashboardPageProps) {
  const [selectedStream, setSelectedStream] = useState<StreamData | null>(null);
  const streamStatuses = useAllStreamStatuses(streams);

  // Filter streams first
  const filteredStreams = useMemo(() => {
    return streams.filter((stream) => {
      if (selectedRatings.length > 0 && !selectedRatings.includes(stream.rating)) {
        return false;
      }
      if (selectedSizes.length > 0 && !selectedSizes.includes(stream.size)) {
        return false;
      }
      return true;
    });
  }, [selectedRatings, selectedSizes]);

  // Group filtered streams by status
  const groupedStreams = useMemo(() => {
    return groupStreamsByStatus(filteredStreams, (stream) =>
      streamStatuses.get(stream.name)
    );
  }, [filteredStreams, streamStatuses]);

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Container
        component="main"
        sx={{
          mt: 4,
          mb: 4,
          flex: 1,
          maxWidth: { xl: '1400px' },
        }}
      >
        <DashboardHeader />
        {GROUP_ORDER.map((status) => (
          <StreamGroup
            key={status}
            status={status}
            streams={groupedStreams[status]}
            defaultExpanded={status !== LevelStatus.TooLow}
            onStreamClick={(stream) => setSelectedStream(stream)}
            selectedRatings={selectedRatings}
            selectedSizes={selectedSizes}
          />
        ))}
      </Container>
      <StreamDetail
        stream={selectedStream}
        open={selectedStream !== null}
        onClose={() => setSelectedStream(null)}
      />
    </Box>
  );
}
```

**Step 3: Add useMemo import if not present**

Ensure useMemo is imported:
```typescript
import { useState, useMemo } from 'react';
```

**Step 4: Test the grouping**

Run: `npm run dev`
Verify streams are grouped by condition

**Step 5: Commit**

```bash
git add src/pages/DashboardPage.tsx
git commit -m "feat: DashboardPage shows streams grouped by condition"
```

---

## Phase 3: Card View & View Toggle

### Task 10: Create useViewPreference Hook

**Files:**
- Create: `src/hooks/useViewPreference.ts`

**Step 1: Create the hook**

```typescript
// src/hooks/useViewPreference.ts
import { useState, useEffect, useCallback } from 'react';

export type ViewMode = 'table' | 'cards';

const STORAGE_KEY = 'ozark-stream-tracker-view-mode';
const MOBILE_BREAKPOINT = 768;

export function useViewPreference(): {
  viewMode: ViewMode;
  setViewMode: (mode: ViewMode) => void;
  isManualOverride: boolean;
} {
  const [manualMode, setManualMode] = useState<ViewMode | null>(() => {
    if (typeof window === 'undefined') return null;
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === 'table' || stored === 'cards' ? stored : null;
  });

  const [windowWidth, setWindowWidth] = useState(() =>
    typeof window !== 'undefined' ? window.innerWidth : MOBILE_BREAKPOINT + 1
  );

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const responsiveDefault: ViewMode = windowWidth < MOBILE_BREAKPOINT ? 'cards' : 'table';
  const viewMode = manualMode ?? responsiveDefault;

  const setViewMode = useCallback((mode: ViewMode) => {
    setManualMode(mode);
    localStorage.setItem(STORAGE_KEY, mode);
  }, []);

  return {
    viewMode,
    setViewMode,
    isManualOverride: manualMode !== null,
  };
}
```

**Step 2: Verify no TypeScript errors**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add src/hooks/useViewPreference.ts
git commit -m "feat: add useViewPreference hook with responsive defaults"
```

---

### Task 11: Create ViewToggle Component

**Files:**
- Create: `src/components/streams/ViewToggle.tsx`

**Step 1: Create the component**

```typescript
// src/components/streams/ViewToggle.tsx
import { ToggleButton, ToggleButtonGroup, Tooltip } from '@mui/material';
import { ViewList, ViewModule } from '@mui/icons-material';
import { ViewMode } from '../../hooks/useViewPreference';

interface ViewToggleProps {
  viewMode: ViewMode;
  onChange: (mode: ViewMode) => void;
}

export function ViewToggle({ viewMode, onChange }: ViewToggleProps) {
  const handleChange = (_: React.MouseEvent<HTMLElement>, newMode: ViewMode | null) => {
    if (newMode !== null) {
      onChange(newMode);
    }
  };

  return (
    <ToggleButtonGroup
      value={viewMode}
      exclusive
      onChange={handleChange}
      size="small"
      aria-label="view mode"
    >
      <ToggleButton value="table" aria-label="table view">
        <Tooltip title="Table View">
          <ViewList />
        </Tooltip>
      </ToggleButton>
      <ToggleButton value="cards" aria-label="card view">
        <Tooltip title="Card View">
          <ViewModule />
        </Tooltip>
      </ToggleButton>
    </ToggleButtonGroup>
  );
}
```

**Step 2: Verify no TypeScript errors**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add src/components/streams/ViewToggle.tsx
git commit -m "feat: add ViewToggle component"
```

---

### Task 12: Create StreamCard Component

**Files:**
- Create: `src/components/streams/StreamCard.tsx`

**Step 1: Create the component**

```typescript
// src/components/streams/StreamCard.tsx
import { Card, CardContent, CardActionArea, Box, Typography, useTheme } from '@mui/material';
import { StreamData, LevelStatus, LevelTrend } from '../../types/stream';
import { useGaugeReading } from '../../hooks/useGaugeReading';
import { useRelativeTime } from '../../hooks/useRelativeTime';
import { RatingBadge } from '../badges/RatingBadge';
import { SizeBadge } from '../badges/SizeBadge';
import { StreamConditionIcon } from '../icons/StreamConditionIcon';
import { TrendIcon } from '../icons/TrendIcon';

interface StreamCardProps {
  stream: StreamData;
  onClick: (stream: StreamData) => void;
}

const STATUS_COLORS: Record<LevelStatus, string> = {
  [LevelStatus.Optimal]: '#2e7d32',
  [LevelStatus.Low]: '#ed6c02',
  [LevelStatus.High]: '#0288d1',
  [LevelStatus.TooLow]: '#d32f2f',
};

export function StreamCard({ stream, onClick }: StreamCardProps) {
  const { currentLevel, reading, loading, error } = useGaugeReading(
    stream.gauge.id,
    stream.targetLevels
  );
  const relativeTime = useRelativeTime(reading?.timestamp);
  const theme = useTheme();

  const statusColor = currentLevel?.status
    ? STATUS_COLORS[currentLevel.status]
    : theme.palette.grey[500];

  return (
    <Card
      sx={{
        height: '100%',
        borderLeft: `4px solid ${statusColor}`,
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: theme.shadows[4],
        },
      }}
    >
      <CardActionArea onClick={() => onClick(stream)} sx={{ height: '100%' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
            <Typography variant="h6" component="h3" sx={{ fontWeight: 'medium' }}>
              {stream.name}
            </Typography>
            {currentLevel?.status && (
              <StreamConditionIcon status={currentLevel.status} size="medium" />
            )}
          </Box>

          <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
            <RatingBadge rating={stream.rating} size="small" />
            <SizeBadge size={stream.size} />
            <Typography variant="caption" color="text.secondary">
              {stream.quality} quality
            </Typography>
          </Box>

          {loading ? (
            <Typography color="text.secondary">Loading...</Typography>
          ) : error ? (
            <Typography color="error">Unavailable</Typography>
          ) : reading ? (
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Typography variant="h5" component="span" fontWeight="bold">
                  {reading.value.toFixed(2)} ft
                </Typography>
                {currentLevel?.trend && currentLevel.trend !== LevelTrend.None && (
                  <TrendIcon trend={currentLevel.trend} size="small" />
                )}
              </Box>
              <Typography variant="body2" color="text.secondary">
                Updated {relativeTime}
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                Optimal: {stream.targetLevels.tooLow}-{stream.targetLevels.high} ft
              </Typography>
            </Box>
          ) : (
            <Typography color="text.secondary">No data</Typography>
          )}
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
```

**Step 2: Verify no TypeScript errors**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add src/components/streams/StreamCard.tsx
git commit -m "feat: add StreamCard component"
```

---

### Task 13: Create StreamCardGrid Component

**Files:**
- Create: `src/components/streams/StreamCardGrid.tsx`

**Step 1: Create the component**

```typescript
// src/components/streams/StreamCardGrid.tsx
import { Grid } from '@mui/material';
import { StreamData } from '../../types/stream';
import { StreamCard } from './StreamCard';

interface StreamCardGridProps {
  streams: StreamData[];
  onStreamClick: (stream: StreamData) => void;
}

export function StreamCardGrid({ streams, onStreamClick }: StreamCardGridProps) {
  return (
    <Grid container spacing={2}>
      {streams.map((stream) => (
        <Grid item xs={12} sm={6} md={4} lg={3} key={`${stream.name}-${stream.gauge.id}`}>
          <StreamCard stream={stream} onClick={onStreamClick} />
        </Grid>
      ))}
    </Grid>
  );
}
```

**Step 2: Verify no TypeScript errors**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add src/components/streams/StreamCardGrid.tsx
git commit -m "feat: add StreamCardGrid component"
```

---

### Task 14: Update StreamGroup to Support Both Views

**Files:**
- Modify: `src/components/streams/StreamGroup.tsx`

**Step 1: Update to accept viewMode and render conditionally**

```typescript
// src/components/streams/StreamGroup.tsx
import { useState } from 'react';
import { Box, Collapse } from '@mui/material';
import { StreamData, LevelStatus } from '../../types/stream';
import { StreamGroupHeader } from './StreamGroupHeader';
import { StreamTable } from './StreamTable';
import { StreamCardGrid } from './StreamCardGrid';
import { ViewMode } from '../../hooks/useViewPreference';

interface StreamGroupProps {
  status: LevelStatus;
  streams: StreamData[];
  defaultExpanded?: boolean;
  onStreamClick: (stream: StreamData) => void;
  selectedRatings: string[];
  selectedSizes: string[];
  viewMode: ViewMode;
}

export function StreamGroup({
  status,
  streams,
  defaultExpanded = true,
  onStreamClick,
  selectedRatings,
  selectedSizes,
  viewMode,
}: StreamGroupProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  if (streams.length === 0) {
    return null;
  }

  return (
    <Box sx={{ mb: 3 }}>
      <StreamGroupHeader
        status={status}
        count={streams.length}
        expanded={expanded}
        onToggle={() => setExpanded(!expanded)}
      />
      <Collapse in={expanded}>
        {viewMode === 'cards' ? (
          <StreamCardGrid streams={streams} onStreamClick={onStreamClick} />
        ) : (
          <StreamTable
            streams={streams}
            onStreamClick={onStreamClick}
            selectedRatings={selectedRatings}
            selectedSizes={selectedSizes}
          />
        )}
      </Collapse>
    </Box>
  );
}
```

**Step 2: Verify no TypeScript errors**

Run: `npx tsc --noEmit`
Expected: No errors

**Step 3: Commit**

```bash
git add src/components/streams/StreamGroup.tsx
git commit -m "feat: StreamGroup supports card and table views"
```

---

### Task 15: Update DashboardPage with View Toggle

**Files:**
- Modify: `src/pages/DashboardPage.tsx`

**Step 1: Add view toggle to page**

Update imports:
```typescript
import { useViewPreference } from '../hooks/useViewPreference';
import { ViewToggle } from '../components/streams/ViewToggle';
```

Add hook in component:
```typescript
const { viewMode, setViewMode } = useViewPreference();
```

Add toolbar with toggle after `<DashboardHeader />`:
```typescript
<Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
  <ViewToggle viewMode={viewMode} onChange={setViewMode} />
</Box>
```

Pass viewMode to each StreamGroup:
```typescript
<StreamGroup
  key={status}
  status={status}
  streams={groupedStreams[status]}
  defaultExpanded={status !== LevelStatus.TooLow}
  onStreamClick={(stream) => setSelectedStream(stream)}
  selectedRatings={selectedRatings}
  selectedSizes={selectedSizes}
  viewMode={viewMode}
/>
```

**Step 2: Test both views**

Run: `npm run dev`
Verify toggle switches between table and card views

**Step 3: Commit**

```bash
git add src/pages/DashboardPage.tsx
git commit -m "feat: add view toggle to DashboardPage"
```

---

## Phase 4: Polish & Error Handling

### Task 16: Add Loading State to Dashboard

**Files:**
- Modify: `src/pages/DashboardPage.tsx`

**Step 1: Add loading state from context**

Add import:
```typescript
import { useGaugeDataContext } from '../context/GaugeDataContext';
import { CircularProgress } from '@mui/material';
```

Add in component:
```typescript
const { isLoading, lastUpdated, error: gaugeError } = useGaugeDataContext();
```

Add loading state before groups:
```typescript
{isLoading && (
  <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
    <CircularProgress />
    <Typography sx={{ ml: 2 }}>Loading gauge data...</Typography>
  </Box>
)}

{gaugeError && (
  <Alert severity="error" sx={{ mb: 2 }}>
    Failed to load gauge data. Some streams may be unavailable.
  </Alert>
)}

{lastUpdated && (
  <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
    Data as of {lastUpdated.toLocaleTimeString()}
  </Typography>
)}
```

Add Alert import:
```typescript
import { Alert } from '@mui/material';
```

**Step 2: Test loading and error states**

Run: `npm run dev`
Verify loading spinner shows briefly on initial load

**Step 3: Commit**

```bash
git add src/pages/DashboardPage.tsx
git commit -m "feat: add loading and error states to DashboardPage"
```

---

### Task 17: Add Refresh Button to Header

**Files:**
- Modify: `src/components/core/Header.tsx`

**Step 1: Add refresh button**

Add imports:
```typescript
import { Refresh } from '@mui/icons-material';
import { useGaugeDataContext } from '../../context/GaugeDataContext';
```

Add in component:
```typescript
const { refresh, isLoading } = useGaugeDataContext();
```

Add refresh button next to theme toggle:
```typescript
<IconButton
  onClick={refresh}
  disabled={isLoading}
  color="inherit"
  aria-label="refresh data"
>
  <Refresh sx={{ animation: isLoading ? 'spin 1s linear infinite' : 'none' }} />
</IconButton>
```

Add keyframes for spin animation (in sx or global styles):
```typescript
'@keyframes spin': {
  from: { transform: 'rotate(0deg)' },
  to: { transform: 'rotate(360deg)' },
}
```

**Step 2: Test refresh button**

Run: `npm run dev`
Click refresh button, verify data reloads

**Step 3: Commit**

```bash
git add src/components/core/Header.tsx
git commit -m "feat: add refresh button to header"
```

---

### Task 18: Final Verification & Cleanup

**Files:**
- Review all modified files
- Delete deprecated code if any

**Step 1: Run full test suite**

Run: `npm run lint`
Fix any linting errors

Run: `npm run build`
Ensure production build succeeds

**Step 2: Manual testing checklist**

- [ ] App loads with batched API call (check Network tab - should see 1 USGS request)
- [ ] Streams grouped by condition
- [ ] Too Low section collapsed by default
- [ ] View toggle works
- [ ] Card view shows on mobile viewport
- [ ] Table view shows on desktop viewport
- [ ] Refresh button reloads data
- [ ] Search still works within groups
- [ ] Filters still work
- [ ] Stream detail drawer opens on click
- [ ] Theme toggle still works

**Step 3: Final commit**

```bash
git add -A
git commit -m "chore: cleanup and final polish"
```

---

## Summary

| Phase | Tasks | Key Deliverables |
|-------|-------|------------------|
| 1. Data Architecture | 1-4 | GaugeDataContext, useGaugeReading |
| 2. Visual Grouping | 5-9 | StreamGroup, StreamGroupHeader, grouping utils |
| 3. Card View | 10-15 | StreamCard, ViewToggle, useViewPreference |
| 4. Polish | 16-18 | Loading states, refresh button, cleanup |

**Total Tasks:** 18
**Estimated Time:** 2-3 hours of focused implementation
