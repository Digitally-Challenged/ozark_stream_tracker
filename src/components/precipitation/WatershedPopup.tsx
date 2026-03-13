import { Box, Typography, Chip, Skeleton } from '@mui/material';
import { WaterDrop, TrendingUp } from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import { Watershed } from '../../utils/watershedGrouping';
import { GaugeReading, LevelTrend } from '../../types/stream';
import {
  determineLevel,
  determineTrend,
  STATUS_HEX_COLORS,
  STATUS_LABELS,
} from '../../utils/streamLevels';
import { getStreamIdFromName } from '../../utils/streamIds';
import { getTrendLabel } from '../../utils/trendUtils';
import { NwsForecast } from '../../services/nwsForecastService';
import { PrecipTotals } from '../../services/precipQueryService';

interface WatershedPopupProps {
  watershed: Watershed;
  reading: GaugeReading | null;
  previousReading: GaugeReading | null;
  forecast?: NwsForecast | null;
  precip?: PrecipTotals | null;
  intelligenceLoading?: boolean;
  isDark?: boolean;
}

const TREND_COLORS: Partial<Record<LevelTrend, string>> = {
  [LevelTrend.Rising]: '#4caf50',
  [LevelTrend.Falling]: '#f44336',
  [LevelTrend.Holding]: '#ff9800',
};

export function WatershedPopup({
  watershed,
  reading,
  previousReading,
  forecast,
  precip,
  intelligenceLoading,
  isDark = true,
}: WatershedPopupProps) {
  const textPrimary = isDark ? '#fff' : '#1a1a2e';
  const textSecondary = isDark ? 'rgba(255,255,255,0.9)' : 'rgba(0,0,0,0.75)';
  const textMuted = isDark ? 'rgba(255,255,255,0.7)' : 'rgba(0,0,0,0.5)';
  const textDisabled = isDark ? 'rgba(255,255,255,0.4)' : 'rgba(0,0,0,0.35)';
  const borderColor = isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.1)';
  const trend =
    reading && previousReading
      ? determineTrend(reading, previousReading)
      : LevelTrend.None;
  const trendLabel = getTrendLabel(trend);
  const trendColor = TREND_COLORS[trend];

  return (
    <Box sx={{ minWidth: 220, maxWidth: 300, color: textPrimary }}>
      <Typography
        variant="subtitle2"
        sx={{
          fontWeight: 700,
          mb: 0.25,
          fontSize: '0.85rem',
          lineHeight: 1.3,
          color: textPrimary,
        }}
      >
        {watershed.gauge.name}
      </Typography>
      <Box
        sx={{
          height: 2,
          width: 40,
          borderRadius: 1,
          background: 'linear-gradient(90deg, #30cfd0, #330867)',
          mb: 1,
        }}
      />

      {reading ? (
        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.75, mb: 1 }}>
          <Typography
            variant="body1"
            sx={{ fontWeight: 700, fontSize: '1rem', color: textPrimary }}
          >
            {reading.value} ft
          </Typography>
          {trendLabel && (
            <Typography
              variant="caption"
              sx={{
                fontWeight: 600,
                color: trendColor,
                fontSize: '0.7rem',
              }}
            >
              {trendLabel}
            </Typography>
          )}
        </Box>
      ) : (
        <Typography
          variant="body2"
          sx={{
            mb: 1,
            color: textDisabled,
            fontStyle: 'italic',
          }}
        >
          Awaiting data...
        </Typography>
      )}

      {precip && (precip.last24h !== null || precip.last48h !== null) && (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 0.5,
            mb: 0.5,
            py: 0.5,
            px: 0.75,
            borderRadius: 1,
            background: isDark
              ? 'rgba(48, 207, 208, 0.06)'
              : 'rgba(48, 207, 208, 0.08)',
          }}
        >
          <WaterDrop sx={{ fontSize: 14, color: '#30cfd0' }} />
          <Typography
            variant="caption"
            sx={{
              fontWeight: 600,
              fontSize: '0.7rem',
              color: textSecondary,
            }}
          >
            {precip.last24h !== null && `${precip.last24h.toFixed(1)} in (24h)`}
            {precip.last24h !== null && precip.last48h !== null && ' \u00b7 '}
            {precip.last48h !== null && `${precip.last48h.toFixed(1)} in (48h)`}
          </Typography>
        </Box>
      )}
      {intelligenceLoading && !precip && (
        <Skeleton
          variant="rectangular"
          height={24}
          sx={{ borderRadius: 1, mb: 0.5 }}
        />
      )}

      {forecast?.peakForecast && (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 0.5,
            mb: 0.75,
            py: 0.5,
            px: 0.75,
            borderRadius: 1,
            background: isDark
              ? 'rgba(76, 175, 80, 0.06)'
              : 'rgba(76, 175, 80, 0.08)',
          }}
        >
          <TrendingUp sx={{ fontSize: 14, color: '#4caf50' }} />
          <Typography
            variant="caption"
            sx={{
              fontWeight: 600,
              fontSize: '0.7rem',
              color: textSecondary,
            }}
          >
            {'\u2192'} {forecast.peakForecast.stage.toFixed(1)} ft by{' '}
            {format(new Date(forecast.peakForecast.time), 'EEE')}
          </Typography>
        </Box>
      )}

      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          gap: 0.25,
        }}
      >
        {watershed.streams.map((stream) => {
          const status = reading
            ? determineLevel(reading.value, stream.targetLevels)
            : null;
          const streamId = getStreamIdFromName(stream.name);

          return (
            <Box
              key={stream.name}
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                py: 0.5,
                px: 0.75,
                borderRadius: 1,
                transition: 'background 0.2s',
                '&:hover': {
                  background: 'rgba(48, 207, 208, 0.08)',
                },
              }}
            >
              {streamId ? (
                <Link
                  to={`/stream/${streamId}`}
                  style={{
                    color: textSecondary,
                    textDecoration: 'none',
                    fontSize: '0.78rem',
                    fontWeight: 500,
                    transition: 'color 0.2s',
                  }}
                  onMouseEnter={(e) =>
                    (e.currentTarget.style.color = '#30cfd0')
                  }
                  onMouseLeave={(e) =>
                    (e.currentTarget.style.color = textSecondary)
                  }
                >
                  {stream.name}
                </Link>
              ) : (
                <Typography
                  variant="caption"
                  sx={{ fontWeight: 500, color: textSecondary }}
                >
                  {stream.name}
                </Typography>
              )}
              {status && (
                <Chip
                  label={STATUS_LABELS[status]}
                  size="small"
                  sx={{
                    height: 20,
                    fontSize: '0.6rem',
                    fontWeight: 700,
                    letterSpacing: '0.03em',
                    bgcolor: STATUS_HEX_COLORS[status],
                    color: '#fff',
                    boxShadow: `0 0 8px ${STATUS_HEX_COLORS[status]}66`,
                  }}
                />
              )}
            </Box>
          );
        })}
      </Box>

      <Link
        to={`/precipitation/watershed/${watershed.gauge.id}`}
        style={{
          display: 'block',
          marginTop: 8,
          paddingTop: 6,
          borderTop: `1px solid ${borderColor}`,
          textAlign: 'center',
          textDecoration: 'none',
          transition: 'color 0.2s',
        }}
      >
        <Typography
          variant="caption"
          sx={{
            fontWeight: 600,
            fontSize: '0.7rem',
            letterSpacing: '0.03em',
            color: textMuted,
            '&:hover': { color: '#30cfd0' },
          }}
        >
          View Watershed Forecast {'\u2192'}
        </Typography>
      </Link>
    </Box>
  );
}
