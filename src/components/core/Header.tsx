import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  useTheme,
  Box,
} from '@mui/material';
import {
  Kayaking,
  FilterList,
  DarkModeOutlined,
  LightModeOutlined,
} from '@mui/icons-material';
import { useTheme as useColorMode } from '../../context/ThemeContext';

interface HeaderProps {
  onFilterClick: () => void;
  filterOpen: boolean;
}

export function Header({ onFilterClick, filterOpen }: HeaderProps) {
  const { mode, toggleColorMode } = useColorMode();
  const theme = useTheme();

  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        backgroundColor: theme.palette.background.default,
        borderBottom: `1px solid ${theme.palette.divider}`,
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
            }}
          >
            <Kayaking sx={{ fontSize: 32 }} />
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
