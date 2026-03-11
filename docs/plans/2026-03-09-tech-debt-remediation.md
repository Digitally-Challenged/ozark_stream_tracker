# Tech Debt Remediation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Eliminate security vulnerabilities, remove dead code, and consolidate duplicated color/trend/filter logic into single sources of truth.

**Architecture:** Extract shared utilities from scattered component-level implementations into centralized modules (`src/utils/`), delete unused dependencies and dead code, and fix npm audit vulnerabilities.

**Tech Stack:** React 18, TypeScript (strict), Material-UI 5, Vite 5, Vitest

---

### Task 1: Fix Security Vulnerabilities & Remove Unused Dependencies

**Files:**

- Modify: `package.json`
- Modify: `vite.config.ts:8-10`

**Step 1: Run npm audit fix**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm audit fix`
Expected: 0 vulnerabilities remaining (fixes 12 issues including XSS in react-router, DoS in axios, path traversal in rollup)

**Step 2: Remove unused `axios` dependency**

`axios` is listed in `package.json:22` but never imported anywhere — the codebase uses native `fetch`. Remove it:

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm uninstall axios
```

**Step 3: Remove unused `cheerio` from frontend dependencies**

`cheerio` at `package.json:23` is only needed in `netlify/functions/` (which has its own `package.json`). It should not be in the frontend bundle:

```bash
cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm uninstall cheerio
```

**Step 4: Remove `lucide-react` from vite config**

In `vite.config.ts`, delete the `optimizeDeps.exclude` block (lines 8-10). `lucide-react` is not installed or used:

```typescript
// DELETE these lines from vite.config.ts:
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
```

**Step 5: Verify build still works**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm run build`
Expected: Build succeeds with no errors

**Step 6: Verify tests still pass**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm run test:run`
Expected: All tests pass

**Step 7: Commit**

```bash
git add package.json package-lock.json vite.config.ts
git commit -m "fix: remove unused deps (axios, cheerio) and fix npm audit vulnerabilities"
```

---

### Task 2: Delete Dead Code

**Files:**

- Modify: `src/services/turnerBendScraper.ts` (delete lines 10-11, 96-103)
- Modify: `src/utils/streamLevels.ts` (delete lines 87-88)

**Step 1: Remove dead `scrapeFromServer` method and commented URL from `turnerBendScraper.ts`**

Delete the commented-out `SCRAPE_URL` (lines 10-11):

```typescript
// DELETE:
// URL available for future server-side scraping implementation
// private static readonly SCRAPE_URL = 'https://www.turnerbend.com/WaterLevel.html';
```

Delete the `scrapeFromServer` method that always throws (lines 96-103):

```typescript
// DELETE:
  // Server-side scraping function (for future backend implementation)
  static async scrapeFromServer(): Promise<TurnerBendData | null> {
    // This would be implemented on a backend service
    // to avoid CORS issues and properly parse HTML
    throw new Error(
      'Server-side scraping not implemented. Use a backend service.'
    );
  }
```

**Step 2: Remove commented-out alpha value from `streamLevels.ts`**

Delete lines 87-88:

```typescript
// DELETE:
// Alpha value available for future use
// const alpha = theme.palette.mode === 'dark' ? '0.2' : '0.1';
```

**Step 3: Verify lint passes**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm run lint`
Expected: No errors

**Step 4: Verify tests still pass**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm run test:run`
Expected: All tests pass

**Step 5: Commit**

```bash
git add src/services/turnerBendScraper.ts src/utils/streamLevels.ts
git commit -m "chore: remove dead code (unused scraper method, commented-out values)"
```

---

### Task 3: Consolidate Color Mapping to Single Source of Truth

**Context:** Level status colors are duplicated in 4 places with different formats (RGBA, hex, primary/secondary). We consolidate them all into `streamLevels.ts`.

**Files:**

- Modify: `src/utils/streamLevels.ts` (add new exports)
- Modify: `src/components/streams/StreamTableRow.tsx:38-54` (delete local `getLevelColor`, use import)
- Modify: `src/components/streams/StreamCard.tsx:27-32` (delete `STATUS_COLORS`, use import)
- Modify: `src/components/common/LiquidFillBar.tsx:25-33` (delete `STATUS_COLORS`, use import)
- Test: `tests/unit/streamLevels.test.ts` (add tests for new exports)

**Step 1: Write failing tests for new color utilities**

