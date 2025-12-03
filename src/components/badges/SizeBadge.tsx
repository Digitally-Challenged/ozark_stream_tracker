// React import not needed in modern React
import { Chip, Box, Tooltip, useTheme } from '@mui/material';
import {
  Opacity,
  Water,
  Waves,
  Pool,
  WaterDrop,
  Tsunami,
} from '@mui/icons-material';

interface SizeBadgeProps {
  size: string;
  variant?: 'filled' | 'outlined';
  animated?: boolean;
}

const sizeInfo = {
  XS: {
    label: 'Extra Small',
    icon: WaterDrop,
    color: '#64b5f6',
    description:
      'XS: < 20ft wide, < 1 sq mi watershed, 1.5 in/hr rain rate, 3-6 hr window to "too low"',
  },
  VS: {
    label: 'Very Small',
    icon: Opacity,
    color: '#42a5f5',
    description:
      'VS: 20-30ft wide, 1-4 sq mi watershed, 1.0 in/hr rain rate, 6-12 hr window to "too low"',
  },
  S: {
    label: 'Small',
    icon: Water,
    color: '#2196f3',
    description:
      'S: 30-40ft wide, 4-10 sq mi watershed, 0.75 in/hr rain rate, 1 day window to "too low"',
  },
  M: {
    label: 'Medium',
    icon: Waves,
    color: '#1e88e5',
    description:
      'M: 40-75ft wide, 10-25 sq mi watershed, 0.5 in/hr rain rate, 1-2 day window to "too low"',
  },
  L: {
    label: 'Large',
    icon: Pool,
    color: '#1976d2',
    description:
      'L: > 75ft wide, > 25 sq mi watershed, 0.2 in/hr rain rate, 2-5 day window to "too low"',
  },
  H: {
    label: 'Huge',
    icon: Tsunami,
    color: '#1565c0',
    description:
      'H: > 150ft wide, > 75 sq mi watershed, 0.1 in/hr rain rate, 5+ day window to "too low"',
  },
  DC: {
    label: 'Dam Controlled',
    icon: Pool,
    color: '#0d47a1',
    description:
      'DC: Dam Controlled - Check Release Schedule! Flow depends on dam operations, not rainfall.',
  },
  A: {
    label: 'Always Runnable',
    icon: Waves,
    color: '#0d47a1',
    description:
      'A: Always Runs - Consistent flow year-round, typically spring-fed or large watershed',
  },
};

export function SizeBadge({
  size,
  variant = 'filled',
  animated = true,
}: SizeBadgeProps) {
  const theme = useTheme();
  const info = sizeInfo[size as keyof typeof sizeInfo] || sizeInfo.M;
  const Icon = info.icon;

  const getBackgroundColor = () => {
    if (theme.palette.mode === 'dark') {
      return variant === 'outlined' ? 'transparent' : info.color + '20';
    }
    return variant === 'outlined' ? 'transparent' : info.color + '30';
  };

  const getBorderColor = () => {
    if (theme.palette.mode === 'dark') {
      return info.color + '60';
    }
    return info.color;
  };

  return (
    <Tooltip title={info.description} arrow>
      <Box
        sx={{
          display: 'inline-flex',
          position: 'relative',
          ...(animated && {
            '&:hover .size-chip': {
              transform: 'scale(1.05) rotate(-2deg)',
              '& .MuiChip-icon': {
                animation: 'wave 1s ease-in-out infinite',
              },
            },
          }),
        }}
      >
        <Chip
          className="size-chip"
          icon={<Icon />}
          label={size}
          variant={variant}
          size="small"
          sx={{
            backgroundColor: getBackgroundColor(),
            borderColor: getBorderColor(),
            color:
              theme.palette.mode === 'dark'
                ? info.color
                : info.color.replace('#', '#').slice(0, -2) + 'ff',
            fontWeight: 600,
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '& .MuiChip-icon': {
              color: 'inherit',
              transition: 'all 0.3s',
            },
            '@keyframes wave': {
              '0%, 100%': {
                transform: 'translateY(0) rotate(0deg)',
              },
              '25%': {
                transform: 'translateY(-2px) rotate(-5deg)',
              },
              '75%': {
                transform: 'translateY(-2px) rotate(5deg)',
              },
            },
          }}
        />
      </Box>
    </Tooltip>
  );
}
