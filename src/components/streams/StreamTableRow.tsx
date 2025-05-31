import { TableRow, TableCell, Tooltip, useTheme } from '@mui/material';
import { StreamData, LevelTrend } from '../../types/stream';
import { useStreamGauge } from '../../hooks/useStreamGauge';
import { getReadingFreshnessClass } from '../../utils/streamLevels';
import InfoTooltip from './StreamInfoTooltip';
import { format, formatDistanceToNow } from 'date-fns';

interface StreamTableRowProps {
  stream: StreamData;
  onClick: (stream: StreamData) => void;
}

export function StreamTableRow({ stream, onClick }: StreamTableRowProps) {
  const { currentLevel, reading, loading, error } = useStreamGauge(stream);
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

  const timeFreshnessClass = reading?.timestamp
    ? getReadingFreshnessClass(reading.timestamp)
    : '';

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
        <Tooltip
          title={<InfoTooltip type="rating" value={stream.rating} />}
          placement="right"
          arrow
        >
          <span style={{ cursor: 'help' }}>{stream.rating}</span>
        </Tooltip>
      </TableCell>

      {/* Size */}
      <TableCell>
        <Tooltip
          title={<InfoTooltip type="size" value={stream.size} />}
          placement="right"
          arrow
        >
          <span style={{ cursor: 'help' }}>{stream.size}</span>
        </Tooltip>
      </TableCell>

      {/* Reference Gauge */}
      <TableCell>
        <Tooltip title="View USGS Gauge Page">
          <a
            href={stream.gauge.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="text-blue-500 hover:underline"
          >
            {stream.gauge.name}
          </a>
        </Tooltip>
        {!loading && !error && (
          <div className="text-sm">
            [{stream.targetLevels.tooLow}, {stream.targetLevels.optimal},{' '}
            {stream.targetLevels.high}]
          </div>
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
      <TableCell className={timeFreshnessClass}>
        {reading?.timestamp && (
          <>
            {format(new Date(reading.timestamp), 'MM/dd HH:mm')}
            <br />
            <span className="text-sm">
              ({formatDistanceToNow(new Date(reading.timestamp))})
            </span>
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

      {/* Current Level with trend */}
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
        ) : (
          <div className="flex items-center">
            <span>{currentLevel?.status || 'N/A'}</span>
            <span className="ml-2">
              {currentLevel?.trend === LevelTrend.Rising
                ? '↑'
                : currentLevel?.trend === LevelTrend.Falling
                  ? '↓'
                  : currentLevel?.trend === LevelTrend.Holding
                    ? '—'
                    : ''}
            </span>
          </div>
        )}
      </TableCell>
    </TableRow>
  );
}
