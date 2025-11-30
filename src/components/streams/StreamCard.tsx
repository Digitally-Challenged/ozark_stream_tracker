// src/components/streams/StreamCard.tsx
import { memo } from 'react';
import {
  Card,
  CardContent,
  CardActionArea,
  Box,
  Typography,
  useTheme,
  Skeleton,
} from '@mui/material';
import { StreamData, LevelStatus, LevelTrend } from '../../types/stream';
import { useGaugeReading } from '../../hooks/useGaugeReading';
import { useRelativeTime } from '../../hooks/useRelativeTime';
import { RatingBadge } from '../badges/RatingBadge';
import { SizeBadge } from '../badges/SizeBadge';
import { StreamConditionIcon } from '../icons/StreamConditionIcon';
import { TrendIcon } from '../icons/TrendIcon';
import { LiquidFillBar } from '../common/LiquidFillBar';
import { glassmorphism } from '../../theme/waterTheme';

interface StreamCardProps {
  stream: StreamData;
  onClick: (stream: StreamData) => void;
}

const STATUS_COLORS: Record<LevelStatus, string> = {
  [LevelStatus.Optimal]: '#2e7d32',
  [LevelStatus.Low]: '#ed6c02',
  [LevelStatus.High]: '#0288d1',
  [LevelStatus.TooLow]: '#d32f2f',
};

export const StreamCard = memo(function StreamCard({ stream, onClick }: StreamCardProps) {
  const { currentLevel, reading, loading, error } = useGaugeReading(
    stream.gauge.id,
    stream.targetLevels
  );
  const relativeTime = useRelativeTime(reading?.timestamp);
  const theme = useTheme();

  const statusColor = currentLevel?.status
    ? STATUS_COLORS[currentLevel.status]
    : theme.palette.grey[500];

  return (
    <Card
      sx={{
        height: '100%',
        borderLeft: `4px solid ${statusColor}`,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        ...(theme.palette.mode === 'dark' ? glassmorphism.dark : glassmorphism.light),
        backdropFilter: 'blur(8px)',
        '&:hover': {
          transform: 'translateY(-4px) scale(1.01)',
          boxShadow: `0 12px 40px ${statusColor}30`,
          borderLeftWidth: '6px',
        },
      }}
    >
      <CardActionArea onClick={() => onClick(stream)} sx={{ height: '100%' }}>
        <CardContent>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              mb: 1,
            }}
          >
            <Typography
              variant="h6"
              component="h3"
              sx={{ fontWeight: 'medium' }}
            >
              {stream.name}
            </Typography>
            {currentLevel?.status && (
              <StreamConditionIcon status={currentLevel.status} size="medium" />
            )}
          </Box>

          <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
            <RatingBadge rating={stream.rating} size="small" />
            <SizeBadge size={stream.size} />
            <Typography variant="caption" color="text.secondary">
              {stream.quality} quality
            </Typography>
          </Box>

          {loading ? (
            <Box sx={{ mt: 1 }}>
              <Skeleton variant="text" width="60%" height={36} />
              <Skeleton variant="text" width="40%" height={20} sx={{ mt: 0.5 }} />
            </Box>
          ) : error ? (
            <Typography color="error">Unavailable</Typography>
          ) : reading ? (
            <Box>
              <Box
                sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}
              >
                <Typography variant="h5" component="span" fontWeight="bold">
                  {reading.value.toFixed(2)} ft
                </Typography>
                {currentLevel?.trend &&
                  currentLevel.trend !== LevelTrend.None && (
                    <Box
                      sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
                    >
                      <TrendIcon trend={currentLevel.trend} size="medium" />
                      <Typography
                        variant="caption"
                        sx={{
                          color:
                            currentLevel.trend === LevelTrend.Rising
                              ? 'success.main'
                              : currentLevel.trend === LevelTrend.Falling
                                ? 'error.main'
                                : 'warning.main',
                          fontWeight: 'bold',
                          textTransform: 'uppercase',
                          fontSize: '0.7rem',
                        }}
                      >
                        {currentLevel.trend === LevelTrend.Rising
                          ? 'Rising'
                          : currentLevel.trend === LevelTrend.Falling
                            ? 'Falling'
                            : 'Stable'}
                      </Typography>
                    </Box>
                  )}
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Updated {relativeTime}
              </Typography>
              {currentLevel?.status && (
                <LiquidFillBar
                  currentValue={reading.value}
                  minValue={stream.targetLevels.tooLow * 0.5}
                  maxValue={stream.targetLevels.high * 1.5}
                  status={currentLevel.status}
                  height={40}
                />
              )}
            </Box>
          ) : (
            <Typography color="text.secondary">No data</Typography>
          )}
        </CardContent>
      </CardActionArea>
    </Card>
  );
}, (prevProps, nextProps) => {
  return prevProps.stream.name === nextProps.stream.name &&
         prevProps.stream.gauge?.id === nextProps.stream.gauge?.id &&
         prevProps.onClick === nextProps.onClick;
});
