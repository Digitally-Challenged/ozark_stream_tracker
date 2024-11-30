import { Box, Typography, Paper, Grid, useTheme, Tooltip } from '@mui/material';
import { WaterDrop, Waves, Terrain, AccessTime } from '@mui/icons-material';
import { keyframes } from '@mui/system';

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

const pulseIcon = keyframes`
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
`;

export function DashboardHeader() {
  const theme = useTheme();

  const statsData = [
    {
      label: 'Total Runs',
      value: '93',
      icon: WaterDrop,
      color: theme.palette.primary.main,
      tooltip: 'Total number of whitewater runs'
    },
    {
      label: 'Beginner Runs',
      value: '87',
      icon: Waves,
      color: theme.palette.success.main,
      tooltip: 'Class I-II runs'
    },
    {
      label: 'Advanced Runs',
      value: '40',
      icon: Terrain,
      color: theme.palette.warning.main,
      tooltip: 'Class IV-V runs'
    },
    {
      label: 'Last Updated',
      value: '3:25:16 PM',
      icon: AccessTime,
      color: theme.palette.info.main,
      tooltip: 'Most recent gauge reading update'
    }
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Grid container spacing={3}>
        {statsData.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={stat.label}>
            <Tooltip title={stat.tooltip} arrow>
              <Paper
                sx={{
                  p: 3,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                  bgcolor: theme.palette.mode === 'dark' 
                    ? 'rgba(255, 255, 255, 0.05)' 
                    : 'rgba(0, 0, 0, 0.02)',
                  backdropFilter: 'blur(10px)',
                  transition: 'all 0.3s ease-in-out',
                  animation: `${fadeInUp} 0.5s ease-out ${index * 0.1}s`,
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    bgcolor: theme.palette.mode === 'dark'
                      ? 'rgba(255, 255, 255, 0.08)'
                      : 'rgba(0, 0, 0, 0.04)',
                    boxShadow: theme.shadows[8],
                  },
                }}
                elevation={0}
              >
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 2,
                    bgcolor: theme.palette.mode === 'dark'
                      ? `${stat.color}15`
                      : `${stat.color}15`,
                    color: stat.color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    '&:hover': {
                      animation: `${pulseIcon} 1s ease-in-out infinite`
                    }
                  }}
                >
                  <stat.icon sx={{ fontSize: 24 }} />
                </Box>
                <Box>
                  <Typography 
                    variant="body2"
                    sx={{ 
                      color: theme.palette.text.secondary,
                      fontWeight: 500
                    }}
                  >
                    {stat.label}
                  </Typography>
                  <Typography 
                    variant="h5" 
                    sx={{ 
                      mt: 0.5,
                      color: theme.palette.text.primary,
                      fontWeight: 600
                    }}
                  >
                    {stat.value}
                  </Typography>
                </Box>
              </Paper>
            </Tooltip>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}