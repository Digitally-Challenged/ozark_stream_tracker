# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ozark Stream Tracker is a React/TypeScript application for monitoring real-time water levels on Arkansas and Oklahoma whitewater streams. It displays USGS gauge data with paddling condition indicators.

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
2. **Turner Bend**: Custom gauge scraped via backend (`server/`) to avoid CORS, cached 15 minutes

### Component Architecture

**Styling & Theming:**

- Material-UI sx prop exclusively (no CSS modules or Tailwind)
- Dark/light modes with theme-aware colors from ThemeContext
- Gradients and animations from `src/theme/waterTheme.ts`
- Responsive design via MUI Grid and breakpoints (xs, sm, md, lg, xl)

**Component Structure:**

```
src/components/
├── badges/       # RatingBadge, SizeBadge
├── common/       # LiveTime, utilities
├── core/         # Header, Footer
├── dashboard/    # DashboardHeader, DashboardSidebar
├── effects/      # GlassCard visual effects
├── icons/        # StreamConditionIcon, TrendIcon
├── stream-page/  # Stream detail page components
└── streams/      # StreamCard, StreamTable, StreamGroup, etc.
```

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

**Gauge Hook** (`src/hooks/useStreamGauge.ts`):

- Single source of truth for fetching gauge readings
- Special-cases `TURNER_BEND` gauge ID to use backend scraper
- Compares current vs previous reading for trend calculation
- Auto-refreshes every 15 minutes (`API_CONFIG.REFRESH_INTERVAL_MS`)

**Filtering System:**

- State managed in `App.tsx`, passed down via props
- Sidebar drawer (`DashboardSidebar`) controls rating/size filters
- Stream table filters in `DashboardPage`

### Important Files

- `src/data/streamData.ts`: Static stream definitions (90+ streams with gauge mappings)
- `src/data/streamContent.generated.ts`: Auto-generated from markdown (via parse-streams)
- `src/constants/index.ts`: API URLs, refresh intervals, level thresholds
- `src/utils/streamLevels.ts`: Level/trend calculation logic
- `src/utils/streamIds.ts`: Explicit stream name to content ID mapping
- `server/turnerBendScraper.js`: Backend scraper for Turner Bend gauge

### Storage Strategy

**localStorage Keys:**

- `ozark-stream-tracker-theme`: Dark/light mode preference
- `ozark-stream-tracker-view-mode`: Table vs cards preference
- `gauge-reading-history`: 24-hour rolling gauge history for trends
- `turner-bend-gauge-data`: 15-minute client-side cache for Turner Bend

### Environment Variables

- `VITE_API_URL`: Turner Bend API endpoint (defaults to `http://localhost:3001/api/turner-bend/current`)

## Build & Configuration

**Build Pipeline:**

1. `npm run build` executes two steps:
   - `npm run parse-streams` (scripts/parse-streams.ts) → generates `src/data/streamContent.generated.ts`
   - `vite build` with code splitting (react-vendor, mui-vendor, date-vendor chunks)

**TypeScript:** Strict mode enabled with `noUnusedLocals` and `noUnusedParameters`

**Key Constants** (`src/constants/index.ts`):

- USGS refresh: 15 minutes
- Level freshness: 1.5h (very fresh), 3h (fresh), 10h (recent)
- Change threshold: 0.1ft for trend detection

## Backend Server

The Turner Bend scraper is a separate Express server (`server/`) that:

1. Scrapes Turner Bend's website (CORS-free alternative to client-side)
2. Caches data locally with 30-day rolling history
3. Refreshes every 4 hours via cron schedule

**API Endpoints:**

- `GET /api/turner-bend/current` - Get latest water level (cached)
- `POST /api/turner-bend/scrape` - Force immediate scrape
- `GET /health` - Health check

**Data Storage:**

- Cached in `server/turner-bend-data.json`
- 30-day rolling window, auto-regenerates on scrape

**Known Limitations:**

- Scraping relies on regex patterns - breaks if Turner Bend website HTML changes
- No retry logic for failed scrapes - depends on 4-hour refresh cycle
- CORS origins hardcoded in `server.js` - update for new deployment domains

## Frontend/Backend Split

The frontend is a Vite SPA deployed to Netlify. The backend is a minimal Express server that scrapes Turner Bend's website to get water levels not available via USGS. These are separate deployments - the frontend can run without the backend (Turner Bend will show errors).
