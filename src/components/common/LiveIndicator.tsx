// src/components/common/LiveIndicator.tsx
import { Box, Typography, keyframes } from '@mui/material';
import { FiberManualRecord } from '@mui/icons-material';

const pulse = keyframes`
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(0.9);
  }
`;

const glow = keyframes`
  0%, 100% {
    box-shadow: 0 0 4px currentColor;
  }
  50% {
    box-shadow: 0 0 12px currentColor, 0 0 20px currentColor;
  }
`;

interface LiveIndicatorProps {
  isLive?: boolean;
  lastUpdated?: Date | null;
}

export function LiveIndicator({ isLive = true, lastUpdated }: LiveIndicatorProps) {
  return (
    <Box
      sx={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 0.75,
        px: 1.5,
        py: 0.5,
        borderRadius: 3,
        background: (theme) =>
          theme.palette.mode === 'dark'
            ? 'rgba(46, 125, 50, 0.15)'
            : 'rgba(46, 125, 50, 0.1)',
        border: '1px solid',
        borderColor: isLive ? 'success.main' : 'text.disabled',
      }}
    >
      <FiberManualRecord
        sx={{
          fontSize: 10,
          color: isLive ? 'success.main' : 'text.disabled',
          animation: isLive ? `${pulse} 2s ease-in-out infinite` : 'none',
          borderRadius: '50%',
          ...(isLive && {
            animation: `${pulse} 2s ease-in-out infinite, ${glow} 2s ease-in-out infinite`,
          }),
        }}
      />
      <Typography
        variant="caption"
        sx={{
          fontWeight: 600,
          letterSpacing: '0.05em',
          color: isLive ? 'success.main' : 'text.disabled',
          textTransform: 'uppercase',
          fontSize: '0.7rem',
        }}
      >
        {isLive ? 'LIVE' : 'OFFLINE'}
      </Typography>
      {lastUpdated && (
        <Typography
          variant="caption"
          sx={{
            color: 'text.secondary',
            fontSize: '0.65rem',
            ml: 0.5,
          }}
        >
          • {lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Typography>
      )}
    </Box>
  );
}
