import { useState, useMemo } from 'react';
import { Box, useMediaQuery, useTheme } from '@mui/material';
import 'leaflet/dist/leaflet.css';
import { MapView } from '../components/precipitation/MapView';
import { ForecastPanel } from '../components/precipitation/ForecastPanel';
import { groupStreamsByWatershed } from '../utils/watershedGrouping';
import { streams } from '../data/streamData';
import type { PrecipLayer } from '../components/precipitation/LayerControl';

export default function PrecipitationMap() {
  const [activeLayer, setActiveLayer] = useState<PrecipLayer>('24h');
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const watersheds = useMemo(() => groupStreamsByWatershed(streams), []);

  if (isMobile) {
    return (
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
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
  );
}
