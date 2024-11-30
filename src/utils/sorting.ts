import { StreamData } from '../types/stream';
import { SortDirection, SortField } from '../types/table';

export function sortStreams(
  streams: StreamData[], 
  sortField: SortField, 
  sortDirection: SortDirection
): StreamData[] {
  return [...streams].sort((a, b) => {
    let comparison = 0;

    switch (sortField) {
      case 'name':
        comparison = a.name.localeCompare(b.name);
        break;
      case 'rating':
        comparison = a.rating.localeCompare(b.rating);
        break;
      case 'size':
        comparison = a.size.localeCompare(b.size);
        break;
      case 'gauge':
        comparison = a.gauge.name.localeCompare(b.gauge.name);
        break;
      case 'quality':
        comparison = a.quality.localeCompare(b.quality);
        break;
      // Note: level and reading sorting will be handled by the actual values
      // from useStreamGauge in a future update
      default:
        comparison = 0;
    }

    return sortDirection === 'asc' ? comparison : -comparison;
  });
}