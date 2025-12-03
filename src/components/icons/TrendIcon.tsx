import { Box, Tooltip } from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Remove,
  TrendingFlat,
} from '@mui/icons-material';
import { LevelTrend } from '../../types/stream';

const trendDescriptions: Record<LevelTrend, string> = {
  [LevelTrend.Rising]: 'Water level rising - conditions may be improving',
  [LevelTrend.Falling]: 'Water level falling - conditions may be worsening',
  [LevelTrend.Holding]: 'Water level stable - conditions unchanged',
  [LevelTrend.None]: 'No trend data available',
};

interface TrendIconProps {
  trend: LevelTrend;
  size?: 'small' | 'medium' | 'large';
}

export function TrendIcon({ trend, size = 'medium' }: TrendIconProps) {
  const sizeMap = {
    small: 18,
    medium: 22,
    large: 28,
  };

  const iconSize = sizeMap[size];

  const getTrendDisplay = () => {
    switch (trend) {
      case LevelTrend.Rising:
        return (
          <TrendingUp
            sx={{
              fontSize: iconSize,
              color: 'success.main',
              fontWeight: 'bold',
            }}
          />
        );
      case LevelTrend.Falling:
        return (
          <TrendingDown
            sx={{
              fontSize: iconSize,
              color: 'error.main',
              fontWeight: 'bold',
            }}
          />
        );
      case LevelTrend.Holding:
        return (
          <TrendingFlat
            sx={{
              fontSize: iconSize,
              color: 'info.main',
            }}
          />
        );
      case LevelTrend.None:
      default:
        return (
          <Remove
            sx={{
              fontSize: iconSize,
              color: 'text.disabled',
              opacity: 0.3,
            }}
          />
        );
    }
  };

  return (
    <Tooltip title={trendDescriptions[trend]} arrow placement="top">
      <Box
        sx={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          minWidth: iconSize + 4,
          minHeight: iconSize + 4,
        }}
      >
        {getTrendDisplay()}
      </Box>
    </Tooltip>
  );
}
