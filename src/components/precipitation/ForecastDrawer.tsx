// src/components/precipitation/ForecastDrawer.tsx
import {
  SwipeableDrawer,
  Box,
  Typography,
  IconButton,
  useTheme,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import { Close, Cloud } from '@mui/icons-material';
import { ForecastPanel } from './ForecastPanel';
import { glassmorphism } from '../../theme/waterTheme';

interface ForecastDrawerProps {
  open: boolean;
  onOpen: () => void;
  onClose: () => void;
}

export function ForecastDrawer({ open, onOpen, onClose }: ForecastDrawerProps) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  return (
    <SwipeableDrawer
      anchor="bottom"
      open={open}
      onOpen={onOpen}
      onClose={onClose}
      swipeAreaWidth={56}
      disableSwipeToOpen={false}
      ModalProps={{ keepMounted: true }}
      PaperProps={{
        sx: {
          height: '70vh',
          borderTopLeftRadius: 16,
          borderTopRightRadius: 16,
          overflow: 'hidden',
          ...(isDark ? glassmorphism.dark : glassmorphism.light),
        },
      }}
    >
      {/* Drag handle */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          py: 1,
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.3)}`,
        }}
      >
        <Box
          sx={{
            width: 40,
            height: 4,
            borderRadius: 2,
            bgcolor: alpha(theme.palette.text.secondary, 0.3),
          }}
        />
      </Box>

      {/* Header with close */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          px: 2,
          py: 1,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Cloud sx={{ fontSize: 18, color: '#30cfd0' }} />
          <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
            Forecast & Precipitation
          </Typography>
        </Box>
        <IconButton onClick={onClose} size="small">
          <Close sx={{ fontSize: 18 }} />
        </IconButton>
      </Box>

      {/* Panel content */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <ForecastPanel />
      </Box>
    </SwipeableDrawer>
  );
}
