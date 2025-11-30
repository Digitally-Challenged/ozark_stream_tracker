// src/components/common/LiquidFillBar.tsx
import { Box, Typography, keyframes, Tooltip } from '@mui/material';
import { LevelStatus } from '../../types/stream';

const wave = keyframes`
  0% { transform: translateX(0) translateZ(0) scaleY(1); }
  50% { transform: translateX(-25%) translateZ(0) scaleY(0.8); }
  100% { transform: translateX(-50%) translateZ(0) scaleY(1); }
`;

const fillAnimation = keyframes`
  from { height: 0%; }
  to { height: var(--fill-height); }
`;

interface LiquidFillBarProps {
  currentValue: number;
  minValue: number;
  maxValue: number;
  status: LevelStatus;
  showLabel?: boolean;
  height?: number;
}

const STATUS_COLORS: Record<LevelStatus, { primary: string; secondary: string }> = {
  [LevelStatus.Optimal]: { primary: '#2e7d32', secondary: '#4caf50' },
  [LevelStatus.Low]: { primary: '#ed6c02', secondary: '#ff9800' },
  [LevelStatus.High]: { primary: '#0288d1', secondary: '#03a9f4' },
  [LevelStatus.TooLow]: { primary: '#d32f2f', secondary: '#f44336' },
};

export function LiquidFillBar({
  currentValue,
  minValue,
  maxValue,
  status,
  showLabel = true,
  height = 60,
}: LiquidFillBarProps) {
  const colors = STATUS_COLORS[status];

  // Calculate fill percentage (clamped between 0 and 100)
  const range = maxValue - minValue;
  const fillPercent = Math.min(100, Math.max(0, ((currentValue - minValue) / range) * 100));

  const tooltipText = `${currentValue.toFixed(2)} ft (${fillPercent.toFixed(0)}% of range)`;

  return (
    <Tooltip title={tooltipText} arrow placement="top">
      <Box
        sx={{
          position: 'relative',
          width: '100%',
          height: height,
          borderRadius: 2,
          overflow: 'hidden',
          background: (theme) =>
            theme.palette.mode === 'dark'
              ? 'rgba(255, 255, 255, 0.05)'
              : 'rgba(0, 0, 0, 0.05)',
          border: '1px solid',
          borderColor: (theme) =>
            theme.palette.mode === 'dark'
              ? 'rgba(255, 255, 255, 0.1)'
              : 'rgba(0, 0, 0, 0.1)',
        }}
      >
        {/* Fill level */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: `${fillPercent}%`,
            background: `linear-gradient(180deg, ${colors.secondary} 0%, ${colors.primary} 100%)`,
            transition: 'height 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
            '--fill-height': `${fillPercent}%`,
            animation: `${fillAnimation} 0.8s cubic-bezier(0.4, 0, 0.2, 1)`,
          }}
        >
          {/* Wave effect on top */}
          <Box
            sx={{
              position: 'absolute',
              top: -5,
              left: 0,
              width: '200%',
              height: 10,
              background: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 88.7'%3E%3Cpath d='M800 56.9c-155.5 0-204.9-50-405.5-49.9-200 0-250 49.9-394.5 49.9v31.8h800v-.2-31.6z' fill='${encodeURIComponent(colors.secondary)}'/%3E%3C/svg%3E")`,
              backgroundSize: '50% 100%',
              animation: `${wave} 3s linear infinite`,
              opacity: 0.6,
            }}
          />
        </Box>

        {/* Labels */}
        {showLabel && (
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              zIndex: 1,
              textAlign: 'center',
            }}
          >
            <Typography
              sx={{
                fontWeight: 700,
                fontSize: '0.9rem',
                color: (theme) =>
                  fillPercent > 50 ? '#fff' : theme.palette.text.primary,
                textShadow: fillPercent > 50 ? '0 1px 2px rgba(0,0,0,0.3)' : 'none',
              }}
            >
              {currentValue.toFixed(1)} ft
            </Typography>
          </Box>
        )}

        {/* Min/Max markers */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 4,
            left: 4,
            fontSize: '0.6rem',
            color: (theme) => theme.palette.text.secondary,
            opacity: 0.7,
          }}
        >
          {minValue}
        </Box>
        <Box
          sx={{
            position: 'absolute',
            top: 4,
            right: 4,
            fontSize: '0.6rem',
            color: (theme) => theme.palette.text.secondary,
            opacity: 0.7,
          }}
        >
          {maxValue}
        </Box>
      </Box>
    </Tooltip>
  );
}
