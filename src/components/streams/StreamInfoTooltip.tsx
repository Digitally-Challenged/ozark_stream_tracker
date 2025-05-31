import { Box, Typography, useTheme } from '@mui/material';
import {
  ArrowDownwardOutlined,
  ArrowUpwardOutlined,
  RemoveOutlined,
} from '@mui/icons-material';
import {
  getSizeDefinition,
  getCorrelationDefinition,
  getLevelDefinition,
  getRatingDefinition,
  sizeDefinitions,
  correlationDefinitions,
} from '../../types/streamDefinitions';
import { LevelTrend } from '../../types/stream';

interface InfoTooltipProps {
  type: 'size' | 'correlation' | 'level' | 'rating';
  value: string;
  trend?: LevelTrend;
}

export default function InfoTooltip({ type, value, trend }: InfoTooltipProps) {
  const theme = useTheme();

  const renderTrendIcon = () => {
    if (!trend) return null;

    const iconProps = {
      size: 16,
      // strokeWidth: 2.5 // strokeWidth is not directly applicable to MUI outlined icons this way
    };

    switch (trend) {
      case LevelTrend.Rising:
        return (
          <ArrowUpwardOutlined
            sx={{ fontSize: iconProps.size, color: theme.palette.success.main }}
          />
        );
      case LevelTrend.Falling:
        return (
          <ArrowDownwardOutlined
            sx={{ fontSize: iconProps.size, color: theme.palette.error.main }}
          />
        );
      case LevelTrend.Holding:
        return (
          <RemoveOutlined
            sx={{
              fontSize: iconProps.size,
              color: theme.palette.text.secondary,
            }}
          />
        );
      default:
        return null;
    }
  };

  const renderLevelContent = () => {
    const levelKey =
      value === 'X'
        ? 'tooLow'
        : value === 'L'
          ? 'low'
          : value === 'O'
            ? 'optimal'
            : value === 'H'
              ? 'high'
              : null;

    if (!levelKey) return null;
    const info = getLevelDefinition(levelKey);

    return (
      <Box sx={{ p: 1 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            mb: 1,
          }}
        >
          <Typography
            variant="subtitle1"
            sx={{
              fontWeight: 600,
              color: theme.palette.text.primary,
            }}
          >
            {info.name}
          </Typography>
          <Box
            sx={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              bgcolor: info.color,
            }}
          />
          {renderTrendIcon()}
        </Box>
        <Typography
          variant="body2"
          sx={{ color: theme.palette.text.secondary }}
        >
          {info.description}
        </Typography>
        {trend && trend !== LevelTrend.None && (
          <Typography
            variant="body2"
            sx={{
              mt: 1,
              color:
                trend === LevelTrend.Rising
                  ? theme.palette.success.main
                  : trend === LevelTrend.Falling
                    ? theme.palette.error.main
                    : theme.palette.text.secondary,
            }}
          >
            Level is {trend.toLowerCase()}
          </Typography>
        )}
      </Box>
    );
  };

  const renderSizeContent = () => {
    const info = getSizeDefinition(value as keyof typeof sizeDefinitions);
    return (
      <Box sx={{ p: 1 }}>
        <Typography
          variant="subtitle1"
          sx={{
            fontWeight: 600,
            color: theme.palette.text.primary,
            mb: 1,
          }}
        >
          {info.name}
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          <Typography
            variant="body2"
            sx={{ color: theme.palette.text.secondary }}
          >
            Width: {info.width}
          </Typography>
          <Typography
            variant="body2"
            sx={{ color: theme.palette.text.secondary }}
          >
            Watershed: {info.watershed}
          </Typography>
          <Typography
            variant="body2"
            sx={{ color: theme.palette.text.secondary }}
          >
            Rain Rate: {info.rainRate}
          </Typography>
          <Typography
            variant="body2"
            sx={{ color: theme.palette.text.secondary }}
          >
            Window: {info.window}
          </Typography>
          <Typography
            variant="body2"
            sx={{
              mt: 1,
              color: theme.palette.text.primary,
            }}
          >
            {info.description}
          </Typography>
        </Box>
      </Box>
    );
  };

  const renderCorrelationContent = () => {
    const info = getCorrelationDefinition(
      value as keyof typeof correlationDefinitions
    );
    return (
      <Box sx={{ p: 1 }}>
        <Typography
          variant="subtitle1"
          sx={{
            fontWeight: 600,
            color: theme.palette.text.primary,
            mb: 1,
          }}
        >
          {info.name}
        </Typography>
        <Typography
          variant="body2"
          sx={{ color: theme.palette.text.secondary }}
        >
          {info.description}
        </Typography>
      </Box>
    );
  };

  const renderRatingContent = () => {
    const info = getRatingDefinition(value);
    return (
      <Box sx={{ p: 1, maxWidth: 300 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            mb: 1,
          }}
        >
          <Typography
            variant="subtitle1"
            sx={{
              fontWeight: 600,
              color: theme.palette.text.primary,
            }}
          >
            {info.name}
          </Typography>
          <Box
            sx={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              bgcolor: info.color,
            }}
          />
        </Box>
        <Typography
          variant="body2"
          sx={{
            color: theme.palette.text.secondary,
            lineHeight: 1.5,
          }}
        >
          {info.description}
        </Typography>
      </Box>
    );
  };

  switch (type) {
    case 'level':
      return renderLevelContent();
    case 'size':
      return renderSizeContent();
    case 'correlation':
      return renderCorrelationContent();
    case 'rating':
      return renderRatingContent();
    default:
      return null;
  }
}
