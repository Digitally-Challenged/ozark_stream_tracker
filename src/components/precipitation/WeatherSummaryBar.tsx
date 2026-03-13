import { Box, Typography, Skeleton, IconButton, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { WaterDrop, TrendingUp, Refresh } from '@mui/icons-material';
import { glassmorphism } from '../../theme/waterTheme';
import { PrecipTotals } from '../../services/precipQueryService';
import { NwsForecast } from '../../services/nwsForecastService';

function getRelativeTime(date: Date): string {
  const mins = Math.round((Date.now() - date.getTime()) / 60000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  return `${Math.round(mins / 60)}h ago`;
}

interface WeatherSummaryBarProps {
  precipData: Map<string, PrecipTotals>;
  forecastData: Map<string, NwsForecast>;
  loading: boolean;
  lastFetched: Date | null;
  onRefresh?: () => void;
  onHighlightRainy?: () => void;
  onHighlightRising?: () => void;
}

export function WeatherSummaryBar({
  precipData,
  forecastData,
  loading,
  lastFetched,
  onRefresh,
  onHighlightRainy,
  onHighlightRising,
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

  const allClear = rainyCount === 0 && risingCount === 0 && !loading;

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 2,
        px: 2,
        py: 1,
        ...glass,
        borderRadius: 0,
        borderBottom: `1px solid ${alpha(isDark ? '#30cfd0' : '#000', 0.1)}`,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
        {allClear && (
          <Typography
            variant="caption"
            sx={{
              fontWeight: 600,
              fontSize: '0.75rem',
              color: 'text.secondary',
            }}
          >
            All clear — no recent rain or rising forecasts
          </Typography>
        )}
        {rainyCount > 0 && (
          <Box
            onClick={onHighlightRainy}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.75,
              cursor: onHighlightRainy ? 'pointer' : 'default',
              px: 1,
              py: 0.25,
              borderRadius: 1,
              transition: 'background 0.2s',
              '&:hover': onHighlightRainy
                ? { bgcolor: alpha('#30cfd0', 0.1) }
                : {},
            }}
          >
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
          <Box
            onClick={onHighlightRising}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.75,
              cursor: onHighlightRising ? 'pointer' : 'default',
              px: 1,
              py: 0.25,
              borderRadius: 1,
              transition: 'background 0.2s',
              '&:hover': onHighlightRising
                ? { bgcolor: alpha('#4caf50', 0.1) }
                : {},
            }}
          >
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
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {lastFetched && (
          <Typography
            variant="caption"
            sx={{
              color: 'text.disabled',
              fontSize: '0.65rem',
              whiteSpace: 'nowrap',
            }}
          >
            {getRelativeTime(lastFetched)}
          </Typography>
        )}
        {onRefresh && (
          <IconButton
            onClick={onRefresh}
            size="small"
            disabled={loading}
            sx={{ p: 0.5 }}
          >
            <Refresh sx={{ fontSize: 14, color: 'text.secondary' }} />
          </IconButton>
        )}
      </Box>
    </Box>
  );
}
