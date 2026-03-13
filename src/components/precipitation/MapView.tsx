import { useMemo } from 'react';
import { Box, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import type { PrecipLayer } from './LayerControl';
import { LayerControl } from './LayerControl';
import { PrecipLegend } from './PrecipLegend';
import { WatershedPopup } from './WatershedPopup';
import { Watershed } from '../../utils/watershedGrouping';
import { getWatershedMarkerColor } from '../../utils/watershedGrouping';
import { GAUGE_LOCATIONS } from '../../data/gaugeLocations';
import { useGaugeDataContext } from '../../context/GaugeDataContext';
import { determineLevel } from '../../utils/streamLevels';
import { LevelStatus, GaugeReading } from '../../types/stream';
import { NwsForecast } from '../../services/nwsForecastService';
import { PrecipTotals } from '../../services/precipQueryService';

const IEM_TILE_URL =
  'https://mesonet.agron.iastate.edu/cache/tile.py/1.0.0/{layer}/{z}/{x}/{y}.png';

const LAYER_IDS: Record<PrecipLayer, string> = {
  radar: 'nexrad-n0q-900913',
  '24h': 'q2-p24h',
  '48h': 'q2-p48h',
  '72h': 'q2-p72h',
};

const LAYER_ATTR =
  'Weather data &copy; <a href="https://mesonet.agron.iastate.edu/">Iowa Environmental Mesonet</a>';

const CARTO_ATTR =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>';

const BASE_TILES = {
  light: {
    base: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png',
    labels:
      'https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png',
  },
  dark: {
    base: 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png',
    labels:
      'https://{s}.basemaps.cartocdn.com/dark_only_labels/{z}/{x}/{y}{r}.png',
  },
};

const OZARK_CENTER: [number, number] = [35.5, -93.5];
const DEFAULT_ZOOM = 8;

function WatershedMarker({
  marker,
  gaugeData,
  isDark,
  forecast,
  precip,
  intelligenceLoading,
  highlightedGauges,
}: {
  marker: {
    gaugeId: string;
    lat: number;
    lng: number;
    color: string;
    watershed: Watershed;
  };
  gaugeData:
    | { reading: GaugeReading | null; previousReading: GaugeReading | null }
    | undefined;
  isDark: boolean;
  forecast: NwsForecast | null;
  precip: PrecipTotals | null;
  intelligenceLoading: boolean;
  highlightedGauges?: Set<string> | null;
}) {
  return (
    <CircleMarker
      center={[marker.lat, marker.lng]}
      radius={12}
      pathOptions={{
        fillColor: marker.color,
        color: '#fff',
        weight: 2.5,
        fillOpacity:
          highlightedGauges && !highlightedGauges.has(marker.gaugeId)
            ? 0.25
            : 0.9,
        className: 'watershed-marker',
      }}
    >
      <Popup>
        <WatershedPopup
          watershed={marker.watershed}
          reading={gaugeData?.reading ?? null}
          previousReading={gaugeData?.previousReading ?? null}
          forecast={forecast}
          precip={precip}
          intelligenceLoading={intelligenceLoading}
          isDark={isDark}
        />
      </Popup>
    </CircleMarker>
  );
}

interface MapViewProps {
  watersheds: Map<string, Watershed>;
  activeLayer: PrecipLayer;
  onLayerChange: (layer: PrecipLayer) => void;
  precipData: Map<string, PrecipTotals>;
  forecastData: Map<string, NwsForecast>;
  intelligenceLoading: boolean;
  highlightedGauges?: Set<string> | null;
}

export function MapView({
  watersheds,
  activeLayer,
  onLayerChange,
  precipData,
  forecastData,
  intelligenceLoading,
  highlightedGauges,
}: MapViewProps) {
  const { gauges } = useGaugeDataContext();
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const tiles = isDark ? BASE_TILES.dark : BASE_TILES.light;

  const markers = useMemo(() => {
    const result: Array<{
      gaugeId: string;
      lat: number;
      lng: number;
      color: string;
      watershed: Watershed;
    }> = [];

    for (const [gaugeId, watershed] of watersheds) {
      const location = GAUGE_LOCATIONS[gaugeId];
      if (!location) continue;

      const gaugeData = gauges.get(gaugeId);
      const reading = gaugeData?.reading ?? null;

      const statuses: LevelStatus[] = reading
        ? watershed.streams.map((s) =>
            determineLevel(reading.value, s.targetLevels)
          )
        : [];

      result.push({
        gaugeId,
        lat: location.lat,
        lng: location.lng,
        color: getWatershedMarkerColor(statuses),
        watershed,
      });
    }

    return result;
  }, [watersheds, gauges]);

  const tileUrl = IEM_TILE_URL.replace('{layer}', LAYER_IDS[activeLayer]);

  return (
    <Box
      sx={{
        position: 'relative',
        width: '100%',
        height: '100%',
        boxShadow: `inset 0 0 20px ${alpha('#000', isDark ? 0.3 : 0.1)}`,
        '& .leaflet-popup-content-wrapper': {
          borderRadius: '12px',
          boxShadow: `0 8px 32px ${alpha('#000', 0.25)}`,
          border: isDark
            ? `1px solid ${alpha('#fff', 0.1)}`
            : `1px solid ${alpha('#000', 0.08)}`,
          background: isDark ? alpha('#1a1a2e', 0.95) : alpha('#fff', 0.95),
          backdropFilter: 'blur(10px)',
        },
        '& .leaflet-popup-tip': {
          background: isDark ? '#1a1a2e' : '#fff',
        },
      }}
    >
      <MapContainer
        center={OZARK_CENTER}
        zoom={DEFAULT_ZOOM}
        style={{ width: '100%', height: '100%' }}
        zoomControl={true}
      >
        {/* Layer 1: Base map without labels */}
        <TileLayer
          key={isDark ? 'dark-base' : 'light-base'}
          url={tiles.base}
          attribution={CARTO_ATTR}
        />

        {/* Layer 2: Precipitation overlay */}
        <TileLayer
          key={activeLayer}
          url={tileUrl}
          attribution={LAYER_ATTR}
          opacity={0.35}
        />

        {/* Layer 3: Labels on top so they're never obscured */}
        <TileLayer
          key={isDark ? 'dark-labels' : 'light-labels'}
          url={tiles.labels}
          zIndex={650}
        />

        {markers.map((marker) => {
          const gaugeData = gauges.get(marker.gaugeId);
          return (
            <WatershedMarker
              key={marker.gaugeId}
              marker={marker}
              gaugeData={gaugeData}
              isDark={isDark}
              forecast={forecastData.get(marker.gaugeId) ?? null}
              precip={precipData.get(marker.gaugeId) ?? null}
              intelligenceLoading={intelligenceLoading}
              highlightedGauges={highlightedGauges}
            />
          );
        })}
      </MapContainer>

      <LayerControl activeLayer={activeLayer} onChange={onLayerChange} />
      <PrecipLegend activeLayer={activeLayer} />
    </Box>
  );
}
