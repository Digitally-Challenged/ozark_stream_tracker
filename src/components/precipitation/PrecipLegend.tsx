import { Box, Typography, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { glassmorphism } from '../../theme/waterTheme';
import type { PrecipLayer } from './LayerControl';

const PRECIP_SCALE = [
  { color: '#00ff00', label: '0.1' },
  { color: '#00c800', label: '0.25' },
  { color: '#ffff00', label: '0.5' },
  { color: '#ffc800', label: '1.0' },
  { color: '#ff6400', label: '2.0' },
  { color: '#ff0000', label: '3.0' },
  { color: '#c80000', label: '5.0+' },
];

interface PrecipLegendProps {
  activeLayer: PrecipLayer;
}

export function PrecipLegend({ activeLayer }: PrecipLegendProps) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const glass = isDark ? glassmorphism.dark : glassmorphism.light;

  if (activeLayer === 'radar') return null;

  return (
    <Box
      sx={{
        position: 'absolute',
        bottom: 64,
        left: 16,
        zIndex: 1000,
        ...glass,
        borderRadius: 1.5,
        p: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: 0.5,
      }}
    >
      <Typography
        variant="caption"
        sx={{
          fontSize: '0.6rem',
          fontWeight: 700,
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          color: isDark ? alpha('#fff', 0.6) : alpha('#000', 0.5),
        }}
      >
        Rainfall (inches)
      </Typography>
      <Box sx={{ display: 'flex', gap: 0 }}>
        {PRECIP_SCALE.map((s) => (
          <Box key={s.label} sx={{ textAlign: 'center' }}>
            <Box
              sx={{
                width: 24,
                height: 8,
                bgcolor: s.color,
                borderRadius: 0,
                '&:first-of-type': {
                  borderTopLeftRadius: 2,
                  borderBottomLeftRadius: 2,
                },
                '&:last-of-type': {
                  borderTopRightRadius: 2,
                  borderBottomRightRadius: 2,
                },
              }}
            />
            <Typography
              variant="caption"
              sx={{
                fontSize: '0.5rem',
                color: isDark ? alpha('#fff', 0.5) : alpha('#000', 0.4),
                lineHeight: 1.6,
              }}
            >
              {s.label}
            </Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );
}
