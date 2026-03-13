import { useState, useEffect, useMemo, useCallback } from 'react';
import { Box, useMediaQuery, useTheme, Fab } from '@mui/material';
import { Cloud } from '@mui/icons-material';
import 'leaflet/dist/leaflet.css';
import { MapView } from '../components/precipitation/MapView';
import { ForecastPanel } from '../components/precipitation/ForecastPanel';
import { ForecastDrawer } from '../components/precipitation/ForecastDrawer';
import { WeatherSummaryBar } from '../components/precipitation/WeatherSummaryBar';
import { groupStreamsByWatershed } from '../utils/watershedGrouping';
import { streams } from '../data/streamData';
import { GAUGE_LOCATIONS } from '../data/gaugeLocations';
import { fetchNwsForecast, NwsForecast } from '../services/nwsForecastService';
import {
  fetchPrecipTotals,
  PrecipTotals,
} from '../services/precipQueryService';
import type { PrecipLayer } from '../components/precipitation/LayerControl';

export default function PrecipitationMap() {
  const [activeLayer, setActiveLayer] = useState<PrecipLayer>('24h');
  const [precipData, setPrecipData] = useState<Map<string, PrecipTotals>>(
    new Map()
  );
  const [forecastData, setForecastData] = useState<Map<string, NwsForecast>>(
    new Map()
  );
  const [intelligenceLoading, setIntelligenceLoading] = useState(true);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [lastFetched, setLastFetched] = useState<Date | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [highlightedGauges, setHighlightedGauges] =
    useState<Set<string> | null>(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const watersheds = useMemo(() => groupStreamsByWatershed(streams), []);

  useEffect(() => {
    let cancelled = false;
    setIntelligenceLoading(true);
    const entries = Array.from(watersheds.entries());

    (async () => {
      for (const [gaugeId] of entries) {
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

        // Stagger requests to avoid hammering APIs
        await new Promise((r) => setTimeout(r, 100));
      }
      if (!cancelled) {
        setIntelligenceLoading(false);
        setLastFetched(new Date());
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [watersheds, refreshKey]);

  const refreshIntelligence = useCallback(() => {
    for (const [gaugeId] of watersheds) {
      localStorage.removeItem(`nws-forecast-${gaugeId}`);
      localStorage.removeItem(`precip-${gaugeId}`);
    }
    setPrecipData(new Map());
    setForecastData(new Map());
    setRefreshKey((k) => k + 1);
  }, [watersheds]);

  const rainyGaugeIds = useMemo(() => {
    const ids = new Set<string>();
    for (const [gaugeId, p] of precipData) {
      if (p.last24h !== null && p.last24h > 0.1) ids.add(gaugeId);
    }
    return ids;
  }, [precipData]);

  const risingGaugeIds = useMemo(() => {
    const ids = new Set<string>();
    for (const [gaugeId, f] of forecastData) {
      if (f.data && f.data.length >= 2) {
        const last = f.data[f.data.length - 1];
        const first = f.data[0];
        if (last.stage > first.stage + 0.1) ids.add(gaugeId);
      }
    }
    return ids;
  }, [forecastData]);

  const handleHighlightRainy = () => {
    setHighlightedGauges((prev) =>
      prev && [...prev].every((id) => rainyGaugeIds.has(id))
        ? null
        : rainyGaugeIds
    );
  };

  const handleHighlightRising = () => {
    setHighlightedGauges((prev) =>
      prev && [...prev].every((id) => risingGaugeIds.has(id))
        ? null
        : risingGaugeIds
    );
  };

  if (isMobile) {
    return (
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
        }}
      >
        <WeatherSummaryBar
          precipData={precipData}
          forecastData={forecastData}
          loading={intelligenceLoading}
          lastFetched={lastFetched}
          onRefresh={refreshIntelligence}
          onHighlightRainy={handleHighlightRainy}
          onHighlightRising={handleHighlightRising}
          highlightActive={highlightedGauges !== null}
        />
        <Box sx={{ flex: 1 }}>
          <MapView
            watersheds={watersheds}
            activeLayer={activeLayer}
            onLayerChange={setActiveLayer}
            precipData={precipData}
            forecastData={forecastData}
            intelligenceLoading={intelligenceLoading}
            highlightedGauges={highlightedGauges}
          />
        </Box>
        <Fab
          size="small"
          onClick={() => setDrawerOpen(true)}
          aria-label="open forecast"
          sx={{
            position: 'absolute',
            bottom: 16,
            right: 16,
            zIndex: 1000,
            background: 'linear-gradient(135deg, #30cfd0, #330867)',
            color: '#fff',
            boxShadow: '0 4px 14px rgba(48, 207, 208, 0.4)',
            '&:hover': {
              background: 'linear-gradient(135deg, #30cfd0, #330867)',
              boxShadow: '0 6px 20px rgba(48, 207, 208, 0.5)',
            },
          }}
        >
          <Cloud />
        </Fab>
        <ForecastDrawer
          open={drawerOpen}
          onOpen={() => setDrawerOpen(true)}
          onClose={() => setDrawerOpen(false)}
        />
      </Box>
    );
  }

  return (
    <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <WeatherSummaryBar
        precipData={precipData}
        forecastData={forecastData}
        loading={intelligenceLoading}
        lastFetched={lastFetched}
        onRefresh={refreshIntelligence}
        onHighlightRainy={handleHighlightRainy}
        onHighlightRising={handleHighlightRising}
        highlightActive={highlightedGauges !== null}
      />
      <Box sx={{ flex: 1, display: 'flex' }}>
        <Box sx={{ flex: 1 }}>
          <MapView
            watersheds={watersheds}
            activeLayer={activeLayer}
            onLayerChange={setActiveLayer}
            precipData={precipData}
            forecastData={forecastData}
            intelligenceLoading={intelligenceLoading}
            highlightedGauges={highlightedGauges}
          />
        </Box>
        <Box sx={{ width: 350, flexShrink: 0 }}>
          <ForecastPanel />
        </Box>
      </Box>
    </Box>
  );
}
