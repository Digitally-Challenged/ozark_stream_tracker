# Next Session: Turner Bend Scraper + Trend UI Fixes

## Overview
Two major issues to address:
1. **Turner Bend Scraper** - Currently broken, regex never matches
2. **Water Flow Trend UI** - Inconsistent display, missing from some views

---

## Issue 1: Turner Bend Scraper (CRITICAL)

### Root Cause
The regex patterns in `server/turnerBendScraper.js` use double backslashes (`\\d`) which match literal `\d` characters instead of digits. **Scraper is 100% broken.**

### Files to Fix
- `server/turnerBendScraper.js` (main fix)
- `src/services/turnerBendScraper.ts` (error handling)
- `src/hooks/useStreamGauge.ts` (graceful fallback)

### Fix Tasks

**P0 - Critical:**
1. [ ] Fix regex patterns - change `\\d` to `\d` (lines 36, 43)
2. [ ] Implement singleton pattern - scraper creates duplicate cron jobs per request
3. [ ] Add backend response validation - prevent NaN/null from crashing frontend

**P1 - Improvements:**
4. [ ] Add graceful error handling - show "unavailable" instead of error
5. [ ] Fix date parsing - use explicit format instead of `new Date(ambiguous)`
6. [ ] Add scrape locking - prevent concurrent writes to data file
7. [ ] Delete `turnerBendScraperFixed.js` - duplicate dead code

### Regex Fix Example
```javascript
// BEFORE (broken):
const levelMatch = pageText.match(/(\\d+\\.?\\d*)\\s*['\"]|Level:\\s*(\\d+\\.?\\d*)/i);

// AFTER (working):
const levelMatch = pageText.match(/(\d+\.?\d*)\s*['"]|Level:\s*(\d+\.?\d*)/i);
```

---

## Issue 2: Water Flow Trend UI

### Root Causes
1. Duplicate trend calculation in two hooks (`useGaugeReading` vs `useStreamGauge`)
2. StreamCard hides "Holding" trend - only shows rising/falling
3. StreamDetail modal doesn't show trend at all
4. 30-minute minimum interval too long for real-time monitoring

### Files to Fix
- `src/hooks/useGaugeHistory.ts` - history management
- `src/hooks/useGaugeReading.ts` - consolidate trend calculation
- `src/components/streams/StreamCard.tsx` - show holding trend
- `src/components/streams/StreamDetail.tsx` - add trend display
- `src/constants/index.ts` - reduce interval to 5-10 min

### Fix Tasks

**P0 - Critical:**
1. [ ] Add trend to StreamDetail modal - currently missing entirely
2. [ ] Consolidate trend calculation - single source of truth in GaugeDataContext
3. [ ] Fix dependency in useGaugeReading - `getPreviousReading` causes recalculation

**P1 - UX Polish:**
4. [ ] Show "Holding" trend in StreamCard (currently hidden when stable)
5. [ ] Fix tooltip text - "rise" → "Rising", "fall" → "Falling"
6. [ ] Reduce MIN_TREND_INTERVAL from 30 to 5-10 minutes

**P2 - Data Quality:**
7. [ ] Move history from localStorage to GaugeDataContext
8. [ ] Add error handling for localStorage failures
9. [ ] Improve reading lookup (avoid timestamp matching edge cases)

### StreamCard Fix Example
```tsx
// BEFORE (hides holding):
{currentLevel.trend !== LevelTrend.None && (
  <TrendIcon trend={currentLevel.trend} />
)}

// AFTER (shows all trends):
<TrendIcon trend={currentLevel.trend} />
```

---

## Suggested Session Order

1. **Start with Turner Bend regex fix** - quick win, unblocks scraper
2. **Add trend to StreamDetail** - most visible missing feature
3. **Show holding trend in StreamCard** - UX consistency
4. **Consolidate trend hooks** - prevents future bugs
5. **Reduce interval and improve error handling** - polish

---

## Testing Plan

### Turner Bend
```bash
# Start backend
cd server && npm run dev

# Test scrape endpoint
curl http://localhost:3001/api/turner-bend/current

# Should return JSON with level, timestamp, not error
```

### Trend UI
1. Open dashboard, verify trend icons in table view
2. Switch to card view, verify trends shown (including "holding")
3. Click stream detail modal, verify trend displayed
4. Wait 5+ minutes, verify trend updates
