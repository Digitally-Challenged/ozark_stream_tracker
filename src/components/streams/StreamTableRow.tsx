import { memo } from 'react';
import {
  TableRow,
  TableCell,
  Tooltip,
  useTheme,
  Link,
  Typography,
  Box,
  Skeleton,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { StreamData, LevelTrend } from '../../types/stream';
import { useGaugeReading } from '../../hooks/useGaugeReading';
import { useRelativeTime } from '../../hooks/useRelativeTime';
import { getReadingFreshnessColor } from '../../utils/streamLevels';
import { getStreamIdFromName } from '../../utils/streamIds';
import InfoTooltip from './StreamInfoTooltip';
import { format } from 'date-fns';
import { RatingBadge } from '../badges/RatingBadge';
import { SizeBadge } from '../badges/SizeBadge';
import { StreamConditionIcon } from '../icons/StreamConditionIcon';
import { TrendIcon } from '../icons/TrendIcon';

interface StreamTableRowProps {
  stream: StreamData;
  onClick: (stream: StreamData) => void;
}

const StreamTableRowComponent = ({ stream, onClick }: StreamTableRowProps) => {
  const { currentLevel, reading, loading, error } = useGaugeReading(
    stream.gauge.id,
    stream.targetLevels
  );
  const relativeTime = useRelativeTime(reading?.timestamp);
  const theme = useTheme();

  const getLevelColor = (status: string | undefined) => {
    if (!status) return undefined;

    const alpha = theme.palette.mode === 'dark' ? '0.3' : '0.2';
    switch (status) {
      case 'X':
        return `rgba(211, 47, 47, ${alpha})`; // Too Low
      case 'L':
        return `rgba(237, 108, 2, ${alpha})`; // Low
      case 'O':
        return `rgba(46, 125, 50, ${alpha})`; // Optimal
      case 'H':
        return `rgba(2, 136, 209, ${alpha})`; // High
      default:
        return undefined;
    }
  };

  const timeFreshnessColor = reading?.timestamp
    ? getReadingFreshnessColor(reading.timestamp, theme)
    : undefined;

  return (
    <TableRow
      hover
      onClick={() => onClick(stream)}
      sx={{
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        '&:hover': {
          backgroundColor:
            theme.palette.mode === 'dark'
              ? 'rgba(255, 255, 255, 0.08)'
              : 'rgba(0, 0, 0, 0.04)',
          transform: 'scale(1.005)',
          boxShadow:
            theme.palette.mode === 'dark'
              ? '0 4px 20px rgba(0, 0, 0, 0.3)'
              : '0 4px 20px rgba(0, 0, 0, 0.1)',
        },
        '&:active': {
          transform: 'scale(0.995)',
        },
      }}
    >
      {/* Stream Name */}
      <TableCell>
        {(() => {
          const streamId = getStreamIdFromName(stream.name);
          return streamId ? (
            <Link
              component={RouterLink}
              to={`/stream/${streamId}`}
              onClick={(e) => e.stopPropagation()}
              sx={{
                color: theme.palette.text.primary,
                textDecoration: 'none',
                fontWeight: 500,
                '&:hover': {
                  color: theme.palette.primary.main,
                  textDecoration: 'underline',
                },
              }}
            >
              {stream.name}
            </Link>
          ) : (
            <Typography
              component="span"
              sx={{
                fontWeight: 500,
                color: theme.palette.text.secondary,
              }}
            >
              {stream.name}
            </Typography>
          );
        })()}
      </TableCell>

      {/* Rating */}
      <TableCell>
        <RatingBadge rating={stream.rating} size="small" animated />
      </TableCell>

      {/* Size */}
      <TableCell>
        <SizeBadge size={stream.size} animated />
      </TableCell>

      {/* Reference Gauge */}
      <TableCell>
        <Tooltip title="View USGS Gauge Page">
          <Link
            href={stream.gauge.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            sx={{
              color: theme.palette.primary.main,
              textDecoration: 'none',
              '&:hover': {
                textDecoration: 'underline',
              },
            }}
          >
            {stream.gauge.name}
          </Link>
        </Tooltip>
        {!loading && !error && (
          <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>
            [{stream.targetLevels.tooLow}, {stream.targetLevels.optimal},{' '}
            {stream.targetLevels.high}]
          </Typography>
        )}
      </TableCell>

      {/* Current Reading with Trend */}
      <TableCell>
        {reading && !loading && !error ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <span>{reading.value.toFixed(2)} ft</span>
            {currentLevel?.trend && currentLevel.trend !== LevelTrend.None && (
              <TrendIcon trend={currentLevel.trend} size="small" />
            )}
          </Box>
        ) : loading ? (
          <Skeleton variant="text" width={80} height={24} />
        ) : error ? (
          <Tooltip title={error.message}>
            <span>Error</span>
          </Tooltip>
        ) : (
          'N/A'
        )}
      </TableCell>

      {/* Time with freshness coloring */}
      <TableCell sx={{ color: timeFreshnessColor }}>
        {reading?.timestamp && (
          <>
            {format(new Date(reading.timestamp), 'MM/dd HH:mm')}
            <br />
            <Typography
              variant="body2"
              component="span"
              sx={{ fontSize: '0.875rem' }}
            >
              ({relativeTime})
            </Typography>
          </>
        )}
      </TableCell>

      {/* Quality */}
      <TableCell>
        <Tooltip
          title={<InfoTooltip type="correlation" value={stream.quality} />}
          placement="left"
          arrow
        >
          <span style={{ cursor: 'help' }}>{stream.quality}</span>
        </Tooltip>
      </TableCell>

      {/* Current Level */}
      <TableCell
        sx={{
          bgcolor: getLevelColor(currentLevel?.status),
          transition: 'background-color 0.2s ease',
        }}
      >
        {loading ? (
          <Skeleton variant="circular" width={24} height={24} />
        ) : error ? (
          <Tooltip title={error.message}>
            <span>Error</span>
          </Tooltip>
        ) : currentLevel?.status ? (
          <StreamConditionIcon status={currentLevel.status} size="small" />
        ) : (
          'N/A'
        )}
      </TableCell>

      {/* Trend */}
      <TableCell>
        {loading ? (
          <Skeleton variant="circular" width={20} height={20} />
        ) : error ? (
          <Tooltip title={error.message}>
            <span>Error</span>
          </Tooltip>
        ) : currentLevel?.trend && currentLevel.trend !== LevelTrend.None ? (
          <Tooltip title={`Water level ${currentLevel.trend}`}>
            <div>
              <TrendIcon trend={currentLevel.trend} size="small" />
            </div>
          </Tooltip>
        ) : (
          <Tooltip title="No trend data available">
            <span style={{ opacity: 0.5 }}>—</span>
          </Tooltip>
        )}
      </TableCell>
    </TableRow>
  );
};

// Export without custom memo - useGaugeReading hook handles context updates
export const StreamTableRow = memo(StreamTableRowComponent);
