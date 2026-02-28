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
2. **Turner Bend**: Custom gauge scraped via Netlify Function (`netlify/functions/turner-bend.js`) to avoid CORS, cached 15 minutes in-memory (warm invocations only)

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
- `server/turnerBendScraper.js`: Local dev scraper for Turner Bend gauge (Express server)
- `netlify/functions/turner-bend.js`: Production Netlify Function scraper for Turner Bend gauge

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

1. `npm run build` executes three steps:
   - `npm run parse-streams` (scripts/parse-streams.ts) → generates `src/data/streamContent.generated.ts`
   - `vite build` with code splitting (react-vendor, mui-vendor, date-vendor chunks)
   - `cd netlify/functions && npm install` → installs function dependencies (cheerio) during Netlify build

**TypeScript:** Strict mode enabled with `noUnusedLocals` and `noUnusedParameters`

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
