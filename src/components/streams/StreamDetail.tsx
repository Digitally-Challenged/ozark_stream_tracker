import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Grid,
  Box,
  useTheme,
} from '@mui/material';
import {
  WaterDropOutlined,
  ThermostatOutlined,
  AccessTimeOutlined,
  ShowChartOutlined,
  TrendingUp,
  TrendingDown,
  HorizontalRule,
} from '@mui/icons-material';
import { StreamData, LevelTrend } from '../../types/stream';
import { format, isValid } from 'date-fns';
import { useGaugeReading } from '../../hooks/useGaugeReading';
import { useRelativeTime } from '../../hooks/useRelativeTime';

interface StreamDetailProps {
  stream: StreamData | null;
  open: boolean;
  onClose: () => void;
}

// Internal component that safely uses hooks
function StreamDetailContent({
  stream,
  onClose,
}: {
  stream: StreamData;
  onClose: () => void;
}) {
  const theme = useTheme();
  const { reading, currentLevel } = useGaugeReading(stream.gauge.id, stream.targetLevels);
  const relativeTime = useRelativeTime(reading?.timestamp);

  const getTrendInfo = () => {
    if (!currentLevel?.trend || currentLevel.trend === LevelTrend.None) {
      return null;
    }
    switch (currentLevel.trend) {
      case LevelTrend.Rising:
        return { icon: TrendingUp, label: 'Rising', color: theme.palette.success.main };
      case LevelTrend.Falling:
        return { icon: TrendingDown, label: 'Falling', color: theme.palette.error.main };
      case LevelTrend.Holding:
        return { icon: HorizontalRule, label: 'Stable', color: theme.palette.warning.main };
      default:
        return null;
    }
  };

  const trendInfo = getTrendInfo();

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not available';
    const date = new Date(dateString);
    return isValid(date) ? format(date, 'PPpp') : 'Invalid date';
  };

  return (
    <>
      <DialogTitle
        sx={{
          borderBottom: `1px solid ${theme.palette.divider}`,
          color: theme.palette.text.primary,
        }}
      >
        {stream.name}
      </DialogTitle>

      <DialogContent sx={{ py: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <WaterDropOutlined
                sx={{ fontSize: 20, color: theme.palette.primary.main }}
              />
              <Typography color="text.primary">
                Current Reading:{' '}
                {reading?.value
                  ? `${reading.value.toFixed(2)} ft`
                  : 'Not available'}
                {trendInfo && (
                  <Box component="span" sx={{ ml: 1, display: 'inline-flex', alignItems: 'center', gap: 0.5 }}>
                    <trendInfo.icon sx={{ fontSize: 18, color: trendInfo.color }} />
                    <Typography component="span" variant="body2" sx={{ color: trendInfo.color, fontWeight: 'bold' }}>
                      {trendInfo.label}
                    </Typography>
                  </Box>
                )}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <ThermostatOutlined
                sx={{ fontSize: 20, color: theme.palette.primary.main }}
              />
              <Typography color="text.primary">
                Target Range: {stream.targetLevels.tooLow}ft -{' '}
                {stream.targetLevels.high}ft
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <ShowChartOutlined
                sx={{ fontSize: 20, color: theme.palette.primary.main }}
              />
              <Typography color="text.primary">
                Quality Rating: {stream.quality}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <AccessTimeOutlined
                sx={{ fontSize: 20, color: theme.palette.primary.main }}
              />
              <Typography color="text.primary">
                Last Updated:{' '}
                {reading?.timestamp ? (
                  <>
                    {formatDate(reading.timestamp)}
                    {relativeTime && (
                      <Typography
                        component="span"
                        variant="body2"
                        sx={{ ml: 1, opacity: 0.7 }}
                      >
                        ({relativeTime})
                      </Typography>
                    )}
                  </>
                ) : (
                  'Not available'
                )}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions
        sx={{
          borderTop: `1px solid ${theme.palette.divider}`,
          px: 3,
          py: 2,
        }}
      >
        <Button
          onClick={onClose}
          variant="contained"
          sx={{
            bgcolor: theme.palette.primary.main,
            '&:hover': {
              bgcolor: theme.palette.primary.dark,
            },
          }}
        >
          Close
        </Button>
      </DialogActions>
    </>
  );
}

// Main component that handles null checks
export function StreamDetail({ stream, open, onClose }: StreamDetailProps) {
  const theme = useTheme();

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          bgcolor: theme.palette.background.paper,
          backgroundImage: 'none',
        },
      }}
    >
      {stream && <StreamDetailContent stream={stream} onClose={onClose} />}
    </Dialog>
  );
}
