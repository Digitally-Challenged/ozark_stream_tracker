// src/components/streams/StreamCardGrid.tsx
import { Grid } from '@mui/material';
import { StreamData } from '../../types/stream';
import { StreamCard } from './StreamCard';

interface StreamCardGridProps {
  streams: StreamData[];
  onStreamClick: (stream: StreamData) => void;
}

export function StreamCardGrid({ streams, onStreamClick }: StreamCardGridProps) {
  return (
    <Grid container spacing={2}>
      {streams.map((stream) => (
        <Grid item xs={12} sm={6} md={4} lg={3} key={`${stream.name}-${stream.gauge.id}`}>
          <StreamCard stream={stream} onClick={onStreamClick} />
        </Grid>
      ))}
    </Grid>
  );
}
