import { Box, Typography, Chip, useTheme } from '@mui/material';
import {
  WaterDrop,
  TrendingUp,
  TrendingDown,
  TrendingFlat,
} from '@mui/icons-material';
import { StreamContent } from '../../types/streamContent';
import { StreamData, LevelTrend } from '../../types/stream';
import { useStreamGauge } from '../../hooks/useStreamGauge';
import { determineLevel } from '../../utils/streamLevels';

interface StreamHeaderProps {
  content: StreamContent;
  streamData?: StreamData;
}

function TrendIcon({ trend }: { trend: LevelTrend }) {
  switch (trend) {
    case LevelTrend.Rising:
      return <TrendingUp sx={{ fontSize: 18 }} />;
    case LevelTrend.Falling:
      return <TrendingDown sx={{ fontSize: 18 }} />;
    default:
      return <TrendingFlat sx={{ fontSize: 18 }} />;
  }
}

function getStatusColor(status: string, theme: ReturnType<typeof useTheme>): string {
  switch (status) {
    case 'X':
      return theme.palette.error.main;
    case 'L':
      return theme.palette.warning.main;
    case 'O':
      return theme.palette.success.main;
    case 'H':
      return theme.palette.info.main;
    default:
      return theme.palette.grey[500];
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'X':
      return 'Too Low';
    case 'L':
      return 'Low';
    case 'O':
      return 'Optimal';
    case 'H':
      return 'High';
    default:
      return 'Unknown';
  }
}

// Separate component to safely use the gauge hook
function GaugeDisplay({ streamData }: { streamData: StreamData }) {
  const theme = useTheme();
  const { reading, currentLevel } = useStreamGauge(streamData);
  const trend = currentLevel?.trend ?? LevelTrend.None;

  const status = reading?.value
    ? determineLevel(reading.value, streamData.targetLevels)
    : null;

  if (!reading?.value) return null;

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        bgcolor: 'rgba(255,255,255,0.15)',
        borderRadius: 2,
        p: 2,
      }}
    >
      <WaterDrop sx={{ fontSize: 32 }} />
      <Box>
        <Typography variant="h5" sx={{ fontWeight: 600 }}>
          {reading.value.toFixed(2)} ft
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <TrendIcon trend={trend} />
          <Typography variant="body2">
            {trend === LevelTrend.Rising
              ? 'Rising'
              : trend === LevelTrend.Falling
                ? 'Falling'
                : 'Holding'}
          </Typography>
        </Box>
      </Box>
      {status && (
        <Chip
          label={getStatusLabel(status)}
          size="small"
          sx={{
            bgcolor: getStatusColor(status, theme),
            color: 'white',
            fontWeight: 600,
          }}
        />
      )}
    </Box>
  );
}

export function StreamHeader({ content, streamData }: StreamHeaderProps) {
  const theme = useTheme();

  return (
    <Box
      sx={{
        p: { xs: 2, md: 4 },
        background:
          theme.palette.mode === 'dark'
            ? 'linear-gradient(135deg, #1a237e 0%, #0d47a1 100%)'
            : 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)',
        color: 'white',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' },
          justifyContent: 'space-between',
          alignItems: { xs: 'flex-start', md: 'center' },
          gap: 2,
        }}
      >
        <Box>
          <Typography
            variant="h4"
            component="h1"
            sx={{ fontWeight: 600, mb: 1 }}
          >
            {content.name}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {content.overview.rating && (
              <Chip
                label={content.overview.rating}
                size="small"
                sx={{
                  bgcolor: 'rgba(255,255,255,0.2)',
                  color: 'white',
                  fontWeight: 500,
                }}
              />
            )}
            {content.overview.length && (
              <Chip
                label={content.overview.length}
                size="small"
                sx={{
                  bgcolor: 'rgba(255,255,255,0.2)',
                  color: 'white',
                }}
              />
            )}
            {content.overview.season && (
              <Chip
                label={content.overview.season}
                size="small"
                sx={{
                  bgcolor: 'rgba(255,255,255,0.2)',
                  color: 'white',
                }}
              />
            )}
          </Box>
        </Box>

        {streamData && <GaugeDisplay streamData={streamData} />}
      </Box>
    </Box>
  );
}
