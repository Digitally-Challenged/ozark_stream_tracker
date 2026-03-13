import { Box, Typography, useTheme } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { format } from 'date-fns';
import {
  NwsForecastPoint,
  NwsFloodCategories,
} from '../../services/nwsForecastService';

interface StageChartProps {
  data: NwsForecastPoint[];
  floodCategories?: NwsFloodCategories | null;
  currentStage?: number;
}

const CHART_W = 600;
const CHART_H = 200;
const PAD = { top: 20, right: 20, bottom: 30, left: 45 };

export function StageChart({
  data,
  floodCategories,
  currentStage,
}: StageChartProps) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  if (data.length < 2) return null;

  const stages = data.map((d) => d.stage);
  const times = data.map((d) => new Date(d.validTime).getTime());

  let minStage = Math.min(...stages);
  let maxStage = Math.max(...stages);

  // Include flood action stage if it's close
  if (floodCategories && floodCategories.action <= maxStage * 1.5) {
    maxStage = Math.max(maxStage, floodCategories.action);
  }

  // Add padding to range
  const range = maxStage - minStage || 1;
  minStage = Math.max(0, minStage - range * 0.1);
  maxStage = maxStage + range * 0.1;

  const minTime = Math.min(...times);
  const maxTime = Math.max(...times);

  const x = (t: number) =>
    PAD.left +
    ((t - minTime) / (maxTime - minTime)) * (CHART_W - PAD.left - PAD.right);
  const y = (s: number) =>
    PAD.top +
    (1 - (s - minStage) / (maxStage - minStage)) *
      (CHART_H - PAD.top - PAD.bottom);

  const now = Date.now();
  const pathPoints = data.map((d, i) => `${x(times[i])},${y(d.stage)}`);
  const observedIdx = times.findIndex((t) => t > now);
  const splitIdx = observedIdx === -1 ? data.length : observedIdx;

  const observedPath = pathPoints.slice(0, splitIdx + 1).join(' L');
  const forecastPath = pathPoints.slice(Math.max(0, splitIdx - 1)).join(' L');

  // X-axis day labels
  const dayLabels: Array<{ time: number; label: string }> = [];
  const startDay = new Date(minTime);
  startDay.setHours(0, 0, 0, 0);
  for (
    let d = new Date(startDay);
    d.getTime() <= maxTime;
    d.setDate(d.getDate() + 1)
  ) {
    if (d.getTime() >= minTime) {
      dayLabels.push({ time: d.getTime(), label: format(d, 'EEE') });
    }
  }

  // Y-axis labels
  const ySteps = 4;
  const yLabels = Array.from(
    { length: ySteps + 1 },
    (_, i) => minStage + (range * 1.2 * i) / ySteps
  );

  const textColor = isDark ? alpha('#fff', 0.6) : alpha('#000', 0.5);
  const gridColor = isDark ? alpha('#fff', 0.08) : alpha('#000', 0.08);

  return (
    <Box sx={{ width: '100%' }}>
      <svg
        viewBox={`0 0 ${CHART_W} ${CHART_H}`}
        style={{ width: '100%', height: 'auto' }}
      >
        {/* Grid lines */}
        {yLabels.map((s, i) => (
          <line
            key={i}
            x1={PAD.left}
            x2={CHART_W - PAD.right}
            y1={y(s)}
            y2={y(s)}
            stroke={gridColor}
            strokeWidth={1}
          />
        ))}

        {/* Flood category line */}
        {floodCategories && floodCategories.action <= maxStage && (
          <line
            x1={PAD.left}
            x2={CHART_W - PAD.right}
            y1={y(floodCategories.action)}
            y2={y(floodCategories.action)}
            stroke="#f44336"
            strokeWidth={1}
            strokeDasharray="6,4"
            opacity={0.6}
          />
        )}

        {/* Observed line */}
        {splitIdx > 0 && (
          <path
            d={`M${observedPath}`}
            fill="none"
            stroke="#30cfd0"
            strokeWidth={2.5}
            strokeLinecap="round"
          />
        )}

        {/* Forecast line */}
        {splitIdx < data.length && (
          <path
            d={`M${forecastPath}`}
            fill="none"
            stroke="#30cfd0"
            strokeWidth={2}
            strokeDasharray="8,4"
            opacity={0.7}
            strokeLinecap="round"
          />
        )}

        {/* Current stage dot */}
        {currentStage !== undefined && (
          <circle
            cx={x(now > maxTime ? maxTime : now < minTime ? minTime : now)}
            cy={y(currentStage)}
            r={4}
            fill="#30cfd0"
            stroke="#fff"
            strokeWidth={2}
          />
        )}

        {/* Y-axis labels */}
        {yLabels.map((s, i) => (
          <text
            key={i}
            x={PAD.left - 8}
            y={y(s) + 4}
            textAnchor="end"
            fontSize={10}
            fill={textColor}
          >
            {s.toFixed(1)}
          </text>
        ))}

        {/* X-axis day labels */}
        {dayLabels.map((d, i) => (
          <text
            key={i}
            x={x(d.time)}
            y={CHART_H - 5}
            textAnchor="middle"
            fontSize={10}
            fill={textColor}
          >
            {d.label}
          </text>
        ))}
      </svg>
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 0.5 }}>
        <Typography
          variant="caption"
          sx={{
            color: 'text.secondary',
            display: 'flex',
            alignItems: 'center',
            gap: 0.5,
          }}
        >
          <Box
            component="span"
            sx={{
              width: 16,
              height: 2,
              bgcolor: '#30cfd0',
              display: 'inline-block',
            }}
          />{' '}
          Observed
        </Typography>
        <Typography
          variant="caption"
          sx={{
            color: 'text.secondary',
            display: 'flex',
            alignItems: 'center',
            gap: 0.5,
          }}
        >
          <Box
            component="span"
            sx={{
              width: 16,
              height: 2,
              bgcolor: '#30cfd0',
              opacity: 0.7,
              display: 'inline-block',
              borderTop: '2px dashed #30cfd0',
              background: 'none',
            }}
          />{' '}
          Forecast
        </Typography>
      </Box>
    </Box>
  );
}
