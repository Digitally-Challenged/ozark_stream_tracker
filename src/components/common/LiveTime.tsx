import { useState, useEffect } from 'react';
import { Typography, Box, Tooltip } from '@mui/material';
import { AccessTime } from '@mui/icons-material';
import { format } from 'date-fns';

interface LiveTimeProps {
  showSeconds?: boolean;
  showIcon?: boolean;
  variant?: 'body1' | 'body2' | 'caption';
  color?: 'primary' | 'secondary' | 'textPrimary' | 'textSecondary';
  updateInterval?: number;
}

/**
 * Component that displays the current time and updates it in real-time
 */
export function LiveTime({ 
  showSeconds = true, 
  showIcon = false, 
  variant = 'body2',
  color = 'textSecondary',
  updateInterval = 1000 
}: LiveTimeProps) {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, updateInterval);

    return () => clearInterval(timer);
  }, [updateInterval]);

  const timeFormat = showSeconds ? 'HH:mm:ss' : 'HH:mm';
  const fullFormat = showSeconds ? 'PPpp' : 'PPp';

  return (
    <Tooltip title={format(currentTime, fullFormat)}>
      <Box display="flex" alignItems="center" gap={0.5}>
        {showIcon && (
          <AccessTime 
            sx={{ 
              fontSize: variant === 'caption' ? 14 : 16,
              color: 'text.secondary'
            }} 
          />
        )}
        <Typography variant={variant} color={color}>
          {format(currentTime, timeFormat)}
        </Typography>
      </Box>
    </Tooltip>
  );
}