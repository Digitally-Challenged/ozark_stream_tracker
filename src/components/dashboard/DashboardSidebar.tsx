import { 
  Box, 
  Drawer, 
  Typography, 
  Divider, 
  FormControl, 
  FormGroup,
  FormControlLabel,
  Checkbox,
  Slider,
  IconButton,
  useTheme,
  useMediaQuery,
  Radio,
  RadioGroup
} from '@mui/material';
import { FilterList, Close } from '@mui/icons-material';
import { useState } from 'react';

interface DashboardSidebarProps {
  mobileOpen: boolean;
  onMobileClose: () => void;
  width?: number;
}

export function DashboardSidebar({ 
  mobileOpen = false, 
  onMobileClose, 
  width = 280 
}: DashboardSidebarProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [filters, setFilters] = useState({
    difficulty: 'all',
    flowRange: [0, 100],
    features: {
      playSpots: false,
      waterfalls: false,
      rapids: false,
      slides: false
    },
    status: {
      running: true,
      tooLow: false,
      tooHigh: false,
      unknown: false
    }
  });

  const handleDifficultyChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFilters(prev => ({
      ...prev,
      difficulty: event.target.value
    }));
  };

  const handleFlowRangeChange = (event: Event, newValue: number | number[]) => {
    setFilters(prev => ({
      ...prev,
      flowRange: newValue as number[]
    }));
  };

  const handleFeatureToggle = (feature: keyof typeof filters.features) => {
    setFilters(prev => ({
      ...prev,
      features: {
        ...prev.features,
        [feature]: !prev.features[feature]
      }
    }));
  };

  const handleStatusToggle = (status: keyof typeof filters.status) => {
    setFilters(prev => ({
      ...prev,
      status: {
        ...prev.status,
        [status]: !prev.status[status]
      }
    }));
  };

  const content = (
    <Box
      sx={{
        height: '100%',
        p: 3,
        backgroundColor: theme.palette.mode === 'dark' 
          ? 'rgba(255, 255, 255, 0.05)' 
          : 'rgba(0, 0, 0, 0.02)',
      }}
    >
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        mb: 3
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FilterList />
          <Typography variant="h6" color="text.primary">
            Filters
          </Typography>
        </Box>
        {isMobile && (
          <IconButton onClick={onMobileClose} color="inherit">
            <Close />
          </IconButton>
        )}
      </Box>

      <Divider sx={{ mb: 3 }} />

      {/* Difficulty Level */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="subtitle2" 
          color="text.secondary"
          sx={{ mb: 2 }}
        >
          Difficulty Level
        </Typography>
        <FormControl>
          <RadioGroup
            value={filters.difficulty}
            onChange={handleDifficultyChange}
          >
            <FormControlLabel 
              value="all" 
              control={<Radio size="small" />} 
              label="All Classes" 
            />
            <FormControlLabel 
              value="beginner" 
              control={<Radio size="small" />} 
              label="Beginner (I-II)" 
            />
            <FormControlLabel 
              value="intermediate" 
              control={<Radio size="small" />} 
              label="Intermediate (III)" 
            />
            <FormControlLabel 
              value="advanced" 
              control={<Radio size="small" />} 
              label="Advanced (IV-V)" 
            />
          </RadioGroup>
        </FormControl>
      </Box>

      {/* Flow Range */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="subtitle2" 
          color="text.secondary"
          sx={{ mb: 2 }}
        >
          Flow Range (CFS)
        </Typography>
        <Slider
          value={filters.flowRange}
          onChange={handleFlowRangeChange}
          valueLabelDisplay="auto"
          min={0}
          max={1000}
          sx={{ ml: 1 }}
        />
      </Box>

      {/* Features */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="subtitle2" 
          color="text.secondary"
          sx={{ mb: 2 }}
        >
          Features
        </Typography>
        <FormGroup>
          {Object.entries(filters.features).map(([key, checked]) => (
            <FormControlLabel
              key={key}
              control={
                <Checkbox 
                  size="small"
                  checked={checked}
                  onChange={() => handleFeatureToggle(key as keyof typeof filters.features)}
                />
              }
              label={key.charAt(0).toUpperCase() + key.slice(1)}
            />
          ))}
        </FormGroup>
      </Box>

      {/* Status */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="subtitle2" 
          color="text.secondary"
          sx={{ mb: 2 }}
        >
          Status
        </Typography>
        <FormGroup>
          {Object.entries(filters.status).map(([key, checked]) => (
            <FormControlLabel
              key={key}
              control={
                <Checkbox 
                  size="small"
                  checked={checked}
                  onChange={() => handleStatusToggle(key as keyof typeof filters.status)}
                />
              }
              label={key.charAt(0).toUpperCase() + key.slice(1)}
            />
          ))}
        </FormGroup>
      </Box>
    </Box>
  );

  return (
    <Box
      component="nav"
      sx={{
        width: { md: width },
        flexShrink: { md: 0 }
      }}
    >
      {isMobile ? (
        <Drawer
          variant="temporary"
          anchor="left"
          open={mobileOpen}
          onClose={onMobileClose}
          ModalProps={{
            keepMounted: true // Better mobile performance
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { 
              width,
              boxSizing: 'border-box',
              backgroundColor: theme.palette.background.default
            }
          }}
        >
          {content}
        </Drawer>
      ) : (
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { 
              width,
              boxSizing: 'border-box',
              position: 'relative',
              height: '100%',
              backgroundColor: 'transparent'
            }
          }}
          open
        >
          {content}
        </Drawer>
      )}
    </Box>
  );
}
