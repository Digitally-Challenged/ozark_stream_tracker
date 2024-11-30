import React from 'react';
import { Box, Typography, Table, TableBody, TableRow, TableCell } from '@mui/material';

interface InfoTooltipProps {
  type: 'size' | 'correlation' | 'level';
  value: string;
}

const getLevelInfo = (level: string) => {
  const levelMap = {
    'X': {
      name: 'Too Low',
      color: '#d32f2f',
      description: 'Creek is too low for fun paddling.'
    },
    'L': {
      name: 'Low',
      color: '#ed6c02',
      description: 'Creek is low but paddlable. May have to drag/portage in places.'
    },
    'O': {
      name: 'Optimal',
      color: '#2e7d32',
      description: 'Creek is perfect for paddling. The ratings listed are for this range.'
    },
    'H': {
      name: 'High/Flood',
      color: '#0288d1',
      description: 'Creek is high and potentially very dangerous. Many more hazards are present in this range and ratings typically are tougher than what is listed.'
    }
  };
  return levelMap[level as keyof typeof levelMap] || null;
};

// ... rest of the existing InfoTooltip component code ...

export default function InfoTooltip({ type, value }: InfoTooltipProps) {
  const renderLevelContent = () => {
    const info = getLevelInfo(value);
    if (!info) return null;

    return (
      <Box>
        <Box display="flex" alignItems="center" gap={1} mb={1}>
          <Typography variant="subtitle1" fontWeight="bold">
            {info.name}
          </Typography>
          <Box
            sx={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              backgroundColor: info.color
            }}
          />
        </Box>
        <Typography variant="body2">
          {info.description}
        </Typography>
      </Box>
    );
  };

  // ... rest of the existing component code ...
}