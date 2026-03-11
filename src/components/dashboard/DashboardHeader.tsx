import { Box, Typography, useTheme } from '@mui/material';
import { LiveTime } from '../common/LiveTime';
import { LiveIndicator } from '../common/LiveIndicator';
import { useGaugeDataContext } from '../../context/GaugeDataContext';

export function DashboardHeader() {
  const theme = useTheme();
  const { isLoading } = useGaugeDataContext();

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'flex-end',
        alignItems: 'center',
        mb: 1.5,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Typography
            variant="caption"
            sx={{ color: theme.palette.text.secondary }}
          >
            Updated
          </Typography>
          <LiveTime
            showSeconds={false}
            variant="caption"
            color="textSecondary"
          />
        </Box>
        <LiveIndicator isLive={!isLoading} lastUpdated={null} />
      </Box>
    </Box>
  );
}
