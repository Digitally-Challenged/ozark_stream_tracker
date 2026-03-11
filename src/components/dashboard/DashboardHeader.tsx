import { Box, Typography, useTheme } from '@mui/material';
import { WaterDrop } from '@mui/icons-material';
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
        justifyContent: 'space-between',
        alignItems: 'center',
        mb: 1.5,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <WaterDrop sx={{ fontSize: 18, color: theme.palette.primary.main }} />
        <Typography
          variant="body2"
          sx={{ fontWeight: 600, color: theme.palette.text.primary }}
        >
          93 Runs
        </Typography>
      </Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <LiveIndicator isLive={!isLoading} lastUpdated={null} />
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
      </Box>
    </Box>
  );
}
