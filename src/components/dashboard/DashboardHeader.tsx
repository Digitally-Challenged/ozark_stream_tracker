import React from 'react';
import { Box, Typography, Paper, Grid, useTheme, Tooltip } from '@mui/material';
import { Droplets, Waves, Mountain, Timer } from 'lucide-react';
import { streams } from '../../data/streamData';
import { format } from 'date-fns';

export function DashboardHeader() {
  const theme = useTheme();
  const lastUpdate = new Date();

  // Calculate stats
  const playSpots = streams.filter(s => s.rating === 'PLAY').length;
  const beginnerRuns = streams.filter(s => s.rating.startsWith('I') || s.rating.startsWith('II')).length;
  const advancedRuns = streams.filter(s => s.rating.includes('IV') || s.rating.includes('V')).length;

  const statsData = [
    {
      label: 'Total Runs',
      value: streams.length.toString(),
      icon: Droplets,
      color: theme.palette.primary.main,
      tooltip: 'Total number of whitewater runs'
    },
    {
      label: 'Play Spots',
      value: playSpots.toString(),
      icon: Waves,
      color: theme.palette.success.main,
      tooltip: 'Dedicated playboating locations'
    },
    {
      label: 'Advanced Runs',
      value: advancedRuns.toString(),
      icon: Mountain,
      color: theme.palette.warning.main,
      tooltip: 'Class IV-V runs'
    },
    {
      label: 'Last Updated',
      value: format(lastUpdate, 'pp'),
      icon: Timer,
      color: theme.palette.info.main,
      tooltip: 'Most recent gauge reading update'
    }
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Whitewater Dashboard
      </Typography>
      <Grid container spacing={3}>
        {statsData.map((stat) => (
          <Grid item xs={12} sm={6} md={3} key={stat.label}>
            <Tooltip title={stat.tooltip} arrow>
              <Paper
                sx={{
                  p: 3,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                  bgcolor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'white',
                  transition: 'transform 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                  },
                }}
                elevation={theme.palette.mode === 'dark' ? 2 : 1}
              >
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 2,
                    bgcolor: `${stat.color}15`,
                    color: stat.color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <stat.icon size={24} />
                </Box>
                <Box>
                  <Typography color="textSecondary" variant="body2">
                    {stat.label}
                  </Typography>
                  <Typography variant="h5" sx={{ mt: 0.5 }}>
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