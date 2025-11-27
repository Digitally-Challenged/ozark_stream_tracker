import { useState, useMemo } from 'react';
import { Box, Container } from '@mui/material';
import { DashboardHeader } from '../components/dashboard/DashboardHeader';
import { StreamGroup } from '../components/streams/StreamGroup';
import { StreamDetail } from '../components/streams/StreamDetail';
import { ViewToggle } from '../components/streams/ViewToggle';
import { streams } from '../data/streamData';
import { StreamData, LevelStatus } from '../types/stream';
import { useAllStreamStatuses } from '../hooks/useStreamStatus';
import { useViewPreference } from '../hooks/useViewPreference';
import { groupStreamsByStatus, GROUP_ORDER } from '../utils/streamGrouping';

interface DashboardPageProps {
  selectedRatings: string[];
  selectedSizes: string[];
}

export function DashboardPage({
  selectedRatings,
  selectedSizes,
}: DashboardPageProps) {
  const [selectedStream, setSelectedStream] = useState<StreamData | null>(null);
  const streamStatuses = useAllStreamStatuses(streams);
  const { viewMode, setViewMode } = useViewPreference();

  // Filter streams first
  const filteredStreams = useMemo(() => {
    return streams.filter((stream) => {
      if (selectedRatings.length > 0 && !selectedRatings.includes(stream.rating)) {
        return false;
      }
      if (selectedSizes.length > 0 && !selectedSizes.includes(stream.size)) {
        return false;
      }
      return true;
    });
  }, [selectedRatings, selectedSizes]);

  // Group filtered streams by status
  const groupedStreams = useMemo(() => {
    return groupStreamsByStatus(filteredStreams, (stream) =>
      streamStatuses.get(stream.name)
    );
  }, [filteredStreams, streamStatuses]);

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
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
          <ViewToggle viewMode={viewMode} onChange={setViewMode} />
        </Box>
        {GROUP_ORDER.map((status) => (
          <StreamGroup
            key={status}
            status={status}
            streams={groupedStreams[status]}
            defaultExpanded={status !== LevelStatus.TooLow}
            onStreamClick={(stream) => setSelectedStream(stream)}
            selectedRatings={selectedRatings}
            selectedSizes={selectedSizes}
            viewMode={viewMode}
          />
        ))}
      </Container>
      <StreamDetail
        stream={selectedStream}
        open={selectedStream !== null}
        onClose={() => setSelectedStream(null)}
      />
    </Box>
  );
}
