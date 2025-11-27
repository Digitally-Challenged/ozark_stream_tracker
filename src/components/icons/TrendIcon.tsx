import { Box } from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Remove,
  HorizontalRule,
} from '@mui/icons-material';
import { LevelTrend } from '../../types/stream';

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
            titleAccess="↗️ Water level rising"
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
            titleAccess="↘️ Water level falling"
          />
        );
      case LevelTrend.Holding:
        return (
          <HorizontalRule
            sx={{
              fontSize: iconSize,
              color: 'warning.main',
            }}
            titleAccess="→ Water level stable"
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
            titleAccess="— No trend data"
          />
        );
    }
  };

  return (
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
  );
}