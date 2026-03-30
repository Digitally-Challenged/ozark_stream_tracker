import { useMemo } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Box,
  Typography,
  Chip,
  CircularProgress,
  IconButton,
} from '@mui/material';
import { ArrowBack, WaterDrop } from '@mui/icons-material';
import { alpha } from '@mui/material/styles';
import { GlassCard } from '../components/effects/GlassCard';
import { StageChart } from '../components/precipitation/StageChart';
import { LevelRangeBar } from '../components/precipitation/LevelRangeBar';
import { useWatershedIntelligence } from '../hooks/useWatershedIntelligence';
import { useGaugeDataContext } from '../context/GaugeDataContext';
import { GAUGE_LOCATIONS } from '../data/gaugeLocations';
import { streams } from '../data/streamData';
import { groupStreamsByWatershed } from '../utils/watershedGrouping';
import {
  determineLevel,
  determineTrend,
  STATUS_HEX_COLORS,
  STATUS_LABELS,
} from '../utils/streamLevels';
import { LevelStatus, LevelTrend } from '../types/stream';
import { getTrendLabel, getTrendMuiColor } from '../utils/trendUtils';
import { getStreamIdFromName } from '../utils/streamIds';

export default function WatershedDetailPage() {
  const { gaugeId } = useParams<{ gaugeId: string }>();
  const navigate = useNavigate();
  const location = GAUGE_LOCATIONS[gaugeId ?? ''];
  const { forecast, precip, loading } = useWatershedIntelligence(
    gaugeId ?? null,
    location?.lat ?? null,
    location?.lng ?? null
  );
  const { gauges } = useGaugeDataContext();
  const gaugeData = gauges.get(gaugeId ?? '');
  const reading = gaugeData?.reading ?? null;
  const previousReading = gaugeData?.previousReading ?? null;

  const watersheds = useMemo(() => groupStreamsByWatershed(streams), []);
  const watershed = gaugeId ? watersheds.get(gaugeId) : undefined;

  const trend =
    reading && previousReading
      ? determineTrend(reading, previousReading)
      : LevelTrend.None;
  const trendLabel = getTrendLabel(trend);
  const trendColor = getTrendMuiColor(trend);

  const highestStatus =
    watershed && reading
      ? watershed.streams.reduce<LevelStatus | null>((best, stream) => {
          const s = determineLevel(reading.value, stream.targetLevels);
          if (!best) return s;
          const priority: Record<LevelStatus, number> = {
            [LevelStatus.High]: 4,
            [LevelStatus.Optimal]: 3,
            [LevelStatus.Low]: 2,
            [LevelStatus.TooLow]: 1,
          };
          return priority[s] > priority[best] ? s : best;
        }, null)
      : null;

  return (
    <Box
      sx={{
        flex: 1,
        overflow: 'auto',
        p: { xs: 2, md: 3 },
        maxWidth: 900,
        mx: 'auto',
        width: '100%',
      }}
    >
      {/* Header with back button */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
        <IconButton onClick={() => navigate('/precipitation')} size="small">
          <ArrowBack />
        </IconButton>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>
          {location?.name ?? gaugeId}
        </Typography>
      </Box>

      {loading && !forecast && !precip && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Current Conditions - 3 stat cards */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' },
          gap: 2,
          mb: 3,
        }}
      >
        <GlassCard hover={false} sx={{ p: 2 }}>
          <Typography
            variant="caption"
            sx={{
              color: 'text.secondary',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              fontSize: '0.7rem',
            }}
          >
            Stage
          </Typography>
          <Typography variant="h4" sx={{ fontWeight: 700, mt: 0.5 }}>
            {reading ? `${reading.value} ft` : '\u2014'}
          </Typography>
        </GlassCard>

        <GlassCard hover={false} sx={{ p: 2 }}>
          <Typography
            variant="caption"
            sx={{
              color: 'text.secondary',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              fontSize: '0.7rem',
            }}
          >
            Trend
          </Typography>
          <Typography
            variant="h4"
            sx={{
              fontWeight: 700,
              mt: 0.5,
              color: trendColor ?? 'text.primary',
            }}
          >
            {trendLabel ?? '\u2014'}
          </Typography>
        </GlassCard>

        <GlassCard hover={false} sx={{ p: 2 }}>
          <Typography
            variant="caption"
            sx={{
              color: 'text.secondary',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              fontSize: '0.7rem',
            }}
          >
            Status
          </Typography>
          {highestStatus ? (
            <Chip
              label={STATUS_LABELS[highestStatus]}
              sx={{
                mt: 1,
                bgcolor: STATUS_HEX_COLORS[highestStatus],
                color: '#fff',
                fontWeight: 700,
                fontSize: '0.85rem',
              }}
            />
          ) : (
            <Typography variant="h4" sx={{ fontWeight: 700, mt: 0.5 }}>
              {'\u2014'}
            </Typography>
          )}
        </GlassCard>
      </Box>

      {/* Level Range Bars */}
      {watershed && (
        <GlassCard hover={false} sx={{ p: 2, mb: 3 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5 }}>
            Current Level vs Target Ranges
          </Typography>
          {watershed.streams.map((stream) => (
            <LevelRangeBar
              key={stream.name}
              currentStage={reading?.value ?? null}
              targetLevels={stream.targetLevels}
              streamName={stream.name}
            />
          ))}
        </GlassCard>
      )}

      {/* Stage Forecast Chart */}
      {forecast && forecast.data.length >= 2 && (
        <GlassCard hover={false} sx={{ p: 2, mb: 3 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5 }}>
            Stage Forecast
          </Typography>
          <StageChart
            data={forecast.data}
            floodCategories={forecast.floodCategories}
            currentStage={reading?.value}
          />
        </GlassCard>
      )}

      {/* Rainfall Totals - 4 cards */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' },
          gap: 2,
          mb: 3,
        }}
      >
        {[
          { label: '24h', value: precip?.last24h },
          { label: '48h', value: precip?.last48h },
          { label: '72h', value: precip?.last72h },
          { label: '7 Day', value: precip?.last7d },
        ].map((item) => (
          <GlassCard
            key={item.label}
            hover={false}
            sx={{ p: 2, textAlign: 'center' }}
          >
            <WaterDrop sx={{ fontSize: 18, color: '#30cfd0', mb: 0.5 }} />
            <Typography variant="h5" sx={{ fontWeight: 700 }}>
              {item.value !== null && item.value !== undefined
                ? `${item.value.toFixed(2)}"`
                : '\u2014'}
            </Typography>
            <Typography
              variant="caption"
              sx={{ color: 'text.secondary', fontWeight: 600 }}
            >
              {item.label}
            </Typography>
          </GlassCard>
        ))}
      </Box>

      {/* Streams on This Gauge */}
      {watershed && (
        <GlassCard hover={false} sx={{ p: 2, mb: 3 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5 }}>
            Streams on This Gauge
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
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
                    py: 1,
                    px: 1.5,
                    borderRadius: 1,
                    transition: 'background 0.2s',
                    '&:hover': { bgcolor: alpha('#30cfd0', 0.06) },
                  }}
                >
                  <Box>
                    {streamId ? (
                      <Link
                        to={`/stream/${streamId}`}
                        style={{
                          color: 'inherit',
                          textDecoration: 'none',
                          fontWeight: 600,
                        }}
                      >
                        {stream.name}
                      </Link>
                    ) : (
                      <Typography sx={{ fontWeight: 600 }}>
                        {stream.name}
                      </Typography>
                    )}
                    <Typography
                      variant="caption"
                      sx={{ display: 'block', color: 'text.secondary' }}
                    >
                      Optimal: {stream.targetLevels.optimal}&ndash;
                      {stream.targetLevels.high} ft
                    </Typography>
                  </Box>
                  {status && (
                    <Chip
                      label={STATUS_LABELS[status]}
                      size="small"
                      sx={{
                        bgcolor: STATUS_HEX_COLORS[status],
                        color: '#fff',
                        fontWeight: 700,
                        fontSize: '0.7rem',
                      }}
                    />
                  )}
                </Box>
              );
            })}
          </Box>
        </GlassCard>
      )}

      {/* Flood Stages */}
      {forecast?.floodCategories && (
        <GlassCard hover={false} sx={{ p: 2 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5 }}>
            Flood Stages
          </Typography>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: 'repeat(4, 1fr)',
              gap: 1,
              textAlign: 'center',
            }}
          >
            {[
              {
                label: 'Action',
                value: forecast.floodCategories.action,
                color: '#ff9800',
              },
              {
                label: 'Minor',
                value: forecast.floodCategories.minor,
                color: '#f44336',
              },
              {
                label: 'Moderate',
                value: forecast.floodCategories.moderate,
                color: '#d32f2f',
              },
              {
                label: 'Major',
                value: forecast.floodCategories.major,
                color: '#b71c1c',
              },
            ].map((item) => (
              <Box key={item.label}>
                <Typography
                  variant="h6"
                  sx={{ fontWeight: 700, color: item.color }}
                >
                  {item.value > 0 ? `${item.value} ft` : '\u2014'}
                </Typography>
                <Typography
                  variant="caption"
                  sx={{ color: 'text.secondary', fontWeight: 600 }}
                >
                  {item.label}
                </Typography>
              </Box>
            ))}
          </Box>
        </GlassCard>
      )}
    </Box>
  );
}
