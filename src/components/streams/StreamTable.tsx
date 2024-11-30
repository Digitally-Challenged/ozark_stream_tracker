import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableContainer,
  Paper,
  Box,
  TextField,
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
    const searchLower = searchTerm.toLowerCase();
    return stream.name.toLowerCase().includes(searchLower) ||
           stream.gauge.name.toLowerCase().includes(searchLower);
  });

  const sortedStreams = sortStreams(filteredStreams, sortField, sortDirection);

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center',
        mb: 2,
        maxWidth: 400,
        position: 'relative'
      }}>
        <Search sx={{ 
          position: 'absolute',
          left: 8,
          color: 'text.secondary'
        }} />
        <TextField
          placeholder="Search streams..."
          variant="outlined"
          size="small"
          fullWidth
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          sx={{
            '& .MuiOutlinedInput-root': {
              pl: 4.5,
              '& fieldset': {
                borderColor: 'divider',
              },
            },
          }}
        />
      </Box>
      <TableContainer 
        component={Paper} 
        elevation={0}
        sx={{ 
          bgcolor: 'background.paper',
          '& .MuiTableCell-root': {
            py: 1.5,
            px: 2,
            fontSize: '0.875rem',
          }
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