Add to `tests/unit/streamLevels.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';
import { LevelStatus } from '../../src/types/stream';
import {
  STATUS_HEX_COLORS,
  STATUS_GRADIENT_COLORS,
} from '../../src/utils/streamLevels';

describe('STATUS_HEX_COLORS', () => {
  it('maps all LevelStatus values to hex colors', () => {
    expect(STATUS_HEX_COLORS[LevelStatus.TooLow]).toBe('#d32f2f');
    expect(STATUS_HEX_COLORS[LevelStatus.Low]).toBe('#ed6c02');
    expect(STATUS_HEX_COLORS[LevelStatus.Optimal]).toBe('#2e7d32');
    expect(STATUS_HEX_COLORS[LevelStatus.High]).toBe('#0288d1');
  });
});

describe('STATUS_GRADIENT_COLORS', () => {
  it('maps all LevelStatus values to primary/secondary pairs', () => {
    expect(STATUS_GRADIENT_COLORS[LevelStatus.Optimal]).toEqual({
      primary: '#2e7d32',
      secondary: '#4caf50',
    });
    expect(STATUS_GRADIENT_COLORS[LevelStatus.TooLow]).toEqual({
      primary: '#d32f2f',
      secondary: '#f44336',
    });
  });
});
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx vitest run tests/unit/streamLevels.test.ts`
Expected: FAIL — `STATUS_HEX_COLORS` and `STATUS_GRADIENT_COLORS` not exported

**Step 3: Add color constants to `streamLevels.ts`**

Add at the top of `src/utils/streamLevels.ts` (after the imports, before `determineLevel`):

```typescript
/** Canonical hex colors for each level status — use throughout UI */
export const STATUS_HEX_COLORS: Record<LevelStatus, string> = {
  [LevelStatus.TooLow]: '#d32f2f',
  [LevelStatus.Low]: '#ed6c02',
  [LevelStatus.Optimal]: '#2e7d32',
  [LevelStatus.High]: '#0288d1',
};

/** Primary/secondary gradient pairs for liquid fill bars */
export const STATUS_GRADIENT_COLORS: Record<
  LevelStatus,
  { primary: string; secondary: string }
> = {
  [LevelStatus.TooLow]: { primary: '#d32f2f', secondary: '#f44336' },
  [LevelStatus.Low]: { primary: '#ed6c02', secondary: '#ff9800' },
  [LevelStatus.Optimal]: { primary: '#2e7d32', secondary: '#4caf50' },
  [LevelStatus.High]: { primary: '#0288d1', secondary: '#03a9f4' },
};
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx vitest run tests/unit/streamLevels.test.ts`
Expected: PASS

**Step 5: Replace `STATUS_COLORS` in `StreamCard.tsx`**

Delete lines 27-32 (the local `STATUS_COLORS` constant) and add import:

```typescript
// ADD to imports:
import { STATUS_HEX_COLORS } from '../../utils/streamLevels';

// REPLACE line 43-44:
//   const statusColor = currentLevel?.status
//     ? STATUS_COLORS[currentLevel.status]
// WITH:
    const statusColor = currentLevel?.status
      ? STATUS_HEX_COLORS[currentLevel.status]
```

**Step 6: Replace `STATUS_COLORS` in `LiquidFillBar.tsx`**

Delete lines 25-33 (the local `STATUS_COLORS` constant) and add import:

```typescript
// ADD to imports:
import { STATUS_GRADIENT_COLORS } from '../../utils/streamLevels';

// REPLACE line 43:
//   const colors = STATUS_COLORS[status];
// WITH:
const colors = STATUS_GRADIENT_COLORS[status];
```

**Step 7: Replace `getLevelColor` in `StreamTableRow.tsx`**

Delete the local `getLevelColor` function (lines 38-54) and import `getLevelStatusColor`:

```typescript
// ADD to imports (already imports getReadingFreshnessColor from this file):
import { getReadingFreshnessColor, getLevelStatusColor } from '../../utils/streamLevels';

// REPLACE line 206:
//   bgcolor: getLevelColor(currentLevel?.status),
// WITH:
          bgcolor: currentLevel?.status
            ? getLevelStatusColor(currentLevel.status as LevelStatus, theme)
            : undefined,
```

Also add `LevelStatus` to the import from `../../types/stream` on line 13.

**Step 8: Verify build and tests pass**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm run build && npm run test:run`
Expected: Build succeeds, all tests pass

**Step 9: Verify lint passes**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm run lint`
Expected: No errors

