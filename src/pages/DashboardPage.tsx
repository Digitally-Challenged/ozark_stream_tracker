import React, { useState } from 'react';
import { Box, Container } from '@mui/material';
import { DashboardHeader } from '../components/dashboard/DashboardHeader';
import { StreamTable } from '../components/streams/StreamTable';
import { StreamDetail } from '../components/streams/StreamDetail';
import { streams } from '../data/streamData';
import { StreamData } from '../types/stream';

interface DashboardPageProps {
  selectedRatings: string[];
  selectedSizes: string[];
}

export function DashboardPage({
  selectedRatings,
  selectedSizes,
}: DashboardPageProps) {
  const [selectedStream, setSelectedStream] = useState<StreamData | null>(null);

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Container
        component="main"
        sx={{
          mt: 4,
          mb: 4,
          flex: 1,
          maxWidth: { xl: '1400px' },
        }}
      >
        <DashboardHeader />
        <StreamTable
          streams={streams}
          onStreamClick={(stream) => setSelectedStream(stream)}
          selectedRatings={selectedRatings}
          selectedSizes={selectedSizes}
        />
      </Container>
      <StreamDetail
        stream={selectedStream}
        open={selectedStream !== null}
        onClose={() => setSelectedStream(null)}
      />
    </Box>
  );
}
