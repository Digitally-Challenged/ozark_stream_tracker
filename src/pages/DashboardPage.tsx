import { useState, useMemo, useCallback } from 'react';
import {
  Box,
  Container,
  CircularProgress,
  Alert,
  Typography,
  IconButton,
  Badge,
} from '@mui/material';
import { FilterList } from '@mui/icons-material';
import { DashboardHeader } from '../components/dashboard/DashboardHeader';
import { DashboardSidebar } from '../components/dashboard/DashboardSidebar';
import { StreamGroup } from '../components/streams/StreamGroup';
import { StreamDetail } from '../components/streams/StreamDetail';
import { ViewToggle } from '../components/streams/ViewToggle';
import { streams } from '../data/streamData';
import { StreamData, LevelStatus } from '../types/stream';
import { useAllStreamStatuses } from '../hooks/useStreamStatus';
import { useViewPreference } from '../hooks/useViewPreference';
import { useGaugeDataContext } from '../context/GaugeDataContext';
import { groupStreamsByStatus, GROUP_ORDER } from '../utils/streamGrouping';
import { filterByRatingAndSize } from '../utils/filterStreams';

export function DashboardPage() {
  const [selectedStream, setSelectedStream] = useState<StreamData | null>(null);
  const [filterOpen, setFilterOpen] = useState(false);
  const [selectedRatings, setSelectedRatings] = useState<string[]>([]);
  const [selectedSizes, setSelectedSizes] = useState<string[]>([]);
  const handleStreamClick = useCallback((stream: StreamData) => {
    setSelectedStream(stream);
  }, []);
  const handleCloseDetail = useCallback(() => {
    setSelectedStream(null);
  }, []);
  const streamStatuses = useAllStreamStatuses(streams);
  const { viewMode, setViewMode } = useViewPreference();
  const { isLoading, error: gaugeError } = useGaugeDataContext();
  const activeFilterCount = selectedRatings.length + selectedSizes.length;

  const filteredStreams = useMemo(() => {
    return filterByRatingAndSize(streams, selectedRatings, selectedSizes);
  }, [selectedRatings, selectedSizes]);

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
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 2,
          }}
        >
          <Badge badgeContent={activeFilterCount} color="primary">
            <IconButton
              onClick={() => setFilterOpen(!filterOpen)}
              size="small"
              sx={{
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1.5,
                transform: filterOpen ? 'rotate(180deg)' : 'none',
                transition: 'transform 0.3s ease',
              }}
            >
              <FilterList sx={{ fontSize: 20 }} />
            </IconButton>
          </Badge>
          <ViewToggle viewMode={viewMode} onChange={setViewMode} />
        </Box>

        {isLoading && (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              py: 4,
            }}
          >
            <CircularProgress size={24} sx={{ mr: 2 }} />
            <Typography>Loading gauge data...</Typography>
          </Box>
        )}

        {gaugeError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            Failed to load gauge data. Some streams may be unavailable.
          </Alert>
        )}

        {GROUP_ORDER.map((status) => (
          <StreamGroup
            key={status}
            status={status}
            streams={groupedStreams[status]}
            defaultExpanded={status !== LevelStatus.TooLow}
            onStreamClick={handleStreamClick}
            selectedRatings={selectedRatings}
            selectedSizes={selectedSizes}
            viewMode={viewMode}
          />
        ))}
      </Container>
      <StreamDetail
        stream={selectedStream}
        open={selectedStream !== null}
        onClose={handleCloseDetail}
      />
      <DashboardSidebar
        open={filterOpen}
        onClose={() => setFilterOpen(false)}
        selectedRatings={selectedRatings}
        setSelectedRatings={setSelectedRatings}
        selectedSizes={selectedSizes}
        setSelectedSizes={setSelectedSizes}
      />
    </Box>
  );
}
