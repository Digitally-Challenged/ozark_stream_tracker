import { Box, Typography } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { STATUS_HEX_COLORS, STATUS_LABELS } from '../../utils/streamLevels';
import { LevelStatus, TargetLevels } from '../../types/stream';

interface LevelRangeBarProps {
  currentStage: number | null;
  targetLevels: TargetLevels;
  streamName: string;
}

export function LevelRangeBar({
  currentStage,
  targetLevels,
  streamName,
}: LevelRangeBarProps) {
  const maxRange = targetLevels.high * 1.2;
  const zones = [
    {
      label: STATUS_LABELS[LevelStatus.TooLow],
      color: STATUS_HEX_COLORS[LevelStatus.TooLow],
      start: 0,
      end: targetLevels.tooLow,
    },
    {
      label: STATUS_LABELS[LevelStatus.Low],
      color: STATUS_HEX_COLORS[LevelStatus.Low],
      start: targetLevels.tooLow,
      end: targetLevels.optimal,
    },
    {
      label: STATUS_LABELS[LevelStatus.Optimal],
      color: STATUS_HEX_COLORS[LevelStatus.Optimal],
      start: targetLevels.optimal,
      end: targetLevels.high,
    },
    {
      label: STATUS_LABELS[LevelStatus.High],
      color: STATUS_HEX_COLORS[LevelStatus.High],
      start: targetLevels.high,
      end: maxRange,
    },
  ];

  const pct = (val: number) =>
    Math.min(100, Math.max(0, (val / maxRange) * 100));
  const markerPct = currentStage !== null ? pct(currentStage) : null;

  return (
    <Box sx={{ mb: 1.5 }}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'baseline',
          mb: 0.5,
        }}
      >
        <Typography
          variant="caption"
          sx={{ fontWeight: 600, fontSize: '0.75rem' }}
        >
          {streamName}
        </Typography>
        {currentStage !== null && (
          <Typography
            variant="caption"
            sx={{ color: 'text.secondary', fontSize: '0.65rem' }}
          >
            {currentStage.toFixed(2)} ft
            {currentStage < targetLevels.optimal &&
              ` — need +${(targetLevels.optimal - currentStage).toFixed(1)} ft for optimal`}
          </Typography>
        )}
      </Box>

      <Box
        sx={{
          position: 'relative',
          height: 12,
          borderRadius: 1,
          overflow: 'hidden',
          display: 'flex',
        }}
      >
        {zones.map((zone) => (
          <Box
            key={zone.label}
            sx={{
              width: `${pct(zone.end) - pct(zone.start)}%`,
              height: '100%',
              bgcolor: alpha(zone.color, 0.5),
              borderRight: '1px solid rgba(255,255,255,0.2)',
              '&:last-of-type': { borderRight: 'none' },
            }}
          />
        ))}
        {markerPct !== null && (
          <Box
            sx={{
              position: 'absolute',
              left: `${markerPct}%`,
              top: -2,
              bottom: -2,
              width: 3,
              bgcolor: '#fff',
              borderRadius: 1,
              boxShadow: '0 0 4px rgba(0,0,0,0.4)',
              transform: 'translateX(-50%)',
            }}
          />
        )}
      </Box>

      <Box sx={{ display: 'flex', mt: 0.25 }}>
        {zones.map((zone) => (
          <Typography
            key={zone.label}
            variant="caption"
            sx={{
              width: `${pct(zone.end) - pct(zone.start)}%`,
              textAlign: 'center',
              fontSize: '0.5rem',
              color: 'text.disabled',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {zone.label}
          </Typography>
        ))}
      </Box>
    </Box>
  );
}
