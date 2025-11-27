# Architecture & UX Redesign

**Date**: 2025-11-27
**Status**: Approved
**Scope**: Performance optimization, UX improvements, visual polish

---

## Overview

Redesign the Ozark Stream Tracker to improve performance, discoverability, and visual appeal without over-engineering. The app already works; this effort focuses on making it faster and more useful for paddlers checking stream conditions.

### Goals

1. **Performance**: Reduce ~90 API calls to ~2 via batched fetching
2. **UX**: Help users instantly answer "What's runnable right now?"
3. **Visual**: Support both card and table views with responsive defaults

---

## 1. Data Architecture

### Problem

Each `StreamTableRow` makes its own `useStreamGauge` API call. With ~90 streams, this means ~90 concurrent requests on initial load. However, many streams share the same USGS gauge (~20 unique gauges).

### Solution

Centralized gauge data store with batched fetching.

```
GaugeDataProvider (React Context)
├── Extracts unique gauge IDs from streamData (~20)
├── Single USGS API call: sites=07055646,07252000,07340300,...
├── Stores readings in Map<gaugeId, GaugeReading>
├── Refreshes every 15 min (single interval)
└── Turner Bend fetched separately, added to same store

useGaugeReading(gaugeId) hook
├── Reads from context (no fetch)
└── Returns { reading, loading, error }
```

### API Call

```
GET https://waterservices.usgs.gov/nwis/iv/
  ?format=json
  &sites=07055646,07252000,07340300,07055875,...
  &parameterCd=00065
```

### Files

| Action | File |
|--------|------|
| Create | `src/context/GaugeDataContext.tsx` |
| Create | `src/hooks/useGaugeReading.ts` |
| Modify | `src/App.tsx` - wrap with GaugeDataProvider |
| Modify | `src/components/streams/StreamTableRow.tsx` - use new hook |
| Deprecate | Per-row fetching in `src/hooks/useStreamGauge.ts` |

### Result

~90 API calls → 2 API calls (USGS batch + Turner Bend)

---

## 2. Visual Grouping by Condition

### Problem

Flat list of 90 streams. User must scan everything to find runnable streams.

### Solution

Group streams by water level condition with collapsible sections.

```
┌─────────────────────────────────────────────────────────┐
│  🟢 Optimal - Running Good (12 streams)            [▼]  │
├─────────────────────────────────────────────────────────┤
│  Richland Cr.  │  III-IV  │  4.2 ft  │  ↑ Rising       │
│  Mulberry R.   │  II      │  2.8 ft  │  → Holding      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  🟡 Low - Runnable but Scraping (18 streams)       [▼]  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  🔵 High - Running Fast (5 streams)                [▼]  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  🔴 Too Low - Not Runnable (55 streams)            [▲]  │
│  (collapsed by default)                                 │
└─────────────────────────────────────────────────────────┘
```

### Behavior

- Optimal/Low/High sections expanded by default
- Too Low collapsed by default (most streams, least useful)
- Click header to expand/collapse
- Count badge updates in real-time as data refreshes
- Streams within each group still sortable by name/rating/size

### Files

| Action | File |
|--------|------|
| Create | `src/components/streams/StreamGroup.tsx` |
| Create | `src/components/streams/StreamGroupHeader.tsx` |
| Modify | `src/pages/DashboardPage.tsx` - grouping logic |

---

## 3. Card & Table Views

### Problem

Table works on desktop but is cramped on mobile. Different users prefer different layouts.

### Solution

Dual view modes with smart responsive defaults.

### Card View (default on mobile, < 768px)

```
┌─────────────────────────────────────────┐
│  Richland Creek                    🟢   │
│  ─────────────────────────────────────  │
│  III-IV  •  Medium  •  A quality        │
│                                         │
│  4.2 ft  ↑ Rising                       │
│  Updated 12 min ago                     │
│                                         │
│  [Optimal: 3.0-6.0 ft]                  │
└─────────────────────────────────────────┘
```

- Prominent condition indicator
- Key info scannable without horizontal scroll
- Tap to open detail drawer
- Responsive grid: 1 col mobile, 2-3 col tablet

### Table View (default on desktop, ≥ 768px)

Current table layout, enhanced:
- Stronger visual treatment for condition column
- More prominent trend arrows
- Zebra striping for readability

### Toggle UI

