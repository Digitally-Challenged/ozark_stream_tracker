# Comprehensive Improvements Roadmap

**Generated**: 2024-11-30
**Based on**: Multi-agent audit (Code Quality, Performance, Security, Architecture, UX)

---

## Phase 1: Foundation Cleanup (4 hours)

**Goal**: Remove dead code and fix impactful bugs with minimal risk.

### 1.1 Delete Dead Code

| File                               | Action | Reason                                              |
| ---------------------------------- | ------ | --------------------------------------------------- |
| `src/services/scraperScheduler.ts` | DELETE | Redundant - GaugeDataContext refreshes every 15 min |
| `src/services/scrapeProxy.ts`      | DELETE | Unused CORS proxy reference                         |
| `src/hooks/useStreamGauge.ts`      | DELETE | Duplicates GaugeDataContext + useGaugeReading       |

**Update App.tsx**: Remove ScraperScheduler import and initialization (lines 12, 28-35).

### 1.2 Fix Broken References After Deletion

- `StreamDetail.tsx:41` → Change `useStreamGauge` to `useGaugeReading`
- `StreamHeader.tsx` → Already fixed (uses GaugeDisplay sub-component)

### 1.3 Remove Duplicate Filtering

- `StreamTable.tsx` lines 50-72: Remove filter logic (already done in DashboardPage)
- `StreamGroup.tsx` lines 15-16, 25-26: Remove unused `selectedRatings`/`selectedSizes` props

### 1.4 Gate Console Logging

Wrap all console.log with `import.meta.env.DEV` check:

- Any remaining debug logs after useStreamGauge deletion

---

## Phase 2: Performance Fixes (4-6 hours)

**Goal**: Eliminate unnecessary re-renders and reduce timer overhead.

### 2.1 Memoize StreamCard

```tsx
// src/components/streams/StreamCard.tsx
export const StreamCard = memo(
  function StreamCard({ stream, onClick }: StreamCardProps) {
    // existing implementation
  },
  (prevProps, nextProps) => {
    return (
      prevProps.stream.name === nextProps.stream.name &&
      prevProps.stream.gauge?.id === nextProps.stream.gauge?.id &&
      prevProps.onClick === nextProps.onClick
    );
  }
);
```

### 2.2 Stabilize Callbacks in DashboardPage

```tsx
// src/pages/DashboardPage.tsx
const handleStreamClick = useCallback((stream: StreamData) => {
  setSelectedStream(stream);
}, []);
```

### 2.3 Stabilize useGaugeHistory Functions

```tsx
// src/hooks/useGaugeHistory.ts
const addReading = useCallback(
  (reading: GaugeReading) => {
    // implementation
  },
  [gaugeId]
);

const getPreviousReading = useCallback((): GaugeReading | null => {
  // implementation
}, [history, gaugeId]);
```

### 2.4 Stabilize StreamGroup Toggle

```tsx
// src/components/streams/StreamGroup.tsx
const handleToggle = useCallback(() => setExpanded((prev) => !prev), []);
```

### 2.5 Centralize Relative Time Updates (Optional - Higher Effort)

Consider creating a TimeContext to share a single timer instead of 90+ individual timers from useRelativeTime.

---

## Phase 3: Security Hardening (2-3 hours)

**Goal**: Close security gaps in backend API.

### 3.1 Add Rate Limiting

```bash
cd server && npm install express-rate-limit
```

```javascript
// server/server.js
const rateLimit = require('express-rate-limit');

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: { error: 'Too many requests' },
});

const scrapeLimiter = rateLimit({
  windowMs: 60 * 60 * 1000,
  max: 5,
  message: { error: 'Scrape rate limit exceeded' },
});

app.use('/api/', apiLimiter);
app.post('/api/turner-bend/scrape', scrapeLimiter);
```

### 3.2 Fix CORS for Production

```javascript
// server/server.js
const allowedOrigins =
  process.env.NODE_ENV === 'production'
    ? ['https://ozark-stream-tracker.netlify.app']
    : [
        'http://localhost:5174',
        'http://localhost:5175',
        'https://ozark-stream-tracker.netlify.app',
      ];

app.use(cors({ origin: allowedOrigins, credentials: true }));
```

### 3.3 Hide Error Details in Production

```javascript
// server/turnerBendScraper.js (both error handlers)
res.status(500).json({
  error: 'Failed to get Turner Bend data',
  message:
    process.env.NODE_ENV === 'development'
      ? error.message
      : 'An internal error occurred',
  timestamp: new Date().toISOString(),
});
```

### 3.4 Add Server Package Lock

```bash
cd server && npm install --package-lock-only
git add server/package-lock.json
```

---

## Phase 4: Accessibility (4-6 hours)

**Goal**: Meet WCAG 2.1 AA compliance for critical user paths.

### 4.1 Add Skip Link

```tsx
// src/App.tsx - First element inside Router
<a
  href="#main-content"
  style={{
    position: 'absolute',
    left: '-9999px',
    '&:focus': { left: 0, top: 0, zIndex: 9999 },
  }}
>
  Skip to main content
</a>
```

