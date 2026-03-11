import { useMemo } from 'react';
import { Box, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import type { PrecipLayer } from './LayerControl';
import { LayerControl } from './LayerControl';
import { WatershedPopup } from './WatershedPopup';
import { Watershed } from '../../utils/watershedGrouping';
import { getWatershedMarkerColor } from '../../utils/watershedGrouping';
import { GAUGE_LOCATIONS } from '../../data/gaugeLocations';
import { useGaugeDataContext } from '../../context/GaugeDataContext';
import { determineLevel } from '../../utils/streamLevels';
import { LevelStatus } from '../../types/stream';

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

const BASE_TILES = {
  light: {
    url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
  },
  dark: {
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
  },
};

const OZARK_CENTER: [number, number] = [35.5, -93.5];
const DEFAULT_ZOOM = 8;

interface MapViewProps {
  watersheds: Map<string, Watershed>;
  activeLayer: PrecipLayer;
  onLayerChange: (layer: PrecipLayer) => void;
}

export function MapView({
  watersheds,
  activeLayer,
  onLayerChange,
}: MapViewProps) {
  const { gauges } = useGaugeDataContext();
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const baseTile = isDark ? BASE_TILES.dark : BASE_TILES.light;

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
        <TileLayer
          key={isDark ? 'dark' : 'light'}
          url={baseTile.url}
          attribution={baseTile.attribution}
        />

        <TileLayer
          key={activeLayer}
          url={tileUrl}
          attribution={LAYER_ATTR}
          opacity={0.6}
        />

        {markers.map((marker) => {
          const gaugeData = gauges.get(marker.gaugeId);
          return (
            <CircleMarker
              key={marker.gaugeId}
              center={[marker.lat, marker.lng]}
              radius={12}
              pathOptions={{
                fillColor: marker.color,
                color: '#fff',
                weight: 2.5,
                fillOpacity: 0.9,
                className: 'watershed-marker',
              }}
            >
              <Popup>
                <WatershedPopup
                  watershed={marker.watershed}
                  reading={gaugeData?.reading ?? null}
                  previousReading={gaugeData?.previousReading ?? null}
                />
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>

      <LayerControl activeLayer={activeLayer} onChange={onLayerChange} />
    </Box>
  );
}