**Step 10: Commit**

```bash
git add src/utils/streamLevels.ts src/components/streams/StreamCard.tsx src/components/common/LiquidFillBar.tsx src/components/streams/StreamTableRow.tsx tests/unit/streamLevels.test.ts
git commit -m "refactor: consolidate level status colors into single source of truth in streamLevels.ts"
```

---

### Task 4: Extract Trend Info Utility

**Context:** Trend-to-icon/label/color mapping is duplicated in `StreamDetail.tsx` (lines 57-83) and `StreamConditionIcon.tsx` (lines 176-211). Extract to a shared utility.

**Files:**

- Create: `src/utils/trendUtils.ts`
- Modify: `src/components/streams/StreamDetail.tsx:57-83` (delete `getTrendInfo`, use import)
- Test: `tests/unit/trendUtils.test.ts`

**Step 1: Write failing test for trend utility**

Create `tests/unit/trendUtils.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';
import { LevelTrend } from '../../src/types/stream';
import { getTrendLabel, getTrendMuiColor } from '../../src/utils/trendUtils';

describe('getTrendLabel', () => {
  it('returns Rising for rising trend', () => {
    expect(getTrendLabel(LevelTrend.Rising)).toBe('Rising');
  });

  it('returns Falling for falling trend', () => {
    expect(getTrendLabel(LevelTrend.Falling)).toBe('Falling');
  });

  it('returns Stable for holding trend', () => {
    expect(getTrendLabel(LevelTrend.Holding)).toBe('Stable');
  });

  it('returns null for none trend', () => {
    expect(getTrendLabel(LevelTrend.None)).toBeNull();
  });
});

describe('getTrendMuiColor', () => {
  it('returns success.main for rising', () => {
    expect(getTrendMuiColor(LevelTrend.Rising)).toBe('success.main');
  });

  it('returns error.main for falling', () => {
    expect(getTrendMuiColor(LevelTrend.Falling)).toBe('error.main');
  });

  it('returns warning.main for holding', () => {
    expect(getTrendMuiColor(LevelTrend.Holding)).toBe('warning.main');
  });

  it('returns null for none', () => {
    expect(getTrendMuiColor(LevelTrend.None)).toBeNull();
  });
});
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx vitest run tests/unit/trendUtils.test.ts`
Expected: FAIL — module not found

**Step 3: Implement `trendUtils.ts`**

Create `src/utils/trendUtils.ts`:

```typescript
import { LevelTrend } from '../types/stream';
import { TrendingUp, TrendingDown, HorizontalRule } from '@mui/icons-material';
import { SvgIconComponent } from '@mui/icons-material';

interface TrendInfo {
  icon: SvgIconComponent;
  label: string;
  muiColor: string;
}

export function getTrendLabel(trend: LevelTrend): string | null {
  switch (trend) {
    case LevelTrend.Rising:
      return 'Rising';
    case LevelTrend.Falling:
      return 'Falling';
    case LevelTrend.Holding:
      return 'Stable';
    default:
      return null;
  }
}

export function getTrendMuiColor(trend: LevelTrend): string | null {
  switch (trend) {
    case LevelTrend.Rising:
      return 'success.main';
    case LevelTrend.Falling:
      return 'error.main';
    case LevelTrend.Holding:
      return 'warning.main';
    default:
      return null;
  }
}

export function getTrendInfo(trend: LevelTrend): TrendInfo | null {
  if (trend === LevelTrend.None) return null;

  const label = getTrendLabel(trend);
  const muiColor = getTrendMuiColor(trend);
  if (!label || !muiColor) return null;

  const icons: Record<string, SvgIconComponent> = {
    [LevelTrend.Rising]: TrendingUp,
    [LevelTrend.Falling]: TrendingDown,
    [LevelTrend.Holding]: HorizontalRule,
  };

  return {
    icon: icons[trend],
    label,
    muiColor,
  };
}
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx vitest run tests/unit/trendUtils.test.ts`
Expected: PASS

**Step 5: Replace `getTrendInfo` in `StreamDetail.tsx`**

Replace the local `getTrendInfo` function (lines 57-83) with an import:

