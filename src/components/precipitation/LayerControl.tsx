import {
  ToggleButtonGroup,
  ToggleButton,
  Box,
  Tooltip,
  useTheme,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import { Radar, WaterDrop } from '@mui/icons-material';
import { glassmorphism } from '../../theme/waterTheme';

export type PrecipLayer = 'radar' | '24h' | '48h' | '72h';

interface LayerControlProps {
  activeLayer: PrecipLayer;
  onChange: (layer: PrecipLayer) => void;
}

export function LayerControl({ activeLayer, onChange }: LayerControlProps) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const glass = isDark ? glassmorphism.dark : glassmorphism.light;

  return (
    <Box
      sx={{
        position: 'absolute',
        bottom: 16,
        left: 16,
        zIndex: 1000,
        borderRadius: 2,
        ...glass,
        p: 0.5,
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
        sx={{
          '& .MuiToggleButton-root': {
            border: 'none',
            borderRadius: '8px !important',
            px: 1.5,
            py: 0.75,
            fontSize: '0.8rem',
            fontWeight: 600,
            letterSpacing: '0.02em',
            color: isDark ? alpha('#fff', 0.7) : alpha('#000', 0.6),
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              background: isDark ? alpha('#fff', 0.1) : alpha('#000', 0.05),
            },
            '&.Mui-selected': {
              background: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
              color: '#fff',
              boxShadow: '0 0 12px rgba(48, 207, 208, 0.4)',
              '&:hover': {
                background: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
              },
            },
          },
        }}
      >
        <Tooltip title="Live NEXRAD radar" placement="top" arrow>
          <ToggleButton value="radar" aria-label="live radar">
            <Radar sx={{ mr: 0.5, fontSize: 18 }} />
            Radar
          </ToggleButton>
        </Tooltip>
        <Tooltip
          title="Accumulated rainfall — last 24 hours"
          placement="top"
          arrow
        >
          <ToggleButton value="24h" aria-label="24 hour precipitation">
            <WaterDrop sx={{ mr: 0.5, fontSize: 18 }} />
            24h
          </ToggleButton>
        </Tooltip>
        <Tooltip
          title="Accumulated rainfall — last 48 hours"
          placement="top"
          arrow
        >
          <ToggleButton value="48h" aria-label="48 hour precipitation">
            48h
          </ToggleButton>
        </Tooltip>
        <Tooltip
          title="Accumulated rainfall — last 72 hours"
          placement="top"
          arrow
        >
          <ToggleButton value="72h" aria-label="72 hour precipitation">
            72h
          </ToggleButton>
        </Tooltip>
      </ToggleButtonGroup>
    </Box>
  );
}