```
┌─────────────────────────────────────────────────────────┐
│  Search...                    [≡ Table] [▦ Cards]  ⚙️   │
└─────────────────────────────────────────────────────────┘
```

- Toggle buttons in toolbar next to search
- Preference saved to localStorage
- Overrides responsive default once user chooses

### Files

| Action | File |
|--------|------|
| Create | `src/components/streams/StreamCard.tsx` |
| Create | `src/components/streams/StreamCardGrid.tsx` |
| Create | `src/components/streams/ViewToggle.tsx` |
| Create | `src/hooks/useViewPreference.ts` |

---

## 4. Component Structure

```
App.tsx
├── GaugeDataProvider              ← NEW
│   └── ThemeProvider
│       └── BrowserRouter
│           ├── Header
│           │   └── FilterButton, ThemeToggle
│           ├── DashboardPage
│           │   ├── DashboardHeader
│           │   ├── Toolbar
│           │   │   ├── SearchField
│           │   │   └── ViewToggle        ← NEW
│           │   └── StreamGroups          ← NEW
│           │       ├── StreamGroup (Optimal)
│           │       │   ├── StreamGroupHeader
│           │       │   └── StreamCardGrid | StreamTable
│           │       ├── StreamGroup (Low)
│           │       ├── StreamGroup (High)
│           │       └── StreamGroup (Too Low)
│           ├── DashboardSidebar
│           └── Footer
```

### State Management

| State | Location | Persistence |
|-------|----------|-------------|
| Gauge readings | `GaugeDataContext` | Memory (refetched) |
| View mode | `useViewPreference` | localStorage |
| Filters (rating/size) | `App.tsx` props | None |
| Search term | `DashboardPage` | None |
| Group collapse | `StreamGroup` local | None |
| Sort field/direction | `StreamGroup` local | None |

---

## 5. Loading & Error Handling

### Initial Load

```
┌─────────────────────────────────────────────────────────┐
│  🌊 Ozark Stream Tracker                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│     Fetching gauge data...                              │
│     Loading 20 gauges from USGS                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Error Strategy

| Scenario | Behavior |
|----------|----------|
| USGS batch fails entirely | Error banner with retry button |
| Individual gauge fails | That gauge's streams show "Unavailable" |
| Turner Bend fails | Independent, doesn't affect USGS streams |
| Network offline | Show cached data if available, "Offline" indicator |

### Refresh Behavior

- Auto-refresh every 15 minutes (background, no spinner)
- Manual refresh button in header
- Last updated timestamp: "Data as of 2:45 PM"

---

## 6. Implementation Order

1. **GaugeDataContext** - Batched fetching, biggest perf win
2. **useGaugeReading hook** - Thin wrapper for components
3. **Update StreamTableRow** - Consume new hook
4. **StreamGroup components** - Grouping by condition
5. **StreamCard component** - Card layout
6. **ViewToggle + useViewPreference** - View switching
7. **Polish** - Loading states, error handling, transitions

---

## Files Summary

### Create

- `src/context/GaugeDataContext.tsx`
- `src/hooks/useGaugeReading.ts`
- `src/hooks/useViewPreference.ts`
- `src/components/streams/StreamGroup.tsx`
- `src/components/streams/StreamGroupHeader.tsx`
- `src/components/streams/StreamCard.tsx`
- `src/components/streams/StreamCardGrid.tsx`
- `src/components/streams/ViewToggle.tsx`

### Modify

- `src/App.tsx` - Wrap with GaugeDataProvider
- `src/pages/DashboardPage.tsx` - Grouping logic, toolbar
- `src/components/streams/StreamTableRow.tsx` - Use new hook
- `src/components/streams/StreamTable.tsx` - Enhanced styling

### Deprecate/Remove

- Per-row fetching logic in `src/hooks/useStreamGauge.ts`

---

## Success Criteria

- [ ] Initial load makes ≤ 3 API calls (USGS batch, Turner Bend, optional retry)
- [ ] Streams grouped by condition on load
- [ ] "Too Low" section collapsed by default
- [ ] Card view displays on mobile (< 768px)
- [ ] Table view displays on desktop (≥ 768px)
- [ ] User can toggle view preference
- [ ] View preference persists across sessions
- [ ] Partial gauge failures don't break entire app
- [ ] All existing functionality preserved (search, filter, sort, detail drawer)
