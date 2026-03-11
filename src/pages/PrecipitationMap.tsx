import { useState, useEffect, useMemo } from 'react';
import { Box, useMediaQuery, useTheme } from '@mui/material';
import 'leaflet/dist/leaflet.css';
import { MapView } from '../components/precipitation/MapView';
import { ForecastPanel } from '../components/precipitation/ForecastPanel';
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
      if (!cancelled) setIntelligenceLoading(false);
    })();

    return () => {
      cancelled = true;
    };
  }, [watersheds]);

  if (isMobile) {
    return (
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <WeatherSummaryBar
          precipData={precipData}
          forecastData={forecastData}
          loading={intelligenceLoading}
        />
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
    <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <WeatherSummaryBar
        precipData={precipData}
        forecastData={forecastData}
        loading={intelligenceLoading}
      />
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
    </Box>
  );
}
