import { StreamData, LevelTrend } from '../types/stream';
import { SortDirection, SortField } from '../types/table';

// Helper function to get trend priority (Rising > Holding > Falling > None)
const getTrendPriority = (trend: LevelTrend | undefined): number => {
  switch (trend) {
    case LevelTrend.Rising:
      return 3;
    case LevelTrend.Holding:
      return 2;
    case LevelTrend.Falling:
      return 1;
    default:
      return 0;
  }
};

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
      case 'trend': {
        const trendA = getTrendPriority(a.currentLevel?.trend);
        const trendB = getTrendPriority(b.currentLevel?.trend);
        comparison = trendB - trendA; // Higher priority first
        break;
      }
      case 'level':
        if (a.currentLevel?.status && b.currentLevel?.status) {
          comparison = a.currentLevel.status.localeCompare(
            b.currentLevel.status
          );
        }
        break;
      case 'reading': {
        // Use gauge reading value instead of non-existent currentFlow
        const readingA = a.currentLevel?.reading?.value ?? -Infinity;
        const readingB = b.currentLevel?.reading?.value ?? -Infinity;
        comparison = readingA - readingB;
        break;
      }
      case 'time': {
        // Sort by timestamp of gauge readings
        const timeA = a.currentLevel?.reading?.timestamp
          ? new Date(a.currentLevel.reading.timestamp).getTime()
          : -Infinity;
        const timeB = b.currentLevel?.reading?.timestamp
          ? new Date(b.currentLevel.reading.timestamp).getTime()
          : -Infinity;
        comparison = timeB - timeA; // Most recent first
        break;
      }
      default:
        comparison = 0;
    }

    return sortDirection === 'asc' ? comparison : -comparison;
  });
}
