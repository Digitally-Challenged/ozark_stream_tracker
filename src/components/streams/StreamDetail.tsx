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
import { WaterDropOutlined, ThermostatOutlined, AccessTimeOutlined, ShowChartOutlined } from '@mui/icons-material';
import { StreamData } from '../../types/stream';
import { format, isValid } from 'date-fns';

interface StreamDetailProps {
  stream: StreamData | null;
  open: boolean;
  onClose: () => void;
}

export function StreamDetail({ stream, open, onClose }: StreamDetailProps) {
  const theme = useTheme();
  
  if (!stream) return null;

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not available';
    const date = new Date(dateString);
    return isValid(date) ? format(date, 'PPpp') : 'Invalid date';
  };

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
        }
      }}
    >
      <DialogTitle sx={{ 
        borderBottom: `1px solid ${theme.palette.divider}`,
        color: theme.palette.text.primary,
      }}>
        {stream.name}
      </DialogTitle>
      
      <DialogContent sx={{ py: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <WaterDropOutlined sx={{ fontSize: 20, color: theme.palette.primary.main }} />
              <Typography color="text.primary">
                Flow Rate: {stream.currentFlow ? `${stream.currentFlow} cfs` : 'Not available'}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <ThermostatOutlined sx={{ fontSize: 20, color: theme.palette.primary.main }} />
              <Typography color="text.primary">
                Temperature: {stream.temperature ? `${stream.temperature}°F` : 'Not available'}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <ShowChartOutlined sx={{ fontSize: 20, color: theme.palette.primary.main }} />
              <Typography color="text.primary">
                Status: {stream.status || 'Not available'}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <AccessTimeOutlined sx={{ fontSize: 20, color: theme.palette.primary.main }} />
              <Typography color="text.primary">
                Last Updated: {formatDate(stream.lastUpdated)}
              </Typography>
            </Box>
          </Grid>

          {stream.waterQuality && (
            <Grid item xs={12}>
              <Typography 
                variant="h6" 
                gutterBottom 
                sx={{ 
                  color: theme.palette.text.primary,
                  fontWeight: 500,
                  mt: 2 
                }}
              >
                Water Quality
              </Typography>
              <Box sx={{ pl: 1 }}>
                <Typography color="text.primary" paragraph>
                  pH: {stream.waterQuality.ph || 'Not available'}
                </Typography>
                <Typography color="text.primary" paragraph>
                  Turbidity: {stream.waterQuality.turbidity ? `${stream.waterQuality.turbidity} NTU` : 'Not available'}
                </Typography>
                <Typography color="text.primary">
                  Dissolved Oxygen: {stream.waterQuality.dissolvedOxygen ? `${stream.waterQuality.dissolvedOxygen} mg/L` : 'Not available'}
                </Typography>
              </Box>
            </Grid>
          )}
        </Grid>
      </DialogContent>

      <DialogActions sx={{ 
        borderTop: `1px solid ${theme.palette.divider}`,
        px: 3,
        py: 2,
      }}>
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
    </Dialog>
  );
}