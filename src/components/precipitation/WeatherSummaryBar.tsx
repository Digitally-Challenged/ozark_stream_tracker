import { Box, Typography, Skeleton, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { WaterDrop, TrendingUp } from '@mui/icons-material';
import { glassmorphism } from '../../theme/waterTheme';
import { PrecipTotals } from '../../services/precipQueryService';
import { NwsForecast } from '../../services/nwsForecastService';

interface WeatherSummaryBarProps {
  precipData: Map<string, PrecipTotals>;
  forecastData: Map<string, NwsForecast>;
  loading: boolean;
}

export function WeatherSummaryBar({
  precipData,
  forecastData,
  loading,
}: WeatherSummaryBarProps) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const glass = isDark ? glassmorphism.dark : glassmorphism.light;

  const rainyCount = Array.from(precipData.values()).filter(
    (p) => p.last24h !== null && p.last24h > 0.1
  ).length;

  const risingCount = Array.from(forecastData.values()).filter((f) => {
    if (!f.data || f.data.length < 2) return false;
    const last = f.data[f.data.length - 1];
    const first = f.data[0];
    return last.stage > first.stage + 0.1;
  }).length;

  if (loading && precipData.size === 0) {
    return (
      <Box sx={{ px: 2, py: 1, ...glass, borderRadius: 0 }}>
        <Skeleton width={300} height={20} />
      </Box>
    );
  }

  if (rainyCount === 0 && risingCount === 0) return null;

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 3,
        px: 2,
        py: 1,
        ...glass,
        borderRadius: 0,
        borderBottom: `1px solid ${alpha(isDark ? '#30cfd0' : '#000', 0.1)}`,
      }}
    >
      {rainyCount > 0 && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
          <WaterDrop sx={{ fontSize: 16, color: '#30cfd0' }} />
          <Typography
            variant="caption"
            sx={{ fontWeight: 600, fontSize: '0.75rem' }}
          >
            {rainyCount} watershed{rainyCount !== 1 ? 's' : ''} got rain (24h)
          </Typography>
        </Box>
      )}
      {risingCount > 0 && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
          <TrendingUp sx={{ fontSize: 16, color: '#4caf50' }} />
          <Typography
            variant="caption"
            sx={{ fontWeight: 600, fontSize: '0.75rem' }}
          >
            {risingCount} gauge{risingCount !== 1 ? 's' : ''} forecast rising
          </Typography>
        </Box>
      )}
    </Box>
  );
}
