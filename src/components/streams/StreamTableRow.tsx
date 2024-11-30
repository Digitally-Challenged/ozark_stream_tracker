import React from 'react';
import { TableRow, TableCell, Tooltip, useTheme } from '@mui/material';
import { StreamData } from '../../types/stream';
import { useStreamGauge } from '../../hooks/useStreamGauge';
import InfoTooltip from './StreamInfoTooltip';

interface StreamTableRowProps {
  stream: StreamData;
  onClick: (stream: StreamData) => void;
}

export function StreamTableRow({ stream, onClick }: StreamTableRowProps) {
  const { currentLevel, reading, loading, error } = useStreamGauge(stream);
  const theme = useTheme();

  const getLevelColor = (level: string) => {
    const alpha = theme.palette.mode === 'dark' ? '0.3' : '0.2';
    switch (level) {
      case 'X':
        return theme.palette.mode === 'dark'
          ? `rgba(211, 47, 47, ${alpha})`  // Dark mode red - Too Low
          : `rgba(211, 47, 47, ${alpha})`; // Light mode red
      case 'L':
        return theme.palette.mode === 'dark'
          ? `rgba(237, 108, 2, ${alpha})`  // Dark mode orange - Low
          : `rgba(237, 108, 2, ${alpha})`; // Light mode orange
      case 'O':
        return theme.palette.mode === 'dark' 
          ? `rgba(46, 125, 50, ${alpha})`  // Dark mode green - Optimal
          : `rgba(46, 125, 50, ${alpha})`; // Light mode green
      case 'H':
        return theme.palette.mode === 'dark'
          ? `rgba(2, 136, 209, ${alpha})`  // Dark mode blue - High/Flood
          : `rgba(2, 136, 209, ${alpha})`; // Light mode blue
      default:
        return undefined;
    }
  };

  return (
    <TableRow 
      hover
      onClick={() => onClick(stream)}
      sx={{ 
        cursor: 'pointer',
        '&:hover': {
          backgroundColor: theme.palette.mode === 'dark' 
            ? 'rgba(255, 255, 255, 0.08)' 
            : 'rgba(0, 0, 0, 0.04)',
        },
      }}
    >
      <TableCell>{stream.name}</TableCell>
      <TableCell>{stream.rating}</TableCell>
      <TableCell>
        <Tooltip
          title={<InfoTooltip type="size" value={stream.size} />}
          placement="right"
          arrow
        >
          <span style={{ cursor: 'help' }}>{stream.size}</span>
        </Tooltip>
      </TableCell>
      <TableCell>
        <Tooltip title="View USGS Gauge Page">
          <a
            href={stream.gauge.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            style={{ 
              color: theme.palette.primary.main,
              textDecoration: 'none',
              '&:hover': {
                textDecoration: 'underline',
              },
            }}
          >
            {stream.gauge.name}
          </a>
        </Tooltip>
      </TableCell>
      <TableCell>
        {reading && !loading && !error ? (
          <Tooltip title={`Last updated: ${new Date(reading.timestamp).toLocaleString()}`}>
            <span>{reading.value.toFixed(2)} ft</span>
          </Tooltip>
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
      <TableCell>
        <Tooltip
          title={<InfoTooltip type="correlation" value={stream.quality} />}
          placement="left"
          arrow
        >
          <span style={{ cursor: 'help' }}>{stream.quality}</span>
        </Tooltip>
      </TableCell>
      <TableCell 
        sx={{ 
          bgcolor: getLevelColor(currentLevel),
          transition: 'background-color 0.2s ease',
        }}
      >
        <Tooltip
          title={<InfoTooltip type="level" value={currentLevel} />}
          placement="left"
          arrow
        >
          <span style={{ cursor: 'help' }}>
            {loading ? 'Loading...' : error ? 'Error' : currentLevel}
          </span>
        </Tooltip>
      </TableCell>
    </TableRow>
  );
}