```typescript
// ADD to imports:
import { getTrendInfo as getTrendInfoUtil } from '../../utils/trendUtils';

// REPLACE lines 57-83 (the entire getTrendInfo function) WITH:
const getTrendInfo = () => {
  if (!currentLevel?.trend) return null;
  const info = getTrendInfoUtil(currentLevel.trend);
  if (!info) return null;
  return {
    icon: info.icon,
    label: info.label,
    color:
      theme.palette.mode === 'dark'
        ? (theme.palette as Record<string, { main: string }>)[
            info.muiColor.split('.')[0]
          ]?.main || info.muiColor
        : (theme.palette as Record<string, { main: string }>)[
            info.muiColor.split('.')[0]
          ]?.main || info.muiColor,
  };
};
```

Note: The StreamDetail component resolves theme colors from the palette, so we need to map `muiColor` string to the actual theme color. A simpler approach — since `StreamDetail` only uses `success.main`, `error.main`, `warning.main`:

```typescript
// SIMPLER APPROACH - replace lines 57-83 with:
const getTrendInfo = () => {
  if (!currentLevel?.trend || currentLevel.trend === LevelTrend.None)
    return null;
  const info = getTrendInfoUtil(currentLevel.trend);
  if (!info) return null;
  return {
    icon: info.icon,
    label: info.label,
    color:
      info.muiColor === 'success.main'
        ? theme.palette.success.main
        : info.muiColor === 'error.main'
          ? theme.palette.error.main
          : theme.palette.warning.main,
  };
};
```

Remove unused imports: `TrendingUp`, `TrendingDown`, `HorizontalRule` from `@mui/icons-material` on lines 6-8 of StreamDetail.tsx.

**Step 6: Verify build and tests pass**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm run build && npm run test:run`
Expected: Build succeeds, all tests pass

**Step 7: Commit**

```bash
git add src/utils/trendUtils.ts tests/unit/trendUtils.test.ts src/components/streams/StreamDetail.tsx
git commit -m "refactor: extract trend info utility to eliminate duplication across components"
```

---

### Task 5: Extract Filter Logic

**Context:** Rating/size filter logic is near-identical in `DashboardPage.tsx:41-54` and `StreamTable.tsx:50-73`. `StreamTable` also adds search — but the rating/size part is pure duplication.

**Files:**

- Create: `src/utils/filterStreams.ts`
- Modify: `src/pages/DashboardPage.tsx:41-54` (use shared filter)
- Modify: `src/components/streams/StreamTable.tsx:50-73` (use shared filter)
- Test: `tests/unit/filterStreams.test.ts`

**Step 1: Write failing test**

Create `tests/unit/filterStreams.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';
import { filterByRatingAndSize } from '../../src/utils/filterStreams';
import { StreamData } from '../../src/types/stream';

const mockStream = (name: string, rating: string, size: string): StreamData =>
  ({
    name,
    rating,
    size,
    gauge: { id: '1', name: 'test', url: '' },
    quality: 'A',
    targetLevels: { tooLow: 1, optimal: 2, high: 3 },
  }) as StreamData;

describe('filterByRatingAndSize', () => {
  const streams = [
    mockStream('Creek A', '5', 'S'),
    mockStream('Creek B', '3', 'M'),
    mockStream('Creek C', '5', 'L'),
  ];

  it('returns all streams when no filters applied', () => {
    expect(filterByRatingAndSize(streams, [], [])).toHaveLength(3);
  });

  it('filters by rating', () => {
    const result = filterByRatingAndSize(streams, ['5'], []);
    expect(result).toHaveLength(2);
    expect(result.map((s) => s.name)).toEqual(['Creek A', 'Creek C']);
  });

  it('filters by size', () => {
    const result = filterByRatingAndSize(streams, [], ['M']);
    expect(result).toHaveLength(1);
    expect(result[0].name).toBe('Creek B');
  });

  it('filters by both rating and size', () => {
    const result = filterByRatingAndSize(streams, ['5'], ['S']);
    expect(result).toHaveLength(1);
    expect(result[0].name).toBe('Creek A');
  });
});
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx vitest run tests/unit/filterStreams.test.ts`
Expected: FAIL — module not found

**Step 3: Implement `filterStreams.ts`**

Create `src/utils/filterStreams.ts`:

```typescript
import { StreamData } from '../types/stream';

