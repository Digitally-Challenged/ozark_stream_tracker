import { memo } from 'react';
import { TableRow, TableCell, Tooltip, useTheme, Link, Typography } from '@mui/material';
import { StreamData, LevelTrend } from '../../types/stream';
import { useGaugeReading } from '../../hooks/useGaugeReading';
import { useRelativeTime } from '../../hooks/useRelativeTime';
import { getReadingFreshnessColor } from '../../utils/streamLevels';
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
        '&:hover': {
          backgroundColor:
            theme.palette.mode === 'dark'
              ? 'rgba(255, 255, 255, 0.08)'
              : 'rgba(0, 0, 0, 0.04)',
        },
      }}
    >
      {/* Stream Name */}
      <TableCell>{stream.name}</TableCell>

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

      {/* Current Reading */}
      <TableCell>
        {reading && !loading && !error ? (
          <span>{reading.value.toFixed(2)} ft</span>
        ) : loading ? (
          'Loading...'
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
            <Typography variant="body2" component="span" sx={{ fontSize: '0.875rem' }}>
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
          'Loading...'
        ) : error ? (
          <Tooltip title={error.message}>
            <span>Error</span>
          </Tooltip>
        ) : currentLevel?.status ? (
          <StreamConditionIcon 
            status={currentLevel.status} 
            size="small" 
          />
        ) : (
          'N/A'
        )}
      </TableCell>

      {/* Trend */}
      <TableCell>
        {loading ? (
          'Loading...'
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

// Memoize the component to prevent unnecessary re-renders
// Only re-render if stream data or onClick handler changes
export const StreamTableRow = memo(StreamTableRowComponent, (prevProps, nextProps) => {
  // Custom comparison function for deep equality check
  return (
    prevProps.stream.name === nextProps.stream.name &&
    prevProps.stream.rating === nextProps.stream.rating &&
    prevProps.stream.size === nextProps.stream.size &&
    prevProps.stream.quality === nextProps.stream.quality &&
    prevProps.stream.gauge?.id === nextProps.stream.gauge?.id &&
    prevProps.stream.targetLevels.tooLow === nextProps.stream.targetLevels.tooLow &&
    prevProps.stream.targetLevels.optimal === nextProps.stream.targetLevels.optimal &&
    prevProps.stream.targetLevels.high === nextProps.stream.targetLevels.high &&
    prevProps.onClick === nextProps.onClick
  );
});
