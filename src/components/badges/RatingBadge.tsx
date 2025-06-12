import React from 'react';
import { Chip, Box, useTheme } from '@mui/material';
import { waterGradients } from '../../theme/waterTheme';
import { 
  Looks6, 
  LooksOne, 
  LooksTwo, 
  Looks3, 
  Looks4, 
  Looks5,
  SportsScore,
  Pool,
} from '@mui/icons-material';

interface RatingBadgeProps {
  rating: string;
  size?: 'small' | 'medium';
  animated?: boolean;
}

export function RatingBadge({ rating, size = 'small', animated = true }: RatingBadgeProps) {
  const theme = useTheme();

  const getRatingColor = (rating: string): { gradient: string; color: string } => {
    if (rating.includes('V')) {
      return { gradient: waterGradients.danger, color: theme.palette.error.main };
    }
    if (rating.includes('IV')) {
      return { gradient: waterGradients.rapid, color: theme.palette.warning.main };
    }
    if (rating.includes('III')) {
      return { gradient: waterGradients.medium, color: theme.palette.info.main };
    }
    if (rating.includes('II')) {
      return { gradient: waterGradients.shallow, color: theme.palette.success.main };
    }
    if (rating === 'A' || rating === 'PLAY') {
      return { gradient: waterGradients.optimal, color: theme.palette.success.light };
    }
    return { gradient: waterGradients.shallow, color: theme.palette.primary.main };
  };

  const getRatingIcon = () => {
    if (rating === 'A' || rating === 'PLAY') return <Pool sx={{ fontSize: 16 }} />;
    if (rating.includes('V+')) return <SportsScore sx={{ fontSize: 16 }} />;
    if (rating.includes('V')) return <Looks5 sx={{ fontSize: 16 }} />;
    if (rating.includes('IV')) return <Looks4 sx={{ fontSize: 16 }} />;
    if (rating.includes('III')) return <Looks3 sx={{ fontSize: 16 }} />;
    if (rating.includes('II')) return <LooksTwo sx={{ fontSize: 16 }} />;
    if (rating.includes('I')) return <LooksOne sx={{ fontSize: 16 }} />;
    return null;
  };

  const { gradient, color } = getRatingColor(rating);

  return (
    <Box
      sx={{
        display: 'inline-flex',
        position: 'relative',
        ...(animated && {
          '&:hover .rating-chip': {
            transform: 'scale(1.05)',
            boxShadow: `0 0 20px ${color}40`,
          },
        }),
      }}
    >
      <Chip
        className="rating-chip"
        icon={getRatingIcon()}
        label={rating}
        size={size}
        sx={{
          background: gradient,
          color: '#fff',
          fontWeight: 600,
          fontSize: size === 'small' ? '0.75rem' : '0.875rem',
          letterSpacing: '0.5px',
          border: 'none',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '& .MuiChip-icon': {
            color: '#fff',
          },
          ...(animated && {
            animation: 'pulse 3s ease-in-out infinite',
            '@keyframes pulse': {
              '0%, 100%': {
                opacity: 0.9,
              },
              '50%': {
                opacity: 1,
              },
            },
          }),
        }}
      />
    </Box>
  );
}