export function filterByRatingAndSize(
  streams: StreamData[],
  selectedRatings: string[],
  selectedSizes: string[]
): StreamData[] {
  return streams.filter((stream) => {
    if (
      selectedRatings.length > 0 &&
      !selectedRatings.includes(stream.rating)
    ) {
      return false;
    }
    if (selectedSizes.length > 0 && !selectedSizes.includes(stream.size)) {
      return false;
    }
    return true;
  });
}
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npx vitest run tests/unit/filterStreams.test.ts`
Expected: PASS

**Step 5: Use in `DashboardPage.tsx`**

Replace the filter logic at lines 41-54:

```typescript
// ADD to imports:
import { filterByRatingAndSize } from '../utils/filterStreams';

// REPLACE lines 41-54 with:
const filteredStreams = useMemo(() => {
  return filterByRatingAndSize(streams, selectedRatings, selectedSizes);
}, [selectedRatings, selectedSizes]);
```

**Step 6: Use in `StreamTable.tsx`**

Replace the rating/size portion of the filter logic at lines 50-73:

```typescript
// ADD to imports:
import { filterByRatingAndSize } from '../../utils/filterStreams';

// REPLACE lines 50-73 with:
const filteredStreams = useMemo(() => {
  const ratingAndSizeFiltered = filterByRatingAndSize(
    streams,
    selectedRatings,
    selectedSizes
  );

  if (!searchTerm) return ratingAndSizeFiltered;

  const searchLower = searchTerm.toLowerCase();
  return ratingAndSizeFiltered.filter(
    (stream) =>
      stream.name.toLowerCase().includes(searchLower) ||
      (stream.gauge?.name &&
        stream.gauge.name.toLowerCase().includes(searchLower))
  );
}, [streams, selectedRatings, selectedSizes, searchTerm]);
```

**Step 7: Verify build and tests pass**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm run build && npm run test:run`
Expected: Build succeeds, all tests pass

**Step 8: Verify lint passes**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm run lint`
Expected: No errors

**Step 9: Commit**

```bash
git add src/utils/filterStreams.ts tests/unit/filterStreams.test.ts src/pages/DashboardPage.tsx src/components/streams/StreamTable.tsx
git commit -m "refactor: extract shared filter logic to eliminate duplication between DashboardPage and StreamTable"
```

---

### Task 6: Add Accessibility Labels

**Files:**

- Modify: `src/components/icons/StreamConditionIcon.tsx:213-214`
- Modify: `src/components/streams/StreamTable.tsx:102-104`

**Step 1: Add `aria-label` to StreamConditionIcon**

In `StreamConditionIcon.tsx`, add `aria-label` to the wrapping Box at line 215:

```typescript
// REPLACE line 215-218:
      <Box
        sx={{
          display: 'inline-flex',
          alignItems: 'center',
// WITH:
      <Box
        aria-label={`Stream condition: ${levelInfo.name}`}
        sx={{
          display: 'inline-flex',
          alignItems: 'center',
```

**Step 2: Add `aria-label` to search field in StreamTable**

In `StreamTable.tsx`, add `aria-label` to the TextField at line 102:

```typescript
// ADD aria-label prop to the TextField:
        <TextField
          placeholder="Search streams by name..."
          aria-label="Search streams"
          variant="outlined"
```

**Step 3: Verify lint passes**

Run: `cd /Users/COLEMAN/Documents/GitHub/ozark_stream_tracker && npm run lint`
Expected: No errors

**Step 4: Commit**

```bash
git add src/components/icons/StreamConditionIcon.tsx src/components/streams/StreamTable.tsx
git commit -m "fix: add aria-labels to stream condition icons and search field for accessibility"
```

---

## Summary

| Task | What                                    | Effort | Impact                       |
| ---- | --------------------------------------- | ------ | ---------------------------- |
| 1    | Fix vulnerabilities, remove unused deps | 15 min | Critical — security          |
| 2    | Delete dead code                        | 10 min | Clean codebase               |
| 3    | Consolidate color mapping               | 1 hr   | Eliminates 4-way duplication |
| 4    | Extract trend utility                   | 45 min | Eliminates 3-way duplication |
| 5    | Extract filter logic                    | 30 min | Eliminates 2-way duplication |
| 6    | Add accessibility labels                | 10 min | a11y compliance              |

**Total estimated effort:** ~3 hours

**Commit history after completion:**

1. `fix: remove unused deps (axios, cheerio) and fix npm audit vulnerabilities`
2. `chore: remove dead code (unused scraper method, commented-out values)`
3. `refactor: consolidate level status colors into single source of truth`
4. `refactor: extract trend info utility to eliminate duplication`
5. `refactor: extract shared filter logic to eliminate duplication`
6. `fix: add aria-labels for accessibility`
