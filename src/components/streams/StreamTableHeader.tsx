import { memo } from 'react';
import { TableHead, TableRow, TableCell, TableSortLabel } from '@mui/material';
import { SortDirection, SortField } from '../../types/table';

interface StreamTableHeaderProps {
  sortField: SortField;
  sortDirection: SortDirection;
  onSort: (field: SortField) => void;
}

const StreamTableHeaderComponent = ({
  sortField,
  sortDirection,
  onSort,
}: StreamTableHeaderProps) => {
  const headers: { field: SortField; label: string }[] = [
    { field: 'name', label: 'Stream Name' },
    { field: 'rating', label: 'Rating' },
    { field: 'size', label: 'Size' },
    { field: 'gauge', label: 'Reference Gauge' },
    { field: 'reading', label: 'Gauge Reading' },
    { field: 'time', label: 'Time' },
    { field: 'quality', label: 'Quality' },
    { field: 'level', label: 'Current Level' },
    { field: 'trend', label: 'Trend' },
  ];

  return (
    <TableHead>
      <TableRow>
        {headers.map(({ field, label }) => (
          <TableCell key={field}>
            <TableSortLabel
              active={sortField === field}
              direction={sortField === field ? sortDirection : 'asc'}
              onClick={() => onSort(field)}
            >
              {label}
            </TableSortLabel>
          </TableCell>
        ))}
      </TableRow>
    </TableHead>
  );
};

// Memoize the component to prevent unnecessary re-renders
// Only re-render if sortField, sortDirection, or onSort changes
export const StreamTableHeader = memo(StreamTableHeaderComponent);
