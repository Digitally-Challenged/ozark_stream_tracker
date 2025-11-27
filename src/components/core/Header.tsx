import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  useTheme,
  Box,
  keyframes,
  alpha,
} from '@mui/material';
import {
  Kayaking,
  FilterList,
  DarkModeOutlined,
  LightModeOutlined,
  Waves,
  Refresh,
} from '@mui/icons-material';
import { useColorMode } from '../../context/ThemeContext';
import { useGaugeDataContext } from '../../context/GaugeDataContext';
import { waterGradients } from '../../theme/waterTheme';

interface HeaderProps {
  onFilterClick: () => void;
  filterOpen: boolean;
}

const float = keyframes`
  0%, 100% { transform: translateY(0) rotate(0deg); }
  25% { transform: translateY(-3px) rotate(-2deg); }
  75% { transform: translateY(-3px) rotate(2deg); }
`;

const wave = keyframes`
  0% { transform: translateX(0); }
  100% { transform: translateX(-100%); }
`;

const spin = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`;

export function Header({ onFilterClick, filterOpen }: HeaderProps) {
  const { mode, toggleColorMode } = useColorMode();
  const theme = useTheme();
  const { refresh, isLoading } = useGaugeDataContext();

  return (
    <AppBar
      position="sticky"
      elevation={1}
      sx={{
        top: 0,
        zIndex: theme.zIndex.appBar,
        background: waterGradients.night,
        borderBottom: `1px solid ${alpha(theme.palette.common.white, 0.1)}`,
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `url("data:image/svg+xml,%3Csvg width='100' height='20' viewBox='0 0 100 20' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0,10 Q25,0 50,10 T100,10 L100,20 L0,20 Z' fill='%23ffffff' opacity='0.05'/%3E%3C/svg%3E")`,
          backgroundSize: '100px 20px',
          animation: `${wave} 10s linear infinite`,
          pointerEvents: 'none',
        },
        '&::after': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `url("data:image/svg+xml,%3Csvg width='100' height='20' viewBox='0 0 100 20' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0,15 Q25,5 50,15 T100,15 L100,20 L0,20 Z' fill='%23ffffff' opacity='0.03'/%3E%3C/svg%3E")`,
          backgroundSize: '100px 20px',
          animation: `${wave} 15s linear infinite reverse`,
          pointerEvents: 'none',
        },
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 2,
          }}
        >
          <Box
            sx={{
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              position: 'relative',
              animation: `${float} 4s ease-in-out infinite`,
              '&:hover': {
                animation: 'none',
                transform: 'scale(1.1)',
                transition: 'transform 0.3s ease',
              },
            }}
          >
            <Kayaking sx={{ fontSize: 32 }} />
            <Waves 
              sx={{ 
                fontSize: 24, 
                position: 'absolute',
                bottom: -5,
                left: '50%',
                transform: 'translateX(-50%)',
                opacity: 0.5,
              }} 
            />
          </Box>
          <Typography
            variant="h6"
            sx={{
              color: 'white',
              letterSpacing: '0.2em',
              fontWeight: 300,
            }}
          >
            OZARK CREEK FLOW ZONE
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography
            sx={{
              color: 'rgba(255, 255, 255, 0.9)',
              letterSpacing: '0.1em',
              fontSize: { xs: '0.875rem', md: '1rem' },
              display: { xs: 'none', md: 'block' },
            }}
          >
            KNOW FLOWS. CHASE RAPIDS. LIVE LARGE.
          </Typography>

          <IconButton
            onClick={refresh}
            disabled={isLoading}
            sx={{
              color: 'white',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
              '&.Mui-disabled': {
                color: 'rgba(255, 255, 255, 0.5)',
              },
            }}
            aria-label="refresh data"
          >
            <Refresh sx={{ animation: isLoading ? `${spin} 1s linear infinite` : 'none' }} />
          </IconButton>

          <IconButton
            onClick={onFilterClick}
            sx={{
              color: 'white',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
              transform: filterOpen ? 'rotate(180deg)' : 'none',
              transition: 'transform 0.3s ease',
            }}
          >
            <FilterList />
          </IconButton>

          <IconButton
            onClick={toggleColorMode}
            sx={{
              color: 'white',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            {mode === 'dark' ? (
              <LightModeOutlined sx={{ fontSize: 20 }} />
            ) : (
              <DarkModeOutlined sx={{ fontSize: 20 }} />
            )}
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
