import React from 'react';
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
  variant?: 'default' | 'outlined';
  animated?: boolean;
}

const sizeInfo = {
  XS: { label: 'Extra Small', icon: WaterDrop, color: '#e3f2fd', description: 'Tiny creek, very technical' },
  VS: { label: 'Very Small', icon: Opacity, color: '#bbdefb', description: 'Small creek, requires precision' },
  S: { label: 'Small', icon: Water, color: '#90caf9', description: 'Small river, good for practice' },
  M: { label: 'Medium', icon: Waves, color: '#64b5f6', description: 'Medium river, versatile runs' },
  L: { label: 'Large', icon: Pool, color: '#42a5f5', description: 'Large river, big water' },
  H: { label: 'Huge', icon: Tsunami, color: '#2196f3', description: 'Very large river' },
  DC: { label: 'Dam Controlled', icon: Pool, color: '#1e88e5', description: 'Flow controlled by dam' },
  A: { label: 'Always Runnable', icon: Waves, color: '#1976d2', description: 'Consistent flow year-round' },
};

export function SizeBadge({ size, variant = 'default', animated = true }: SizeBadgeProps) {
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
            color: theme.palette.mode === 'dark' ? info.color : info.color.replace('#', '#').slice(0, -2) + 'ff',
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