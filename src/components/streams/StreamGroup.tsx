// src/components/streams/StreamGroup.tsx
import { useState } from 'react';
import { Box, Collapse } from '@mui/material';
import { StreamData, LevelStatus } from '../../types/stream';
import { StreamGroupHeader } from './StreamGroupHeader';
import { StreamTable } from './StreamTable';
import { StreamCardGrid } from './StreamCardGrid';
import { ViewMode } from '../../hooks/useViewPreference';

interface StreamGroupProps {
  status: LevelStatus;
  streams: StreamData[];
  defaultExpanded?: boolean;
  onStreamClick: (stream: StreamData) => void;
  selectedRatings: string[];
  selectedSizes: string[];
  viewMode: ViewMode;
}

export function StreamGroup({
  status,
  streams,
  defaultExpanded = true,
  onStreamClick,
  selectedRatings,
  selectedSizes,
  viewMode,
}: StreamGroupProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  if (streams.length === 0) {
    return null;
  }

  return (
    <Box sx={{ mb: 3 }}>
      <StreamGroupHeader
        status={status}
        count={streams.length}
        expanded={expanded}
        onToggle={() => setExpanded(!expanded)}
      />
      <Collapse in={expanded}>
        {viewMode === 'cards' ? (
          <StreamCardGrid streams={streams} onStreamClick={onStreamClick} />
        ) : (
          <StreamTable
            streams={streams}
            onStreamClick={onStreamClick}
            selectedRatings={selectedRatings}
            selectedSizes={selectedSizes}
          />
        )}
      </Collapse>
    </Box>
  );
}
