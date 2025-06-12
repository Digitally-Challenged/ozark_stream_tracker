import React, { useState, useMemo, useCallback } from 'react';
import {
  Table,
  TableBody,
  TableContainer,
  Paper,
  Box,
  TextField,
  useTheme,
  InputAdornment,
} from '@mui/material';
import { Search } from '@mui/icons-material';
import { StreamData } from '../../types/stream';
import { StreamTableHeader } from './StreamTableHeader';
import { StreamTableRow } from './StreamTableRow';
import { SortDirection, SortField } from '../../types/table';
import { sortStreams } from '../../utils/sorting';

interface StreamTableProps {
  streams: StreamData[];
  onStreamClick: (stream: StreamData) => void;
  selectedRatings: string[];
  selectedSizes: string[];
}

export function StreamTable({
  streams,
  onStreamClick,
  selectedRatings,
  selectedSizes,
}: StreamTableProps) {
  const [sortField, setSortField] = useState<SortField>('name');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [searchTerm, setSearchTerm] = useState('');
  const theme = useTheme();

  // Memoize the sort handler to prevent unnecessary re-renders of child components
  const handleSort = useCallback((field: SortField) => {
    setSortDirection((prevDirection) => {
      const isAsc = sortField === field && prevDirection === 'asc';
      return isAsc ? 'desc' : 'asc';
    });
    setSortField(field);
  }, [sortField]);

  // Memoize filtered streams calculation
  const filteredStreams = useMemo(() => {
    return streams.filter((stream) => {
      if (
        selectedRatings.length > 0 &&
        !selectedRatings.includes(stream.rating)
      ) {
        return false;
      }

      if (selectedSizes.length > 0 && !selectedSizes.includes(stream.size)) {
        return false;
      }

      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        return (
          stream.name.toLowerCase().includes(searchLower) ||
          (stream.gauge?.name &&
            stream.gauge.name.toLowerCase().includes(searchLower))
        );
      }
      return true;
    });
  }, [streams, selectedRatings, selectedSizes, searchTerm]);

  // Memoize sorted streams calculation
  const sortedStreams = useMemo(() => {
    return sortStreams(filteredStreams, sortField, sortDirection);
  }, [filteredStreams, sortField, sortDirection]);

  // Memoize search handler
  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  }, []);

  // Memoize stream click handler to ensure referential stability
  const handleStreamClick = useCallback((stream: StreamData) => {
    onStreamClick(stream);
  }, [onStreamClick]);

  return (
    <Box sx={{ width: '100%' }}>
      <Paper elevation={0} sx={{ mb: 3, p: 2, backgroundColor: theme.palette.background.paper }}>
        <TextField
          placeholder="Search streams by name..."
          variant="outlined"
          size="small"
          fullWidth
          value={searchTerm}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search sx={{ color: 'text.secondary' }} />
              </InputAdornment>
            ),
          }}
          sx={{
            maxWidth: 400,
            '& .MuiOutlinedInput-root': {
              backgroundColor: theme.palette.background.default,
              '& fieldset': {
                borderColor: theme.palette.divider,
              },
              '&:hover fieldset': {
                borderColor: theme.palette.primary.main,
              },
            },
          }}
        />
      </Paper>
      <TableContainer
        component={Paper}
        elevation={0}
        sx={{
          backgroundColor: theme.palette.background.paper,
          '& .MuiTableCell-root': {
            py: 1.5,
            px: 2,
            fontSize: '0.875rem',
          },
          '& .MuiTableRow-root': {
            '&:hover': {
              backgroundColor: theme.palette.action.hover,
            },
          },
        }}
      >
        <Table size="small">
          <StreamTableHeader
            sortField={sortField}
            sortDirection={sortDirection}
            onSort={handleSort}
          />
          <TableBody>
            {sortedStreams.map((stream) => (
              <StreamTableRow
                key={`${stream.name}-${stream.gauge?.id || Math.random()}`}
                stream={stream}
                onClick={handleStreamClick}
              />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
