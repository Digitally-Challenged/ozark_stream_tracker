// React import not needed in modern React
import { Box, keyframes } from '@mui/material';
import {
  WaterDrop,
  Waves,
  Warning,
  TrendingUp,
  TrendingDown,
  Remove,
  Opacity,
} from '@mui/icons-material';
import { LevelStatus, LevelTrend } from '../../types/stream';

interface StreamConditionIconProps {
  status: LevelStatus;
  trend?: LevelTrend;
  size?: 'small' | 'medium' | 'large';
}

const ripple = keyframes`
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
`;

const float = keyframes`
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
`;

const pulse = keyframes`
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
`;

export function StreamConditionIcon({
  status,
  trend,
  size = 'medium',
}: StreamConditionIconProps) {
  const sizeMap = {
    small: 20,
    medium: 24,
    large: 32,
  };

  const iconSize = sizeMap[size];

  const getStatusIcon = () => {
    switch (status) {
      case LevelStatus.TooLow:
        return (
          <Box sx={{ position: 'relative', display: 'inline-flex' }}>
            <Opacity
              sx={{
                fontSize: iconSize,
                color: 'error.main',
                opacity: 0.5,
              }}
            />
            <Warning
              sx={{
                fontSize: iconSize * 0.5,
                color: 'error.main',
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                animation: `${pulse} 2s ease-in-out infinite`,
              }}
            />
          </Box>
        );
      case LevelStatus.Low:
        return (
          <WaterDrop
            sx={{
              fontSize: iconSize,
              color: 'warning.main',
              opacity: 0.7,
              animation: `${float} 3s ease-in-out infinite`,
            }}
          />
        );
      case LevelStatus.Optimal:
        return (
          <Box sx={{ position: 'relative', display: 'inline-flex' }}>
            <Waves
              sx={{
                fontSize: iconSize,
                color: 'success.main',
                animation: `${float} 2s ease-in-out infinite`,
              }}
            />
            <Box
              sx={{
                position: 'absolute',
                width: '100%',
                height: '100%',
                borderRadius: '50%',
                border: '2px solid',
                borderColor: 'success.main',
                animation: `${ripple} 2s ease-out infinite`,
              }}
            />
          </Box>
        );
      case LevelStatus.High:
        return (
          <Box sx={{ position: 'relative', display: 'inline-flex' }}>
            <Waves
              sx={{
                fontSize: iconSize,
                color: 'info.main',
                transform: 'scaleY(1.2)',
              }}
            />
            <Warning
              sx={{
                fontSize: iconSize * 0.4,
                color: 'warning.main',
                position: 'absolute',
                top: -2,
                right: -2,
                animation: `${pulse} 1s ease-in-out infinite`,
              }}
            />
          </Box>
        );
      default:
        return <Remove sx={{ fontSize: iconSize, color: 'text.disabled' }} />;
    }
  };

  const getTrendIcon = () => {
    if (!trend || trend === LevelTrend.None) return null;

    const trendIconProps = {
      sx: {
        fontSize: iconSize * 0.6,
        ml: 0.5,
      },
    };

    switch (trend) {
      case LevelTrend.Rising:
        return (
          <TrendingUp
            {...trendIconProps}
            sx={{ ...trendIconProps.sx, color: 'success.main' }}
          />
        );
      case LevelTrend.Falling:
        return (
          <TrendingDown
            {...trendIconProps}
            sx={{ ...trendIconProps.sx, color: 'error.main' }}
          />
        );
      case LevelTrend.Holding:
        return (
          <Remove
            {...trendIconProps}
            sx={{ ...trendIconProps.sx, color: 'text.secondary' }}
          />
        );
      default:
        return null;
    }
  };

  return (
    <Box
      sx={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 0.5,
        p: 1,
        borderRadius: 2,
        background: (theme) =>
          theme.palette.mode === 'dark'
            ? 'rgba(255, 255, 255, 0.05)'
            : 'rgba(0, 0, 0, 0.02)',
        backdropFilter: 'blur(10px)',
      }}
    >
      {getStatusIcon()}
      {getTrendIcon()}
    </Box>
  );
}
