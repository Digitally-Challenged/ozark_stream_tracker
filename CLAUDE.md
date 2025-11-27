# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ozark Stream Tracker is a React/TypeScript application for monitoring real-time water levels on Arkansas and Oklahoma whitewater streams. It displays USGS gauge data with paddling condition indicators.

## Commands

```bash
# Development
npm run dev          # Start Vite dev server (port 5173)
npm run build        # Production build to dist/
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

### Key Patterns

**Stream Data Model** (`src/types/stream.ts`):
- `StreamData`: Core stream info with gauge reference and target levels
- `LevelStatus`: X (too low), L (low), O (optimal), H (high)
- `LevelTrend`: rise, fall, hold, none

**Gauge Hook** (`src/hooks/useStreamGauge.ts`):
- Single source of truth for fetching gauge readings
- Special-cases `TURNER_BEND` gauge ID to use backend scraper
- Compares current vs previous reading for trend calculation
- Auto-refreshes every 15 minutes (`API_CONFIG.REFRESH_INTERVAL_MS`)

**Filtering System**:
- State managed in `App.tsx`, passed down via props
- Sidebar drawer (`DashboardSidebar`) controls rating/size filters
- Stream table filters in `DashboardPage`

### Important Files

- `src/data/streamData.ts`: Static stream definitions (90+ streams with gauge mappings)
- `src/constants/index.ts`: API URLs, refresh intervals, level thresholds
- `src/utils/streamLevels.ts`: Level/trend calculation logic
- `server/turnerBendScraper.js`: Backend scraper for Turner Bend gauge

### Environment Variables

- `VITE_API_URL`: Turner Bend API endpoint (defaults to `http://localhost:3001/api/turner-bend/current`)

## Frontend/Backend Split

The frontend is a Vite SPA deployed to Netlify. The backend is a minimal Express server that scrapes Turner Bend's website to get water levels not available via USGS. These are separate deployments - the frontend can run without the backend (Turner Bend will show errors).
