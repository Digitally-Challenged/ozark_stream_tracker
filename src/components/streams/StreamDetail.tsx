import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Grid,
  Box,
} from '@mui/material';
import { Droplet, Thermometer, Clock, Activity } from 'lucide-react';
import { StreamData } from '../../types/stream';
import { format, isValid } from 'date-fns';

interface StreamDetailProps {
  stream: StreamData | null;
  open: boolean;
  onClose: () => void;
}

export function StreamDetail({ stream, open, onClose }: StreamDetailProps) {
  if (!stream) return null;

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not available';
    const date = new Date(dateString);
    return isValid(date) ? format(date, 'PPpp') : 'Invalid date';
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>{stream.name}</DialogTitle>
      <DialogContent>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <Droplet />
              <Typography>
                Flow Rate: {stream.currentFlow ? `${stream.currentFlow} cfs` : 'Not available'}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <Thermometer />
              <Typography>
                Temperature: {stream.temperature ? `${stream.temperature}°F` : 'Not available'}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <Activity />
              <Typography>Status: {stream.status || 'Not available'}</Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Box display="flex" alignItems="center" gap={1}>
              <Clock />
              <Typography>
                Last Updated: {formatDate(stream.lastUpdated)}
              </Typography>
            </Box>
          </Grid>
          {stream.waterQuality && (
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>Water Quality</Typography>
              <Typography>pH: {stream.waterQuality.ph || 'Not available'}</Typography>
              <Typography>
                Turbidity: {stream.waterQuality.turbidity ? `${stream.waterQuality.turbidity} NTU` : 'Not available'}
              </Typography>
              <Typography>
                Dissolved Oxygen: {stream.waterQuality.dissolvedOxygen ? `${stream.waterQuality.dissolvedOxygen} mg/L` : 'Not available'}
              </Typography>
            </Grid>
          )}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
}