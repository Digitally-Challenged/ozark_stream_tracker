import { Box, Typography, Paper, Grid, useTheme, Tooltip } from '@mui/material';
import { WaterDrop, Waves, Terrain, AccessTime } from '@mui/icons-material';
import { keyframes } from '@mui/system';
import { LiveTime } from '../common/LiveTime';

const fadeInUp = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

// Pulse animation available for future use
// const pulseIcon = keyframes`...`;

export function DashboardHeader() {
  const theme = useTheme();

  const statsData = [
    {
      label: 'Total Runs',
      value: '93',
      icon: WaterDrop,
      color: theme.palette.primary.main,
      tooltip: 'Total number of whitewater runs',
    },
    {
      label: 'Beginner Runs',
      value: '87',
      icon: Waves,
      color: theme.palette.success.main,
      tooltip: 'Class I-II runs',
    },
    {
      label: 'Advanced Runs',
      value: '40',
      icon: Terrain,
      color: theme.palette.warning.main,
      tooltip: 'Class IV-V runs',
    },
    {
      label: 'Last Updated',
      value: 'live',
      icon: AccessTime,
      color: theme.palette.info.main,
      tooltip: 'Current time - gauges refresh every 15 minutes',
    },
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Grid container spacing={3}>
        {statsData.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={stat.label}>
            <Tooltip title={stat.tooltip} arrow>
              <Box>
                <Paper
                  elevation={0}
                  sx={{
                    p: 3,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 2,
                    height: '100%',
                    animation: `${fadeInUp} 0.5s ease-out ${index * 0.1}s both`,
                    backgroundColor: theme.palette.background.paper,
                    borderLeft: `3px solid ${stat.color}`,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: theme.shadows[4],
                      '& .stat-icon': {
                        transform: 'rotate(360deg) scale(1.2)',
                      },
                    },
                  }}
                >
                  <Box
                    className="stat-icon"
                    sx={{
                      p: 1.5,
                      borderRadius: 2,
                      background: `linear-gradient(135deg, ${stat.color}20 0%, ${stat.color}10 100%)`,
                      color: stat.color,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'all 0.3s ease',
                      border: `1px solid ${stat.color}30`,
                    }}
                  >
                    <stat.icon sx={{ fontSize: 24 }} />
                  </Box>
                  <Box>
                    <Typography
                      variant="body2"
                      sx={{
                        color: theme.palette.text.secondary,
                        fontWeight: 500,
                      }}
                    >
                      {stat.label}
                    </Typography>
                    <Typography
                      variant="h5"
                      sx={{
                        mt: 0.5,
                        color: theme.palette.text.primary,
                        fontWeight: 600,
                      }}
                    >
                      {stat.value === 'live' ? (
                        <LiveTime
                          showSeconds={true}
                          variant="body1"
                          color="textPrimary"
                        />
                      ) : (
                        stat.value
                      )}
                    </Typography>
                  </Box>
                </Paper>
              </Box>
            </Tooltip>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
