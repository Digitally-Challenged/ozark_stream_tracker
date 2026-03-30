import { useMemo } from 'react';
import { Box, Typography, Chip } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { format, startOfDay, isSameDay } from 'date-fns';
import { NwsForecastPoint } from '../../services/nwsForecastService';
import { StreamData, LevelStatus } from '../../types/stream';
import {
  determineLevel,
  STATUS_HEX_COLORS,
  STATUS_LABELS,
} from '../../utils/streamLevels';

interface ForecastTableProps {
  forecastData: NwsForecastPoint[];
  streams: StreamData[];
}

interface DayForecast {
  date: Date;
  label: string;
  isToday: boolean;
  avgStage: number;
  minStage: number;
  maxStage: number;
  streamStatuses: Array<{
    name: string;
    status: LevelStatus;
  }>;
}

export function ForecastTable({ forecastData, streams }: ForecastTableProps) {
  const days = useMemo(() => {
    if (forecastData.length === 0) return [];

    // Group forecast points by day
    const dayMap = new Map<string, NwsForecastPoint[]>();
    for (const point of forecastData) {
      const day = startOfDay(new Date(point.validTime));
      const key = day.toISOString();
      const existing = dayMap.get(key) ?? [];
      existing.push(point);
      dayMap.set(key, existing);
    }

    const now = new Date();
    const result: DayForecast[] = [];

    for (const [key, points] of dayMap) {
      const date = new Date(key);
      const stages = points.map((p) => p.stage);
      const avgStage = stages.reduce((a, b) => a + b, 0) / stages.length;
      const maxStage = Math.max(...stages);
      const minStage = Math.min(...stages);

      const streamStatuses = streams.map((stream) => ({
        name: stream.name,
        status: determineLevel(avgStage, stream.targetLevels),
      }));

      result.push({
        date,
        label: format(date, 'EEE M/d'),
        isToday: isSameDay(date, now),
        avgStage,
        minStage,
        maxStage,
        streamStatuses,
      });
    }

    return result.sort((a, b) => a.date.getTime() - b.date.getTime());
  }, [forecastData, streams]);

  if (days.length === 0) return null;

  return (
    <Box sx={{ overflowX: 'auto' }}>
      <Box
        component="table"
        sx={{
          width: '100%',
          borderCollapse: 'collapse',
          '& th, & td': {
            px: 1.5,
            py: 1,
            textAlign: 'center',
            fontSize: '0.75rem',
            borderBottom: (theme) =>
              `1px solid ${alpha(theme.palette.divider, 0.2)}`,
          },
          '& th': {
            fontWeight: 700,
            color: 'text.secondary',
            textTransform: 'uppercase',
            fontSize: '0.65rem',
            letterSpacing: '0.05em',
          },
        }}
      >
        <thead>
          <tr>
            <Box component="th" sx={{ textAlign: 'left !important' }}>
              Day
            </Box>
            <th>Stage</th>
            {streams.map((s) => (
              <th key={s.name}>{s.name}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {days.map((day) => (
            <Box
              component="tr"
              key={day.label}
              sx={{
                fontWeight: day.isToday ? 700 : 400,
                bgcolor: day.isToday
                  ? (theme) => alpha(theme.palette.primary.main, 0.05)
                  : 'transparent',
              }}
            >
              <Box
                component="td"
                sx={{ textAlign: 'left !important', whiteSpace: 'nowrap' }}
              >
                <Typography
                  variant="caption"
                  sx={{
                    fontWeight: day.isToday ? 700 : 600,
                    fontSize: '0.75rem',
                  }}
                >
                  {day.label}
                  {day.isToday && (
                    <Box
                      component="span"
                      sx={{
                        ml: 0.5,
                        color: 'primary.main',
                        fontSize: '0.6rem',
                      }}
                    >
                      TODAY
                    </Box>
                  )}
                </Typography>
              </Box>
              <td>
                <Typography
                  variant="caption"
                  sx={{ fontWeight: 700, fontSize: '0.75rem' }}
                >
                  {day.avgStage.toFixed(1)} ft
                </Typography>
                {day.maxStage - day.minStage > 0.2 && (
                  <Typography
                    variant="caption"
                    sx={{
                      display: 'block',
                      color: 'text.disabled',
                      fontSize: '0.55rem',
                    }}
                  >
                    {day.minStage.toFixed(1)}&ndash;{day.maxStage.toFixed(1)}
                  </Typography>
                )}
              </td>
              {day.streamStatuses.map((ss) => (
                <td key={ss.name}>
                  <Chip
                    label={STATUS_LABELS[ss.status]}
                    size="small"
                    sx={{
                      height: 20,
                      fontSize: '0.6rem',
                      fontWeight: 700,
                      bgcolor: STATUS_HEX_COLORS[ss.status],
                      color: '#fff',
                    }}
                  />
                </td>
              ))}
            </Box>
          ))}
        </tbody>
      </Box>
    </Box>
  );
}
