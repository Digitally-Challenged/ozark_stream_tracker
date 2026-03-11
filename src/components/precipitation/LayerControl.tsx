import { ToggleButtonGroup, ToggleButton, Paper } from '@mui/material';
import { Radar, WaterDrop } from '@mui/icons-material';

export type PrecipLayer = 'radar' | '24h' | '48h' | '72h';

interface LayerControlProps {
  activeLayer: PrecipLayer;
  onChange: (layer: PrecipLayer) => void;
}

export function LayerControl({ activeLayer, onChange }: LayerControlProps) {
  return (
    <Paper
      elevation={3}
      sx={{
        position: 'absolute',
        bottom: 16,
        left: 16,
        zIndex: 1000,
        borderRadius: 2,
      }}
    >
      <ToggleButtonGroup
        value={activeLayer}
        exclusive
        onChange={(_, value) => {
          if (value !== null) onChange(value as PrecipLayer);
        }}
        size="small"
        aria-label="precipitation layer"
      >
        <ToggleButton value="radar" aria-label="live radar">
          <Radar sx={{ mr: 0.5, fontSize: 18 }} />
          Radar
        </ToggleButton>
        <ToggleButton value="24h" aria-label="24 hour precipitation">
          <WaterDrop sx={{ mr: 0.5, fontSize: 18 }} />
          24h
        </ToggleButton>
        <ToggleButton value="48h" aria-label="48 hour precipitation">
          48h
        </ToggleButton>
        <ToggleButton value="72h" aria-label="72 hour precipitation">
          72h
        </ToggleButton>
      </ToggleButtonGroup>
    </Paper>
  );
}
