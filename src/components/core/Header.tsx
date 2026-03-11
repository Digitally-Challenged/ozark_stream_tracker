import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  useTheme,
  Box,
  keyframes,
  alpha,
  ButtonBase,
} from '@mui/material';
import {
  Kayaking,
  DarkModeOutlined,
  LightModeOutlined,
  Waves,
  Refresh,
  Cloud,
  Dashboard,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useColorMode } from '../../context/ThemeContext';
import { useGaugeDataContext } from '../../context/GaugeDataContext';
import { waterGradients } from '../../theme/waterTheme';

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

export function Header() {
  const { mode, toggleColorMode } = useColorMode();
  const theme = useTheme();
  const { refresh, isLoading } = useGaugeDataContext();
  const navigate = useNavigate();
  const location = useLocation();
  const onPrecipMap = location.pathname === '/precipitation';

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
      <Toolbar
        sx={{
          justifyContent: 'space-between',
          gap: { xs: 1, sm: 2 },
          px: { xs: 1, sm: 2 },
        }}
      >
        {/* Logo + App Name */}
        <ButtonBase
          onClick={() => navigate('/dashboard')}
          disableRipple
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1.5,
            borderRadius: 1,
            px: 1,
            py: 0.5,
            flexShrink: 0,
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.06)',
            },
          }}
        >
          <Box
            sx={{
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              position: 'relative',
              animation: `${float} 4s ease-in-out infinite`,
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
              letterSpacing: '0.15em',
              fontWeight: 300,
              display: { xs: 'none', sm: 'block' },
              whiteSpace: 'nowrap',
            }}
          >
            OZARK CREEK FLOW ZONE
          </Typography>
        </ButtonBase>

        {/* Center: Tagline */}
        <Box
          sx={{
            display: { xs: 'none', md: 'flex' },
            alignItems: 'center',
          }}
        >
          <Typography
            sx={{
              color: 'rgba(255, 255, 255, 0.9)',
              letterSpacing: '0.1em',
              fontSize: '1rem',
            }}
          >
            KNOW FLOWS. CHASE RAPIDS. LIVE LARGE.
          </Typography>
        </Box>

        {/* Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          {/* Nav Icons */}
          <Box
            sx={{
              display: 'flex',
              gap: 0.25,
              backgroundColor: 'rgba(255, 255, 255, 0.06)',
              borderRadius: 2,
              p: 0.375,
              border: '1px solid rgba(255, 255, 255, 0.08)',
              mr: 0.5,
            }}
          >
            <IconButton
              onClick={() => navigate('/dashboard')}
              aria-label="dashboard"
              size="small"
              sx={{
                color: !onPrecipMap ? 'white' : 'rgba(255, 255, 255, 0.45)',
                backgroundColor: !onPrecipMap
                  ? 'rgba(255, 255, 255, 0.12)'
                  : 'transparent',
                borderRadius: 1.5,
                transition: 'all 0.25s ease',
                ...(!onPrecipMap && {
                  boxShadow: '0 0 10px rgba(48, 207, 208, 0.2)',
                }),
                '&:hover': {
                  color: 'white',
                  backgroundColor: !onPrecipMap
                    ? 'rgba(255, 255, 255, 0.15)'
                    : 'rgba(255, 255, 255, 0.08)',
                },
              }}
            >
              <Dashboard sx={{ fontSize: 20 }} />
            </IconButton>
            <IconButton
              onClick={() => navigate('/precipitation')}
              aria-label="precipitation map"
              size="small"
              sx={{
                color: onPrecipMap ? 'white' : 'rgba(255, 255, 255, 0.45)',
                backgroundColor: onPrecipMap
                  ? 'rgba(255, 255, 255, 0.12)'
                  : 'transparent',
                borderRadius: 1.5,
                transition: 'all 0.25s ease',
                ...(onPrecipMap && {
                  boxShadow: '0 0 10px rgba(48, 207, 208, 0.2)',
                }),
                '&:hover': {
                  color: 'white',
                  backgroundColor: onPrecipMap
                    ? 'rgba(255, 255, 255, 0.15)'
                    : 'rgba(255, 255, 255, 0.08)',
                },
              }}
            >
              <Cloud sx={{ fontSize: 20 }} />
            </IconButton>
          </Box>

          <IconButton
            onClick={refresh}
            disabled={isLoading}
            aria-label="refresh data"
            sx={{
              color: 'white',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
              '&.Mui-disabled': {
                color: 'rgba(255, 255, 255, 0.5)',
              },
            }}
          >
            <Refresh
              sx={{
                fontSize: 20,
                animation: isLoading ? `${spin} 1s linear infinite` : 'none',
              }}
            />
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
