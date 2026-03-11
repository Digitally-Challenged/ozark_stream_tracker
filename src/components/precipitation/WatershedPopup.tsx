import { Box, Typography, Chip } from '@mui/material';
import { Link } from 'react-router-dom';
import { Watershed } from '../../utils/watershedGrouping';
import { GaugeReading, LevelStatus, LevelTrend } from '../../types/stream';
import { determineLevel, determineTrend } from '../../utils/streamLevels';
import { STATUS_HEX_COLORS } from '../../utils/streamLevels';
import { getStreamIdFromName } from '../../utils/streamIds';
import { getTrendLabel } from '../../utils/trendUtils';

interface WatershedPopupProps {
  watershed: Watershed;
  reading: GaugeReading | null;
  previousReading: GaugeReading | null;
}

const STATUS_LABELS: Record<LevelStatus, string> = {
  [LevelStatus.TooLow]: 'Too Low',
  [LevelStatus.Low]: 'Low',
  [LevelStatus.Optimal]: 'Optimal',
  [LevelStatus.High]: 'High',
};

export function WatershedPopup({
  watershed,
  reading,
  previousReading,
}: WatershedPopupProps) {
  const trend =
    reading && previousReading
      ? determineTrend(reading, previousReading)
      : LevelTrend.None;
  const trendLabel = getTrendLabel(trend);

  return (
    <Box sx={{ minWidth: 200, maxWidth: 280 }}>
      <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 0.5 }}>
        {watershed.gauge.name}
      </Typography>

      {reading ? (
        <Typography variant="body2" sx={{ mb: 1, color: 'text.secondary' }}>
          {reading.value} ft{trendLabel ? ` (${trendLabel})` : ''}
        </Typography>
      ) : (
        <Typography variant="body2" sx={{ mb: 1, color: 'text.disabled' }}>
          Loading...
        </Typography>
      )}

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
              }}
            >
              {streamId ? (
                <Link
                  to={`/stream/${streamId}`}
                  style={{
                    color: 'inherit',
                    textDecoration: 'none',
                    fontSize: '0.8rem',
                  }}
                >
                  {stream.name}
                </Link>
              ) : (
                <Typography variant="caption">{stream.name}</Typography>
              )}
              {status && (
                <Chip
                  label={STATUS_LABELS[status]}
                  size="small"
                  sx={{
                    height: 20,
                    fontSize: '0.65rem',
                    bgcolor: STATUS_HEX_COLORS[status],
                    color: '#fff',
                  }}
                />
              )}
            </Box>
          );
        })}
      </Box>
    </Box>
  );
}
