// src/components/streams/StreamGroupHeader.tsx
import { Box, Typography, IconButton, Chip, useTheme } from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';
import { LevelStatus } from '../../types/stream';

interface StreamGroupHeaderProps {
  status: LevelStatus;
  count: number;
  expanded: boolean;
  onToggle: () => void;
}

const STATUS_CONFIG: Record<LevelStatus, { label: string; emoji: string; color: string }> = {
  [LevelStatus.Optimal]: { label: 'Optimal - Running Good', emoji: '🟢', color: '#2e7d32' },
  [LevelStatus.Low]: { label: 'Low - Runnable but Scraping', emoji: '🟡', color: '#ed6c02' },
  [LevelStatus.High]: { label: 'High - Running Fast', emoji: '🔵', color: '#0288d1' },
  [LevelStatus.TooLow]: { label: 'Too Low - Not Runnable', emoji: '🔴', color: '#d32f2f' },
};

export function StreamGroupHeader({
  status,
  count,
  expanded,
  onToggle,
}: StreamGroupHeaderProps) {
  const theme = useTheme();
  const config = STATUS_CONFIG[status];

  return (
    <Box
      onClick={onToggle}
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        p: 2,
        cursor: 'pointer',
        borderRadius: 1,
        bgcolor: theme.palette.mode === 'dark'
          ? 'rgba(255,255,255,0.05)'
          : 'rgba(0,0,0,0.02)',
        '&:hover': {
          bgcolor: theme.palette.mode === 'dark'
            ? 'rgba(255,255,255,0.08)'
            : 'rgba(0,0,0,0.04)',
        },
        borderLeft: `4px solid ${config.color}`,
        mb: 1,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography variant="h6" component="span">
          {config.emoji}
        </Typography>
        <Typography variant="subtitle1" fontWeight="medium">
          {config.label}
        </Typography>
        <Chip
          label={count}
          size="small"
          sx={{
            bgcolor: config.color,
            color: 'white',
            fontWeight: 'bold',
          }}
        />
      </Box>
      <IconButton size="small">
        {expanded ? <ExpandLess /> : <ExpandMore />}
      </IconButton>
    </Box>
  );
}
