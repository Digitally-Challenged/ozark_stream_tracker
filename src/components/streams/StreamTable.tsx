import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableContainer,
  Paper,
  Box,
  TextField,
  InputAdornment,
} from '@mui/material';
import { Search } from 'lucide-react';
import { StreamData } from '../../types/stream';
import { StreamTableHeader } from './StreamTableHeader';
import { StreamTableRow } from './StreamTableRow';
import { SortDirection, SortField } from '../../types/table';
import { sortStreams } from '../../utils/sorting';

interface StreamTableProps {
  streams: StreamData[];
  onStreamClick: (stream: StreamData) => void;
}

export function StreamTable({ streams, onStreamClick }: StreamTableProps) {
  const [sortField, setSortField] = useState<SortField>('name');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [searchTerm, setSearchTerm] = useState('');

  const handleSort = (field: SortField) => {
    const isAsc = sortField === field && sortDirection === 'asc';
    setSortDirection(isAsc ? 'desc' : 'asc');
    setSortField(field);
  };

  const filteredStreams = streams.filter((stream) => {
    const matchesSearch = stream.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      stream.gauge.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  const sortedStreams = sortStreams(filteredStreams, sortField, sortDirection);

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search streams..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search size={20} />
              </InputAdornment>
            ),
          }}
        />
      </Box>
      <TableContainer 
        component={Paper} 
        sx={{ 
          maxHeight: 'calc(100vh - 400px)',
          overflow: 'auto',
          '&::-webkit-scrollbar': {
            width: 8,
            height: 8,
          },
          '&::-webkit-scrollbar-track': {
            backgroundColor: 'rgba(0, 0, 0, 0.05)',
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: 'rgba(0, 0, 0, 0.2)',
            borderRadius: 4,
          },
        }}
      >
        <Table stickyHeader>
          <StreamTableHeader
            sortField={sortField}
            sortDirection={sortDirection}
            onSort={handleSort}
          />
          <TableBody>
            {sortedStreams.map((stream) => (
              <StreamTableRow
                key={`${stream.name}-${stream.gauge.id}`}
                stream={stream}
                onClick={onStreamClick}
              />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}