import { useState } from 'react';
import { Box, IconButton, useTheme } from '@mui/material';
import { FilterList } from '@mui/icons-material';
import { DashboardSidebar } from './DashboardSidebar';
import { DashboardHeader } from './DashboardHeader';
import { Outlet } from 'react-router-dom';

export function DashboardLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <DashboardSidebar
        mobileOpen={mobileOpen}
        onMobileClose={() => setMobileOpen(false)}
      />
      
      <Box 
        component="main" 
        sx={{ 
          flexGrow: 1,
          minHeight: '100vh',
          backgroundColor: theme.palette.mode === 'dark' 
            ? 'rgb(17, 24, 39)' 
            : 'rgb(249, 250, 251)',
        }}
      >
        {/* Mobile filter button */}
        <Box sx={{ 
          display: { xs: 'block', md: 'none' }, 
          position: 'fixed',
          bottom: 16,
          right: 16,
          zIndex: 1000
        }}>
          <IconButton 
            onClick={handleDrawerToggle}
            sx={{ 
              bgcolor: theme.palette.primary.main,
              color: 'white',
              '&:hover': {
                bgcolor: theme.palette.primary.dark,
              },
              width: 56,
              height: 56,
              boxShadow: theme.shadows[4],
            }}
          >
            <FilterList />
          </IconButton>
        </Box>

        <DashboardHeader />
        <Box sx={{ p: 3 }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
