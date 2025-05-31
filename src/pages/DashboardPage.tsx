// src/pages/DashboardPage.tsx
import React, { useState } from 'react';
import { Box, Container } from '@mui/material';
import { DashboardHeader } from '../components/dashboard/DashboardHeader';
import { StreamTable } from '../components/streams/StreamTable';
import { StreamDetail } from '../components/streams/StreamDetail';
import { streams } from '../data/streamData';
import { StreamData } from '../types/stream';

interface DashboardPageProps {
  // Added
  selectedRatings: string[]; // Added
  selectedSizes: string[]; // Added
}

export function DashboardPage({
  selectedRatings,
  selectedSizes,
}: DashboardPageProps) {
  // Modified
  const [selectedStream, setSelectedStream] = useState<StreamData | null>(null);

  // TODO in a later step: Pass selectedRatings and selectedSizes to StreamTable
  console.log('Filters received in DashboardPage:', {
    selectedRatings,
    selectedSizes,
  });

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
          selectedRatings={selectedRatings} // Added
          selectedSizes={selectedSizes} // Added
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