### 4.2 Add aria-labels to Interactive Elements

| File                    | Line    | Fix                                                                    |
| ----------------------- | ------- | ---------------------------------------------------------------------- |
| `Header.tsx`            | 164-176 | `aria-label="Open filters"`                                            |
| `Header.tsx`            | 178-192 | `aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}` |
| `StreamGroupHeader.tsx` | 89      | `aria-label={expanded ? 'Collapse section' : 'Expand section'}`        |
| `DashboardSidebar.tsx`  | 118-123 | `aria-label="Close filter panel"`                                      |
| `StreamTable.tsx`       | 102     | `aria-label="Search streams by name"`                                  |

### 4.3 Add Keyboard Support to StreamGroupHeader

```tsx
// src/components/streams/StreamGroupHeader.tsx
<Box
  onClick={onToggle}
  onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onToggle(); }}}
  tabIndex={0}
  role="button"
  aria-expanded={expanded}
  sx={{ cursor: 'pointer', /* existing styles */ }}
>
```

### 4.4 Respect prefers-reduced-motion

```tsx
// src/components/icons/StreamConditionIcon.tsx (and other animated components)
sx={{
  animation: `${ripple} 2s ease-out infinite`,
  '@media (prefers-reduced-motion: reduce)': {
    animation: 'none',
  },
}}
```

---

## Phase 5: Mobile UX (4-6 hours)

**Goal**: Make the app usable for paddlers checking conditions in the field.

### 5.1 Responsive Filter Drawer

```tsx
// src/components/dashboard/DashboardSidebar.tsx
<Drawer
  sx={{ width: { xs: '100%', sm: 320 } }}
  // ...
>
```

### 5.2 Increase Touch Targets

```tsx
// src/components/core/Header.tsx - All IconButtons
<IconButton sx={{ minWidth: 48, minHeight: 48 }}>
```

### 5.3 Add Active Filter Indicator

```tsx
// src/components/core/Header.tsx
const activeFilterCount = selectedRatings.length + selectedSizes.length;

<Badge badgeContent={activeFilterCount} color="primary">
  <IconButton aria-label="Open filters">
    <FilterList />
  </IconButton>
</Badge>;
```

### 5.4 Add "Show Runnable" Quick Filter

Add a prominent toggle button on DashboardPage that filters to Optimal status only.

### 5.5 Improve Loading States

Replace generic "Loading gauge data..." with skeleton screens showing the table/card structure.

---

## Phase 6: Architecture Polish (2-4 hours)

**Goal**: Clean up remaining technical debt.

### 6.1 Consolidate STATUS_COLORS

Move hardcoded colors from `StreamCard.tsx` to theme or constants:

```tsx
// src/constants/index.ts
export const STATUS_COLORS = {
  [LevelStatus.Optimal]: 'success.main',
  [LevelStatus.Low]: 'warning.main',
  [LevelStatus.High]: 'info.main',
  [LevelStatus.TooLow]: 'error.main',
};
```

### 6.2 Extract USGS API Types

Create proper TypeScript interfaces for USGS API responses instead of inline type assertions in GaugeDataContext.

### 6.3 Remove Unused Exports

- `useGaugeHistory.ts:91-96` - `getReadingAge` function is exported but never used

---

## Priority Order

| Phase                 | Effort  | Impact | Risk   |
| --------------------- | ------- | ------ | ------ |
| 1. Foundation Cleanup | 4 hrs   | High   | Low    |
| 2. Performance        | 4-6 hrs | High   | Medium |
| 3. Security           | 2-3 hrs | Medium | Low    |
| 4. Accessibility      | 4-6 hrs | High   | Low    |
| 5. Mobile UX          | 4-6 hrs | High   | Medium |
| 6. Architecture       | 2-4 hrs | Medium | Low    |

**Total estimated effort**: 20-29 hours (3-4 focused sessions)

**Recommended approach**: Complete Phase 1 + 2 in one session, then Phase 3-4, then Phase 5-6.

---

## Files Changed Summary

### Deleted

- `src/services/scraperScheduler.ts`
- `src/services/scrapeProxy.ts`
- `src/hooks/useStreamGauge.ts`

### Modified (Major)

- `src/App.tsx` - Remove scheduler, add skip link
- `src/pages/DashboardPage.tsx` - Stabilize callbacks, add quick filter
- `src/components/streams/StreamCard.tsx` - Add memo, use theme colors
- `src/components/streams/StreamTable.tsx` - Remove duplicate filtering
- `src/components/streams/StreamGroup.tsx` - Remove unused props, stabilize toggle
- `src/components/streams/StreamGroupHeader.tsx` - Add keyboard support, aria
- `src/hooks/useGaugeHistory.ts` - Wrap functions in useCallback
- `server/server.js` - Add rate limiting, fix CORS

### Modified (Minor)

- `src/components/core/Header.tsx` - Touch targets, aria-labels, filter badge
- `src/components/dashboard/DashboardSidebar.tsx` - Responsive width, aria-label
- `src/components/icons/StreamConditionIcon.tsx` - Reduced motion support
- `server/turnerBendScraper.js` - Hide error details in production
